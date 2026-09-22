# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Execute synchronous requests through the compiled Python/Rust binding.

A customer app's order read crosses these components::

    Python wrapper: prepared read of order-42 -> RustBackend
        -> binding layer: azure.cosmos._rust
        -> Rust driver: a CosmosDriver object
        -> service backend: Cosmos DB

This module is Python wrapper code. The binding calls the separately owned Rust
driver, which routes and sends requests. Python response helpers turn the
backend's result into the customer's item after execution returns.

Importing without the compiled binding remains possible for migration checks.
Construction still requires the binding to validate CosmosDriverRuntime
settings; a missing binding is not a supported release mode.
"""
from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Any, Iterator, Optional

from azure.core.exceptions import ServiceResponseError
from .._operation_deadline import remaining_timeout
from ..exceptions import CosmosClientTimeoutError

from .cosmos_backend import CosmosBackend
from .operations import (
    OP_TO_BINDING_FUNCTION_NAME,
    get_page_binding_function_name,
)
from .errors import BindingProtocolError, PagePreflightError
from .contracts import BackendResponse, ContainerMetadata, PreparedClientConfig, PreparedPageRequest, PreparedRequest, BackendPage
from ._binding_conversions import (
    build_backend_response, build_binding_request_from_page,
    build_container_metadata, metadata_exception_from_binding,
    build_backend_page, page_binding_call_arguments,
)
from ._rust_backend_shared import (
    RustBackendShared,
    _binding_error_type,
    driver_transport_error_type,
    driver_unsupported_query_error_type,
    finalize_backend_resources,
    page_binding_call_errors,
    validate_page_request,
)
from .constants import BACKEND_NAME_RUST
from .request_settings import binding_settings_contract_error

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
        "_rust module not available; RustBackend operations "
        "will raise NotImplementedError until the Rust module is built."
    )

# Save binding exception classes for conversion to public Python exceptions.
_DRIVER_TRANSPORT_ERROR = driver_transport_error_type(_rust_module)
_DRIVER_RESPONSE_ERROR = _binding_error_type(_rust_module, "_DriverResponseError")
_UNSUPPORTED_QUERY_ERROR = driver_unsupported_query_error_type(_rust_module)
_REQUEST_CONTRACT_ERROR = binding_settings_contract_error(_rust_module) if _rust_module is not None else None


# Look up functions per call so tests can install a stand-in binding.
def _binding_function_for_op(op: str) -> Optional[Any]:
    """Find the binding function that runs one operation.

    ``op`` is the Python wrapper's name for the operation. It usually matches
    the public method the customer called, but not always: ``get_throughput``
    and ``replace_throughput`` reach the binding as ``read_offer`` and
    ``replace_offer``. ``OP_TO_BINDING_FUNCTION_NAME`` holds the mapping, and
    ``RustBackend.execute`` is the only caller.

    ``None`` means the binding cannot run ``op`` in this process, which
    ``execute`` reports as ``NotImplementedError``. It covers four cases: the
    binding is not installed; the installed binding is too old to export this
    operation; the operation has no binding function at all; or the operation
    is a feed such as ``query_items``, left out of the mapping on
    purpose because feeds go through ``execute_pages``.

    A match only means the binding exposes that name. It acquires no Rust
    driver, checks no arguments, and promises nothing about service support.

    :param op: The Python wrapper's operation name, from the prepared request.
    :returns: The matching binding function, or ``None``.
    """
    binding_function_name = OP_TO_BINDING_FUNCTION_NAME.get(op)
    if binding_function_name is None or _rust_module is None:
        return None
    return getattr(_rust_module, binding_function_name, None)


def _binding_function_by_name(binding_function_name: Optional[str]) -> Optional[Any]:
    """Find a binding function the caller has already named.

    An operation name and a binding function name are usually the same word,
    which is what makes them easy to confuse: operation ``"read_item"`` is run
    by binding function ``"read_item"``. They come apart for feeds, where one
    operation can be served by two different binding functions::

        op "query_items", pager made no cursor -> binding function "query_items"
        op "query_items", pager made a cursor  -> binding function "fetch_page_with_cursor"

    Only the caller knows whether it made a cursor, so the caller resolves the
    name with ``get_page_binding_function_name`` and passes the result here. That is
    the entire reason this exists next to :func:`_binding_function_for_op`,
    which takes an operation name and resolves the mapping itself.

    ``get_page_binding_function_name`` returns ``None`` when no function matches
    the operation and cursor mode; that ``None`` is passed straight through.

    :param binding_function_name: A binding function name, or ``None`` if none applies.
    :returns: The matching binding function, or ``None``.
    """
    if binding_function_name is None or _rust_module is None:
        return None
    return getattr(_rust_module, binding_function_name, None)


class RustBackend(RustBackendShared, CosmosBackend):
    """Retain one client's settings and execute its prepared requests.

    A driver handle is a string identifying a CosmosDriver retained by the
    binding. This backend acquires one on first use and reuses it::

        construct -> store settings, no driver handle
        first operation -> acquire handle H -> execute
        later operation -> reuse H -> execute
        close -> release this client's acquisition of H

    H is an illustration, not an actual handle. Clients with matching account,
    credential, and configuration can share a CosmosDriver. RustBackendShared
    supplies common setup and cleanup code, not a shared Python settings object.
    """

    name = BACKEND_NAME_RUST

    def __init__(
        self,
        endpoint: str,
        master_key: Optional[str] = None,
        client_config: Optional[PreparedClientConfig] = None,
        token_credential: Optional[Any] = None,
    ) -> None:
        """Remember the client's inputs without acquiring a CosmosDriver.

        A customer app's endpoint and region preference follow this path::

            endpoint + credential + PreparedClientConfig
                -> save on this RustBackend
                -> check any completed CosmosDriverRuntime initialization

        The check neither creates CosmosDriverRuntime nor reserves its settings.
        """
        self._init_shared(
            endpoint, master_key, client_config, token_credential
        )

    def _ensure_driver_handle(self) -> str:
        """Acquire a handle on first use; reuse it on subsequent calls.

        Two initial callers on this backend must share one acquisition::

            caller A: lock -> acquire H -> store H -> unlock
            caller B: lock -> find stored H -> reuse H -> unlock
            later caller: find stored H -> reuse H without acquisition

        The binding may create a CosmosDriver or reuse a matching one. A failed
        acquisition leaves no handle and can be attempted again. Closing blocks
        new acquisition, but cannot revoke a handle another call already read.
        """
        # Reject incompatible request settings even if a driver was already acquired.
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
        # Another thread may have acquired the handle while this one waited.
        with self._driver_handle_lock:
            # close() also clears the handle; do not mistake a closed client for
            # one that has not acquired a driver yet.
            if self._closing:
                raise RuntimeError("RustBackend: the client is closed.")
            if self._driver_handle is None:
                self._driver_handle = self._initialize_driver(_rust_module)
            return self._driver_handle

    def close(self) -> None:
        """Release this client's resources without closing another client's driver.

        When two clients have acquired the same driver::

            clients A and B use H -> close A -> B still holds its acquisition
            close A again -> no second driver release

        Mark this RustBackend closed and remove its handle before cleanup. Release
        its SDK-owned async credential bridge, if present, but not the customer's
        credential. An operation already in progress can also retain the driver.
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
            _LOGGER.debug("RustBackend.close failed while releasing the driver handle")

    def __del__(self) -> None:
        """Hand abandoned resources to the cleanup helper without raising.

        Unclosed RustBackend -> detach its async credential bridge and driver handle
        -> finalize_backend_resources. Explicit close remains the normal path.
        """
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
        """Send one prepared operation and return a BackendResponse.

        An illustrative read of order-42 follows this path::

            PreparedRequest(op="read_item", ...)
                -> select _rust.read_item before acquiring a driver
                -> call with the driver handle and prepared request
                -> (status, sub_status, headers, body_bytes, diagnostics)
                -> BackendResponse

        The body remains bytes; Python response helpers produce the customer's
        item. If the deadline has 1.5 seconds left, pass timeout_seconds=1.5,
        not a fresh operation budget. Convert binding errors without retrying
        the operation through the legacy Python implementation.
        """
        if not isinstance(prepared, PreparedRequest):
            raise TypeError("execute requires a PreparedRequest")
        if _rust_module is None:
            raise NotImplementedError(
                "RustBackend.execute: the compiled "
                "azure.cosmos._rust module is not present in "
                "this environment. Build it with `maturin develop` from "
                "the repo root."
            )

        binding_function = _binding_function_for_op(prepared.op)
        if binding_function is None:
            raise NotImplementedError(
                "RustBackend.execute does not yet support op={!r}.".format(prepared.op)
            )
        driver_handle = self._ensure_driver_handle()
        # This records the chosen function, not proof that a request was sent.
        # Do not include the driver handle in logs.
        _LOGGER.debug(
            "cosmos backend=%s op=%s binding_function=%s",
            BACKEND_NAME_RUST,
            prepared.op,
            OP_TO_BINDING_FUNCTION_NAME.get(prepared.op),
        )
        # A transport error does not prove the service backend did no work.
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
        """Obtain container properties needed to prepare an item operation.

        For a customer app's orders container, an illustrative result is::

            "dbs/checkout/colls/orders"
                -> _rust.get_container_metadata(handle, container_link)
                -> (rid, ("/customerId",), "Hash", False)
                -> ContainerMetadata

        rid is the service-assigned container ID, not the name "orders".
        The driver may fetch missing properties rather than use cached ones.
        This returns properties, not order rows or a BackendResponse.
        """
        if _rust_module is None:
            raise NotImplementedError(
                "RustBackend.get_container_metadata: the compiled "
                "azure.cosmos._rust module is not present in this environment."
            )
        binding_function = getattr(_rust_module, "get_container_metadata", None)
        if binding_function is None:
            raise NotImplementedError("The Rust binding does not expose get_container_metadata")
        driver_handle = self._ensure_driver_handle()
        try:
            raw_response = (
                binding_function(driver_handle, container_link)
                if deadline is None
                else binding_function(driver_handle, container_link, timeout_seconds=remaining_timeout(deadline))
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
        self, prepared: PreparedPageRequest, *, deadline: Optional[float] = None
    ) -> Iterator[BackendPage]:
        """Yield one page when the caller iterates this generator.

        For an orders query using feed cursor C::

            PreparedPageRequest(op="query_items", cursor=C, ...)
                -> build the binding request
                -> _rust.fetch_page_with_cursor(handle, request, C, ...)
                -> one BackendPage with body and continuation metadata

        Without a feed cursor, select the stateless page binding function.
        Calling this method creates a generator; iteration performs the fetch.
        The caller owns subsequent page fetches, not a loop inside this method.
        """
        self.validate_page_request(prepared)
        binding_function_name = get_page_binding_function_name(
            prepared.op, uses_cursor=prepared.cursor is not None
        )
        binding_function = _binding_function_by_name(binding_function_name)
        if binding_function is None:
            raise BindingProtocolError("Validated page binding function is no longer available")
        driver_handle = self._ensure_driver_handle()
        binding_request = build_binding_request_from_page(prepared)
        _LOGGER.debug(
            "cosmos backend=%s op=%s binding_function=%s",
            BACKEND_NAME_RUST,
            prepared.op,
            binding_function_name,
        )
        with page_binding_call_errors(deadline, _UNSUPPORTED_QUERY_ERROR, _DRIVER_TRANSPORT_ERROR):
            args, kwargs = page_binding_call_arguments(driver_handle, binding_request, prepared, deadline)
            result = binding_function(*args, **kwargs)
            response = build_backend_response(*result)
        yield build_backend_page(prepared, response)

    def validate_page_request(self, prepared: PreparedPageRequest) -> None:
        """Check page support before acquiring a driver or fetching results.

        Orders query with feed cursor -> require fetch_page_with_cursor.
        Orders query without feed cursor -> require query_items.
        Missing support raises here instead of after driver acquisition.
        """
        validate_page_request(prepared, _rust_module, _binding_function_by_name, "RustBackend")

    def create_item_feed_cursor(self) -> _ItemFeedCursor:
        """Create an empty feed cursor retained by one page iterator.

        Create feed cursor C -> first page uses C -> later pages reuse C.
        This calls the binding's cursor constructor synchronously, but does not
        acquire a driver handle or fetch a page. One page iterator retains C.
        """
        if _rust_module is None:
            raise PagePreflightError(
                "The compiled azure.cosmos._rust module is not present."
            )
        if not hasattr(_rust_module, "_ItemFeedCursor"):
            raise RuntimeError(
                "The compiled binding lacks _ItemFeedCursor; rebuild it from the current source."
            )
        return _rust_module._ItemFeedCursor()
