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
from dataclasses import replace

import json
import logging
from typing import TYPE_CHECKING, Any, Iterator, Optional

from azure.core.exceptions import ServiceResponseError
from .._operation_deadline import remaining_timeout
from ..exceptions import CosmosClientTimeoutError

from .cosmos_backend import CosmosBackend
from .operations import (
    OP_LIST_CONTAINERS,
    OP_LIST_DATABASES,
    OP_READ_ALL_ITEMS,
    OP_QUERY_CHANGE_FEED,
    OP_QUERY_ITEMS,
    OP_TO_BINDING_METHOD,
    get_page_binding_method,
)
from .errors import BackendProtocolError, PageNotSupportedByBackendError, QueryNotSupportedByBackendError
from .contracts import BackendResponse, ContainerMetadata, PreparedClientConfig, PreparedQuery, PreparedRequest, QueryPage
from ._binding_conversions import build_backend_response, build_container_metadata, metadata_exception_from_binding
from ._shared import (
    RustBackendShared,
    _binding_error_type,
    configure_packaged_query_plan_interop,
    driver_transport_error_type,
    driver_unsupported_query_error_type,
)
from .constants import BACKEND_NAME_RUST
from .request_settings import native_settings_contract_error

if TYPE_CHECKING:
    from azure.cosmos._rust import ItemFeedCursor

_LOGGER = logging.getLogger(__name__)

# Paged feeds that take no SQL, so their binding request carries an empty body.
# Change feed carries mode/start/scope data; the remaining page operations carry SQL.
_PARAMETERLESS_FEED_OPS = frozenset({OP_READ_ALL_ITEMS, OP_LIST_DATABASES, OP_LIST_CONTAINERS})

# Imported once when this module loads; not changed afterwards.
_rust_module: Optional[Any] = None
try:
    from azure.cosmos import _rust  # type: ignore[attr-defined]
    _rust_module = _rust
    configure_packaged_query_plan_interop(_rust_module)
except ImportError:
    _LOGGER.debug(
        "_rust module not available; RustBackend operations "
        "will raise NotImplementedError until the Rust module is built."
    )

# The binding's error for a failure that produced no HTTP response, captured
# once at load. A driver operation that fails before any reply comes back
# raises this; we re-raise it as azure-core's ServiceResponseError (see
# driver_transport_error_type).
_DRIVER_TRANSPORT_ERROR = driver_transport_error_type(_rust_module)
_DRIVER_RESPONSE_ERROR = _binding_error_type(_rust_module, "DriverResponseError")
_UNSUPPORTED_QUERY_ERROR = driver_unsupported_query_error_type(_rust_module)
_native_runtime_module = _rust_module
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


def build_binding_request_from_page(prepared: PreparedQuery) -> PreparedRequest:
    """Adapt the page contract to the binding's current request object.

    ``query_items`` and ``query_containers`` carry their SQL and parameters as a
    JSON body; parameterless feeds send none, and change feed carries its
    mode/start/scope mapping. Continuation and page size replace the corresponding
    typed query settings and remove matching lowercase header keys when supplied.
    """
    if prepared.op == OP_QUERY_CHANGE_FEED:
        body = json.dumps(prepared.change_feed, separators=(",", ":")).encode("utf-8")
    elif prepared.op in _PARAMETERLESS_FEED_OPS:
        body = b""
    else:
        if prepared.query is None:
            raise ValueError("{} requires PreparedQuery.query.".format(prepared.op))
        payload: dict[str, Any] = {"query": prepared.query}
        if prepared.parameters:
            payload["parameters"] = list(prepared.parameters)
        if prepared.op == OP_QUERY_ITEMS and prepared.cursor is not None:
            payload = {"query": payload, **(prepared.query_scope.as_dict() if prepared.query_scope is not None else {})}
        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    headers = dict(prepared.headers)
    query_settings = prepared.settings.query
    if prepared.continuation is not None:
        headers.pop("x-ms-continuation", None)
        query_settings = replace(query_settings, continuation=prepared.continuation)
    if prepared.max_item_count is not None:
        headers.pop("x-ms-max-item-count", None)
        query_settings = replace(query_settings, max_item_count=prepared.max_item_count)
    return PreparedRequest(
        op=prepared.op,
        container_link=prepared.container_link,
        body_bytes=body,
        partition_key=prepared.partition_key,
        headers=headers,
        settings=replace(prepared.settings, query=query_settings),
    )


def _runtime_configuration() -> Optional[tuple[Optional[bool], Optional[float], Optional[float]]]:
    if _native_runtime_module is None:
        return None
    return _native_runtime_module.runtime_configuration()


