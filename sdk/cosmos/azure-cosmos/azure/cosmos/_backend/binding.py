# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Sync backend that sends operations to the rust driver through the compiled binding.

Terms, consistent across the backend layer: the **binding** is the compiled
``azure.cosmos._rust`` extension Python calls into; the **rust driver** is the
driver the binding builds (it owns the connection pool, request signing, and
region routing); the **driver handle** is the string ``acquire_driver_handle`` returns -- a
key made from ``(endpoint, credential, config)`` that names *which* rust driver a
client uses. The compiled ``_rust`` file contains both the binding and the rust
driver code.

This module and its async counterpart load ``azure.cosmos._rust`` for dispatch.
The import is guarded so the Python package can load without a built extension.
Missing-extension errors are raised by the selected operation's lookup/preflight;
legacy migration routing, where allowed, is decided separately.
"""
from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Any, Iterator, Optional

from azure.core.exceptions import ServiceResponseError
from .._operation_deadline import remaining_timeout
from ..exceptions import CosmosClientTimeoutError

from .cosmos_backend import CosmosBackend
from .operations import (
    OP_TO_BINDING_METHOD,
    get_page_binding_method,
)
from .errors import BindingProtocolError, PagePreflightError
from .contracts import BackendResponse, ContainerMetadata, PreparedClientConfig, PreparedQuery, PreparedRequest, QueryPage
from ._binding_conversions import (
    build_backend_response, build_binding_request_from_page,
    build_container_metadata, metadata_exception_from_binding,
    build_query_page, page_dispatch_arguments,
)
from ._shared import (
    RustBindingShared,
    _binding_error_type,
    driver_transport_error_type,
    driver_unsupported_query_error_type,
    finalize_backend_resources,
    page_dispatch_errors,
    validate_page_request,
)
from .constants import BACKEND_NAME_RUST
from .request_settings import native_settings_contract_error

if TYPE_CHECKING:
    from azure.cosmos._rust import _ItemFeedCursor

_LOGGER = logging.getLogger(__name__)

# Imported once when this module loads; not changed afterwards.
_rust_module: Optional[Any] = None
try:
    from azure.cosmos import _rust  # type: ignore[attr-defined]
    _rust_module = _rust
except ImportError:
    _LOGGER.debug(
        "_rust module not available; RustBinding operations "
        "will raise NotImplementedError until the Rust module is built."
    )

# The binding's error for a failure that produced no HTTP response, captured
# once at load. A driver operation that fails before any reply comes back
# raises this; we re-raise it as azure-core's ServiceResponseError (see
# driver_transport_error_type).
_DRIVER_TRANSPORT_ERROR = driver_transport_error_type(_rust_module)
_DRIVER_RESPONSE_ERROR = _binding_error_type(_rust_module, "_DriverResponseError")
_UNSUPPORTED_QUERY_ERROR = driver_unsupported_query_error_type(_rust_module)
_REQUEST_CONTRACT_ERROR = native_settings_contract_error(_rust_module) if _rust_module is not None else None


# Look up the binding's function for an operation. Read live from ``_rust_module``
# rather than cached at import, so the tests can swap in a fake binding; the extra
# getattr per call is tiny next to the network round trip.
def _get_binding_function(op: str) -> Optional[Any]:
    """Return the binding's ``<op>`` function, or ``None`` if the op is unsupported
    or the compiled module is absent."""
    method = OP_TO_BINDING_METHOD.get(op)
    if method is None or _rust_module is None:
        return None
    return getattr(_rust_module, method, None)


def _get_page_dispatch(method: Optional[str]) -> Optional[Any]:
    """Look up the selected page binding without changing its execution mode."""
    if method is None or _rust_module is None:
        return None
    return getattr(_rust_module, method, None)


class RustBinding(RustBindingShared, CosmosBackend):
    """Sends operations from one ``CosmosClient`` to a shared rust driver.

    The **driver handle** ``acquire_driver_handle`` returns is built on the first operation
    and reused; every operation passes it back. The handle is not the
    ``CosmosClient`` and not the rust driver itself -- it is the driver's key,
    made from ``(endpoint, credential, config)``. The binding keeps one rust driver
    per distinct ``(endpoint, credential, config)`` and reference-counts it, so
    several clients with the same settings share a single rust driver; ``close``
    drops this client's reference. Active operations can keep the driver alive
    after the last client closes.
    Missing compiled exports fail at lookup or preflight. Page paths use
    ``PagePreflightError`` rather than ``NotImplementedError``.

    :class:`~azure.cosmos._backend._shared.RustBindingShared` stores common client
    state and registrations. This class builds the driver, sends synchronous
    operations, and releases this client's resources.
    """

    name = BACKEND_NAME_RUST

    def __init__(
        self,
        endpoint: str,
        master_key: Optional[str] = None,
        client_config: Optional[PreparedClientConfig] = None,
        token_credential: Optional[Any] = None,
    ) -> None:
        """Store client settings and check initialized runtime configuration."""
        self._init_shared(
            endpoint, master_key, client_config, token_credential
        )

    def _ensure_driver_handle(self) -> str:
        """Return this client's driver handle, building it once on first use.

        On the first operation the binding's ``acquire_driver_handle`` either builds a new
        rust driver for this ``(endpoint, credential, config)`` or, if one already
        exists, bumps its reference count and returns the same handle. Without this,
        each operation would acquire another native reference. The double-check
        under the lock shares a successfully stored handle; an acquisition
        that raises can be attempted again by a later call. The slow path
        rejects a closed client but does not drain operations racing with close.
        """
        # If the handle is already built, return it without locking.
        if _REQUEST_CONTRACT_ERROR is not None:
            raise RuntimeError(_REQUEST_CONTRACT_ERROR)
        driver_handle = self._driver_handle
        if driver_handle is not None:
            return driver_handle
        if _rust_module is None:
            raise NotImplementedError(
                "RustBinding: the compiled azure.cosmos._rust "
                "module is not present in this environment. Build it with "
                "`maturin develop` from the repo root."
            )
        # Build it once. The lock, with a second check inside, keeps
        # concurrent first callers from each building one.
        with self._driver_handle_lock:
            # close() clears the handle, so without this check a closed client would
            # look exactly like a brand-new one and silently open a second driver
            # reference -- an operation on a closed client would appear to succeed.
            # The async backend refuses the same way.
            if self._closing:
                raise RuntimeError("RustBinding: the client is closed.")
            if self._driver_handle is None:
                self._driver_handle = self._initialize_driver(_rust_module)
            return self._driver_handle

    def close(self) -> None:
        """Release this client's credential-bridge hold and Rust driver reference.

        Mark the client closed and take its handle once, so repeated calls cannot
        release another client's reference. Other clients and operations can keep
        the driver alive. The customer's own credential is not closed.
        """
        with self._driver_handle_lock:
            self._closing = True
            driver_handle = self._driver_handle
            self._driver_handle = None
        self._close_token_credential_bridge()
        if driver_handle is None or _rust_module is None:
            return
        release_driver_handle = getattr(_rust_module, "release_driver_handle", None)
        if release_driver_handle is None:
            return
        try:
            release_driver_handle(driver_handle)
        except Exception:  # pylint: disable=broad-except
            # The exception can also contain the handle; do not log its text or traceback.
            _LOGGER.debug("RustBinding.close failed while releasing native resources")

    def __del__(self) -> None:
        """Release resources if the client was not closed explicitly."""
        try:
            with self._driver_handle_lock:
                self._closing = True
                driver_handle, self._driver_handle = self._driver_handle, None
            credential = self._take_token_credential_for_close()
            finalize_backend_resources(credential, driver_handle, _rust_module)
        except Exception:  # pylint: disable=broad-except
            # Never raise from object finalization.
            pass

    def execute(
        self, prepared: PreparedRequest, *, deadline: Optional[float] = None
    ) -> BackendResponse:
        """Send one prepared single-response operation."""
        if not isinstance(prepared, PreparedRequest):
            raise TypeError("execute requires a PreparedRequest")
        if _rust_module is None:
            raise NotImplementedError(
                "RustBinding.execute: the compiled "
                "azure.cosmos._rust module is not present in "
                "this environment. Build it with `maturin develop` from "
                "the repo root."
            )

        # Look up the binding's function for this op; None if unsupported.
        binding_function = _get_binding_function(prepared.op)
        if binding_function is None:
            raise NotImplementedError(
                "RustBinding.execute does not yet support op={!r}.".format(prepared.op)
            )
        driver_handle = self._ensure_driver_handle()
        # Record the selected dispatch before calling it; this is not proof of
        # native execution or service I/O. Omit the credential-bearing handle.
        _LOGGER.debug(
            "cosmos backend=%s op=%s dispatch=%s",
            BACKEND_NAME_RUST,
            prepared.op,
            OP_TO_BINDING_METHOD.get(prepared.op),
        )
        # Translate the binding's response-less error to ServiceResponseError.
        # No returned response does not prove that nothing was sent or applied.
        # This translation does not invoke legacy transport retry policies.
        try:
            raw_response = (
                binding_function(driver_handle, prepared)
                if deadline is None
                else binding_function(driver_handle, prepared, timeout_seconds=remaining_timeout(deadline))
            )
        except TimeoutError as exc:
            if deadline is None:
                raise
            raise CosmosClientTimeoutError(error=exc) from exc
        except _DRIVER_TRANSPORT_ERROR as exc:
            raise ServiceResponseError(message=str(exc)) from exc
        except _DRIVER_RESPONSE_ERROR as exc:
            raise metadata_exception_from_binding(exc) from exc
        if raw_response is None:
            raise BindingProtocolError(f"The binding returned no response for {prepared.op!r}")
        return build_backend_response(*raw_response)

    def _debug_fault_injection_rule_hit_count(self, rule_id: str) -> int:
        """Return how many Rust transport attempts applied one configured rule."""
        if _rust_module is None:
            raise NotImplementedError(
                "Rust fault injection requires the compiled azure.cosmos._rust module."
            )
        return int(
            _rust_module._debug_fault_injection_rule_hit_count(
                self._ensure_driver_handle(),
                rule_id,
            )
        )

    def get_container_metadata(
        self, container_link: str, *, deadline: Optional[float] = None
    ) -> ContainerMetadata:
        """Get routing facts from the driver's cache, fetching on a miss."""
        if _rust_module is None:
            raise NotImplementedError(
                "RustBinding.get_container_metadata: the compiled "
                "azure.cosmos._rust module is not present in this environment."
            )
        dispatch = getattr(_rust_module, "get_container_metadata", None)
        if dispatch is None:
            raise NotImplementedError("The Rust binding does not expose get_container_metadata")
        driver_handle = self._ensure_driver_handle()
        try:
            raw_response = (
                dispatch(driver_handle, container_link)
                if deadline is None
                else dispatch(driver_handle, container_link, timeout_seconds=remaining_timeout(deadline))
            )
        except TimeoutError as exc:
            if deadline is None:
                raise
            raise CosmosClientTimeoutError(error=exc) from exc
        except _DRIVER_TRANSPORT_ERROR as exc:
            raise ServiceResponseError(message=str(exc)) from exc
        except _DRIVER_RESPONSE_ERROR as exc:
            raise metadata_exception_from_binding(exc) from exc
        return build_container_metadata(raw_response)

    def execute_pages(
        self, prepared: PreparedQuery, *, deadline: Optional[float] = None
    ) -> Iterator[QueryPage]:
        """Yield one page from the selected stateless or retained-cursor dispatch."""
        self.validate_page_request(prepared)
        method = get_page_binding_method(
            prepared.op, uses_cursor=prepared.cursor is not None
        )
        dispatch = _get_page_dispatch(method)
        if dispatch is None:
            raise BindingProtocolError("Validated page dispatch is no longer available")
        driver_handle = self._ensure_driver_handle()
        binding_request = build_binding_request_from_page(prepared)
        _LOGGER.debug(
            "cosmos backend=%s op=%s dispatch=%s",
            BACKEND_NAME_RUST,
            prepared.op,
            method,
        )
        with page_dispatch_errors(deadline, _UNSUPPORTED_QUERY_ERROR, _DRIVER_TRANSPORT_ERROR):
            args, kwargs = page_dispatch_arguments(driver_handle, binding_request, prepared, deadline)
            result = dispatch(*args, **kwargs)
            response = build_backend_response(*result)
        yield build_query_page(prepared, response)

    def validate_page_request(self, prepared: PreparedQuery) -> None:
        """Check module/export availability without acquiring a driver."""
        validate_page_request(prepared, _rust_module, _get_page_dispatch, "RustBinding")

    def create_item_feed_cursor(self) -> _ItemFeedCursor:
        """Create pager-owned state without acquiring a driver."""
        if _rust_module is None:
            raise PagePreflightError(
                "The compiled azure.cosmos._rust module is not present."
            )
        if not hasattr(_rust_module, "_ItemFeedCursor"):
            raise RuntimeError(
                "The compiled extension lacks _ItemFeedCursor; rebuild it from the current source."
            )
        return _rust_module._ItemFeedCursor()
