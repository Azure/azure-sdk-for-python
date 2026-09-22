# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Call the Python/Rust binding from the synchronous Python wrapper.

This file is Python wrapper code, not the compiled binding despite its name.
The Python/Rust binding, azure.cosmos._rust, calls the separately owned Rust
driver. The Rust driver
chooses a region and sends requests to the service backend. On first use,
the binding returns a driver handle: a string identifying the driver for later
calls. Clients with matching endpoints, credentials, and settings can share
a driver. Closing one client releases its reference, not other clients' work.

Importing this module without the binding remains possible for legacy
migration checks. Constructing the Rust caller requires the binding to check
shared runtime settings. A missing binding is not a supported release mode.
Missing operation functions are checked before use.
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

# Load once during normal use. Tests can replace this reference with a fake binding.
_rust_module: Optional[Any] = None
try:
    from azure.cosmos import _rust  # type: ignore[attr-defined]
    _rust_module = _rust
except ImportError:
    _LOGGER.debug(
        "_rust module not available; RustBinding operations "
        "will raise NotImplementedError until the Rust module is built."
    )

# Save binding exception classes for conversion to public Python exceptions.
_DRIVER_TRANSPORT_ERROR = driver_transport_error_type(_rust_module)
_DRIVER_RESPONSE_ERROR = _binding_error_type(_rust_module, "_DriverResponseError")
_UNSUPPORTED_QUERY_ERROR = driver_unsupported_query_error_type(_rust_module)
_REQUEST_CONTRACT_ERROR = native_settings_contract_error(_rust_module) if _rust_module is not None else None


# Look up functions on each call so tests can supply a replacement binding.
def _get_binding_function(op: str) -> Optional[Any]:
    """Return the function for this operation, or None if unavailable."""
    method = OP_TO_BINDING_METHOD.get(op)
    if method is None or _rust_module is None:
        return None
    return getattr(_rust_module, method, None)


def _get_page_dispatch(method: Optional[str]) -> Optional[Any]:
    """Return the named page-fetch function, or None if unavailable."""
    if method is None or _rust_module is None:
        return None
    return getattr(_rust_module, method, None)


class RustBinding(RustBindingShared, CosmosBackend):
    """Send one CosmosClient's requests and release its resources on close.

    RustBindingShared stores client settings and provides shared cleanup.
    This Python class asks the binding to acquire a Rust driver on first use,
    makes synchronous binding calls, and converts results for Python wrapper
    response helpers.
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
        """Acquire this client's driver handle once and reuse it.

        The binding either creates a driver or adds a reference to a matching
        shared driver. The lock prevents concurrent first calls on this client
        from acquiring separate references. Failed acquisition can be attempted
        again later. Closing prevents new acquisition, but cannot stop a call
        that already read the handle.
        """
        # Reject incompatible request settings even if a driver was already acquired.
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
        # Another thread may have acquired the handle while this one waited.
        with self._driver_handle_lock:
            # close() also clears the handle; do not mistake a closed client for
            # one that has not acquired a driver yet.
            if self._closing:
                raise RuntimeError("RustBinding: the client is closed.")
            if self._driver_handle is None:
                self._driver_handle = self._initialize_driver(_rust_module)
            return self._driver_handle

    def close(self) -> None:
        """Release this client's credential bridge and Rust driver reference.

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

        binding_function = _get_binding_function(prepared.op)
        if binding_function is None:
            raise NotImplementedError(
                "RustBinding.execute does not yet support op={!r}.".format(prepared.op)
            )
        driver_handle = self._ensure_driver_handle()
        # This records the chosen function, not proof that a request was sent.
        # Do not include the driver handle in logs.
        _LOGGER.debug(
            "cosmos backend=%s op=%s dispatch=%s",
            BACKEND_NAME_RUST,
            prepared.op,
            OP_TO_BINDING_METHOD.get(prepared.op),
        )
        # No response does not prove the service backend did no work. Convert
        # the error without retrying the operation through Python.
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
        """Return how many Rust request attempts applied the named test rule."""
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
        """Get the container ID and partition-key definition from the driver.

        The driver may fetch these properties if they are not already cached.
        """
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
        """Fetch one page, passing the binding's saved query progress if present."""
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
        """Check that the extension has the needed function, without a driver."""
        validate_page_request(prepared, _rust_module, _get_page_dispatch, "RustBinding")

    def create_item_feed_cursor(self) -> _ItemFeedCursor:
        """Create the binding's query-progress object without acquiring a Rust driver."""
        if _rust_module is None:
            raise PagePreflightError(
                "The compiled azure.cosmos._rust module is not present."
            )
        if not hasattr(_rust_module, "_ItemFeedCursor"):
            raise RuntimeError(
                "The compiled extension lacks _ItemFeedCursor; rebuild it from the current source."
            )
        return _rust_module._ItemFeedCursor()