class RustBackend(RustBackendShared, CosmosBackend):
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
    ``PageNotSupportedByBackendError`` rather than ``NotImplementedError``.

    :class:`~azure.cosmos._backend._shared.RustBackendShared` stores common client
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
        strict_isolation: bool = False,
    ) -> None:
        """Store client settings and register process-wide Rust configuration."""
        # The sync backend has no fields beyond the shared ones, so initialize shared
        # state directly. This also registers against the endpoint and, in strict
        # isolation mode, may raise StrictDriverIsolationError for a config conflict.
        self._init_shared(
            endpoint, master_key, client_config, token_credential, strict_isolation
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
                "RustBackend: the compiled azure.cosmos._rust "
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
                raise RuntimeError("RustBackend: the client is closed.")
            if self._driver_handle is None:
                self._driver_handle = self._initialize_driver(_rust_module, _runtime_configuration)
            return self._driver_handle

    def close(self) -> None:
        """Release this client's registration, credential-bridge hold, and Rust driver reference.

        Mark the client closed and take its handle once, so repeated calls cannot
        release another client's reference. Other clients and operations can keep
        the driver alive. The customer's own credential is not closed.
        """
        with self._driver_handle_lock:
            self._closing = True
            driver_handle = self._driver_handle
            self._driver_handle = None
        self._release_config_once()
        self._close_token_credential_bridge()
        if driver_handle is None or _rust_module is None:
            return
        release_driver_handle = getattr(_rust_module, "release_driver_handle", None)
        if release_driver_handle is None:
            return
        try:
            release_driver_handle(driver_handle)
        except Exception:  # pylint: disable=broad-except
            _LOGGER.debug("RustBackend.close failed for handle=%s", driver_handle, exc_info=True)

    def __del__(self) -> None:
        """Release resources if the client was not closed explicitly."""
        try:
            self.close()
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
                "RustBackend.execute: the compiled "
                "azure.cosmos._rust module is not present in "
                "this environment. Build it with `maturin develop` from "
                "the repo root."
            )

        driver_handle = self._ensure_driver_handle()
        # Look up the binding's function for this op; None if unsupported.
        binding_function = _get_binding_function(prepared.op)
        if binding_function is None:
            raise NotImplementedError(
                "RustBackend.execute does not yet support op={!r}.".format(prepared.op)
            )
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
            raise BackendProtocolError(f"The binding returned no response for {prepared.op!r}")
        return build_backend_response(*raw_response)

    def fault_injection_rule_hit_count(self, rule_id: str) -> int:
        """Return how many Rust transport attempts applied one configured rule."""
        if _rust_module is None:
            raise NotImplementedError(
                "Rust fault injection requires the compiled azure.cosmos._rust module."
            )
        return int(
            _rust_module.fault_injection_rule_hit_count(
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
                "RustBackend.get_container_metadata: the compiled "
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
            raise BackendProtocolError("Validated page dispatch is no longer available")
        driver_handle = self._ensure_driver_handle()
        binding_request = build_binding_request_from_page(prepared)
        _LOGGER.debug(
            "cosmos backend=%s op=%s dispatch=%s",
            BACKEND_NAME_RUST,
            prepared.op,
            method,
        )
        try:
            if prepared.cursor is not None:
                result = dispatch(
                    driver_handle,
                    binding_request,
                    prepared.cursor,
                    timeout_seconds=remaining_timeout(deadline),
                )
            elif prepared.op == OP_LIST_DATABASES and deadline is not None:
                result = dispatch(
                    driver_handle, binding_request, timeout_seconds=remaining_timeout(deadline),
                )
            else:
                result = dispatch(driver_handle, binding_request)
            response = build_backend_response(*result)
        except TimeoutError as exc:
            if deadline is None:
                raise
            raise CosmosClientTimeoutError(error=exc) from exc
        except _UNSUPPORTED_QUERY_ERROR as exc:
            raise QueryNotSupportedByBackendError(str(exc)) from exc
        except _DRIVER_TRANSPORT_ERROR as exc:
            raise ServiceResponseError(message=str(exc)) from exc
        continuation = (
            response.headers.get("x-ms-continuation") if response.headers else None
        )
        yield QueryPage(
            status_code=response.status_code,
            continuation=continuation,
            sub_status=response.sub_status,
            headers=response.headers,
            body=response.body,
            diagnostics=response.diagnostics,
            has_more=(
                prepared.cursor.has_more
                if prepared.op == OP_QUERY_ITEMS and prepared.cursor is not None
                else None
            ),
            continuation_supported=(
                prepared.cursor.continuation_supported
                if prepared.op == OP_QUERY_ITEMS and prepared.cursor is not None
                else True
            ),
        )

    def validate_page_request(self, prepared: PreparedQuery) -> None:
        """Check module/export availability without acquiring a driver."""
        if _rust_module is None:
            raise PageNotSupportedByBackendError(
                "RustBackend.execute_pages: the compiled azure.cosmos._rust "
                "module is not present in this environment. Build it with "
                "`maturin develop` from the repo root."
            )
        uses_cursor = prepared.cursor is not None
        method = get_page_binding_method(prepared.op, uses_cursor=uses_cursor)
        dispatch = _get_page_dispatch(method)
        if uses_cursor and method is not None and dispatch is None:
            raise RuntimeError(
                f"The compiled azure.cosmos._rust extension does not export {method}; "
                "rebuild it from the current source."
            )
        if dispatch is None:
            raise PageNotSupportedByBackendError(
                "RustBackend.execute_pages does not yet support op={!r}.".format(
                    prepared.op
                )
            )

    def create_item_feed_cursor(self) -> ItemFeedCursor:
        """Create pager-owned state without acquiring a driver."""
        if _rust_module is None:
            raise PageNotSupportedByBackendError(
                "The compiled azure.cosmos._rust module is not present."
            )
        if not hasattr(_rust_module, "ItemFeedCursor"):
            raise RuntimeError(
                "The compiled extension lacks ItemFeedCursor; rebuild it from the current source."
            )
        return _rust_module.ItemFeedCursor()
