# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Run sync client operations through the compiled Rust part of the SDK.

For example, when the customer app reads database "sales", BindingAdapter
passes the prepared read to azure.cosmos._rust, the compiled Rust part of the
SDK. It sends the request to the service backend and turns the result into
Python values, or into a Python exception if the read failed::

    BindingAdapter: prepare the read for database "sales"
        -> azure.cosmos._rust: send the request to the service backend
        -> service backend: return the database properties
        -> azure.cosmos._rust: turn the response into Python values

If azure.cosmos._rust is missing, this module still imports, but creating a
client raises ImportError.
"""
from __future__ import annotations
import logging
from concurrent.futures import wait
from typing import TYPE_CHECKING, Any, Iterator, Optional

from azure.core.exceptions import ClientAuthenticationError, ServiceResponseError
from .._operation_deadline import remaining_timeout
from .._telemetry import get_operation, log_error_diagnostics, log_response_diagnostics, record_failed_lookup
from ..runtime import CosmosRuntime

from .cosmos_backend import CosmosBackend
from .operations import (
    OP_TO_BINDING_FUNCTION_NAME,
    get_page_binding_function_name,
)
from .errors import BindingProtocolError, PagePreflightError
from .contracts import (
    BackendResponse, ContainerMetadata, PreparedClientConfig, PreparedPageRequest, PreparedRequest, BackendPage,
)
from ._binding_conversions import (
    build_backend_response, build_binding_request_from_page,
    build_container_metadata, response_exception_from_binding,
    build_backend_page, page_binding_call_arguments,
)
from ._binding_adapter_shared import (
    BindingAdapterShared,
    _binding_error_type,
    driver_transport_error_type,
    driver_unsupported_query_error_type,
    finalize_adapter_resources,
    is_credential_error,
    operation_timeout_error,
    page_binding_call_errors,
    release_driver_handle_quietly,
    validate_page_request,
)
from .constants import BACKEND_NAME_RUST
from .request_settings import binding_settings_contract_error

if TYPE_CHECKING:
    from azure.cosmos._rust import _DriverHandle, _ItemFeedCursor

_LOGGER = logging.getLogger(__name__)

# Load once during normal use. Tests can replace this reference with a fake binding.
_rust_module: Optional[Any] = None
try:
    from azure.cosmos import _rust  # type: ignore[attr-defined]
    _rust_module = _rust
except ImportError:
    _LOGGER.debug(
        "_rust module not available; BindingAdapter construction raises "
        "ImportError if the compiled Rust extension cannot be loaded."
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
    the public method the customer called, including ``get_throughput`` and
    ``replace_throughput``. ``OP_TO_BINDING_FUNCTION_NAME`` holds the mapping, and
    ``BindingAdapter.execute`` is the only caller.

    ``None`` means the binding is absent, its export is missing, or the
    operation has no mapping. For example, ``query_items`` has no mapping here
    because feeds go through ``execute_pages``. ``execute`` distinguishes an
    installation problem from an operation this entry point does not support.

    A match only means the binding exposes that name. It acquires no Rust
    driver, checks no arguments, and promises nothing about service support.

    :param op: The Python wrapper's operation name, from the prepared request.
    :type op: str
    :returns: The matching binding function, or ``None``.
    :rtype: typing.Callable or None
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
    :type binding_function_name: str or None
    :returns: The matching binding function, or ``None``.
    :rtype: typing.Callable or None
    """
    if binding_function_name is None or _rust_module is None:
        return None
    return getattr(_rust_module, binding_function_name, None)


class BindingAdapter(BindingAdapterShared, CosmosBackend):
    """Keep one client's settings and run its operations.

    The adapter connects to the service on first use and reuses that
    connection for later operations::

        create client -> save settings, not connected yet
        first operation -> connect -> run
        later operation -> reuse the connection -> run
        close -> release this client's hold on the connection

    BindingAdapterShared supplies the common setup and cleanup code, not
    shared settings.
    """

    name = BACKEND_NAME_RUST

    def __init__(
        self,
        endpoint: str,
        master_key: Optional[str] = None,
        client_config: Optional[PreparedClientConfig] = None,
        token_credential: Optional[Any] = None,
        runtime: Optional[CosmosRuntime] = None,
    ) -> None:
        """Save the client's inputs. This does not connect to the service.

        See BindingAdapterShared._init_shared for what is saved and which
        settings are rejected.
        """
        self._init_shared(endpoint, master_key, client_config, token_credential, runtime)

    def _ensure_driver_handle(self, *, deadline: Optional[float] = None) -> _DriverHandle:
        """Reuse a handle or wait within this caller's budget for shared acquisition.

        One dedicated Python daemon thread runs this adapter's pending acquisition
        attempt for concurrent callers. Each caller has its own deadline.
        Timing out or Ctrl+C stops only that wait, not the acquisition thread.
        A late handle remains available to an open client. If close wins, the
        worker releases the acquisition instead of publishing it.

        :keyword deadline: Absolute monotonic deadline for this caller's wait, or None.
        :paramtype deadline: float or None
        :return: Shared owning driver handle.
        :rtype: ~azure.cosmos._rust._DriverHandle
        """
        if _REQUEST_CONTRACT_ERROR is not None:
            raise RuntimeError(_REQUEST_CONTRACT_ERROR)
        if _rust_module is None:
            raise NotImplementedError(
                "BindingAdapter: the compiled azure.cosmos._rust "
                "module is not present in this environment. Build it with "
                "`maturin develop` from the repo root."
            )
        remaining_timeout(deadline)
        with self._driver_handle_lock:
            if self._closing:
                raise RuntimeError("BindingAdapter: the client is closed.")
            if self._driver_handle is not None:
                return self._driver_handle
            future = self._start_driver_acquisition(_rust_module, _LOGGER)
        while not future.done():
            remaining = remaining_timeout(deadline)
            # Short waits let Python process Ctrl+C on Windows as well as POSIX.
            wait((future,), timeout=0.1 if remaining is None else min(remaining, 0.1))
            remaining_timeout(deadline)
        driver_handle = future.result()
        remaining_timeout(deadline)
        return driver_handle

    def close(self) -> None:
        """Release this client's resources without closing another client's driver.

        When two clients have acquired the same driver::

            A holds H_A and B holds H_B for driver D1
            close A -> release H_A's cache acquisition; B still holds H_B
            close A again -> no second acquisition release

        Mark this BindingAdapter closed and remove its handle before cleanup. Release
        its SDK-owned async credential bridge, if present, but not the customer's
        credential. Driver release is still attempted if credential cleanup raises.
        An operation already in progress can also retain the driver.
        """
        with self._driver_handle_lock:
            self._closing = True
            driver_handle = self._driver_handle
            self._driver_handle = None
            self._runtime = None
        try:
            self._close_token_credential_bridge()
        finally:
            if driver_handle is not None:
                release_driver_handle_quietly(driver_handle, _rust_module)

    def __del__(self) -> None:
        """Hand abandoned resources to the cleanup helper without raising.

        Unclosed BindingAdapter -> detach its async credential bridge and driver handle
        -> finalize_adapter_resources. Explicit close remains the normal path.
        """
        try:
            with self._driver_handle_lock:
                self._closing = True
                driver_handle, self._driver_handle = self._driver_handle, None
            credential = self._take_token_credential_for_close()
            finalize_adapter_resources(credential, driver_handle, _rust_module)
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

        :param prepared: Operation inputs to send through the binding.
        :type prepared: ~azure.cosmos._backend.contracts.PreparedRequest
        :keyword deadline: Absolute monotonic deadline, or None to derive a budget from settings.
        :paramtype deadline: float or None
        :return: Normalized backend response with unparsed body bytes.
        :rtype: ~azure.cosmos._backend.contracts.BackendResponse
        """
        if not isinstance(prepared, PreparedRequest):
            raise TypeError("execute requires a PreparedRequest")
        prepared = self._with_client_headers(prepared)
        deadline = self._request_deadline(deadline, prepared.settings.timeout_seconds)
        if _rust_module is None:
            raise ImportError(
                "BindingAdapter.execute: the compiled "
                "azure.cosmos._rust module is not present in "
                "this environment. Install an azure-cosmos wheel built for this "
                "operating system, processor, and Python version, or rebuild "
                "the extension from the current source.",
                name="azure.cosmos._rust",
            )

        binding_function = _binding_function_for_op(prepared.op)
        if not callable(binding_function):
            binding_name = OP_TO_BINDING_FUNCTION_NAME.get(prepared.op)
            if binding_name is not None:
                raise RuntimeError(
                    f"The compiled azure.cosmos._rust extension does not export a callable {binding_name}; "
                    "install a matching azure-cosmos wheel or rebuild the extension from the current source."
                )
            raise NotImplementedError("BindingAdapter.execute does not yet support op={!r}.".format(prepared.op))
        operation = get_operation(self, prepared.op)
        contribution = operation.begin_contribution() if operation is not None else None
        try:
            driver_handle = self._ensure_driver_handle(deadline=deadline)
        except Exception as exc:
            if contribution is not None:
                contribution.setup_error(exc)
            log_error_diagnostics(self, exc, prepared.op)
            raise
        # This records the chosen function, not proof that a request was sent.
        # Do not include the driver handle in logs.
        _LOGGER.debug(
            "cosmos backend=%s op=%s binding_function=%s",
            BACKEND_NAME_RUST,
            prepared.op,
            OP_TO_BINDING_FUNCTION_NAME.get(prepared.op),
        )
        raw_response = self._call_operation(binding_function, driver_handle, prepared, deadline, contribution)
        if raw_response is None:
            raise BindingProtocolError(f"The binding returned no response for {prepared.op!r}")
        if contribution is not None:
            raw_response = contribution.response(raw_response)
        response = build_backend_response(*raw_response)
        log_response_diagnostics(self, prepared.op, response)
        return response

    def _call_operation(
        self,
        binding_function: Any,
        driver_handle: _DriverHandle,
        prepared: PreparedRequest,
        deadline: Optional[float],
        contribution: Any,
    ) -> Any:
        """Call the selected binding export and translate operation failures.

        :param binding_function: Callable export selected and validated before driver acquisition.
        :type binding_function: typing.Callable
        :param driver_handle: Acquired owning handle for this operation.
        :type driver_handle: ~azure.cosmos._rust._DriverHandle
        :param prepared: Operation inputs, including merged client headers.
        :type prepared: ~azure.cosmos._backend.contracts.PreparedRequest
        :param deadline: Absolute monotonic deadline, or None.
        :type deadline: float or None
        :param contribution: Operation diagnostics recorder, or None when tracing is inactive.
        :type contribution: typing.Any
        :return: Raw binding response tuple, before response normalization.
        :rtype: typing.Any
        """
        # A transport error does not prove the service backend did no work.
        try:
            binding_kwargs: dict[str, Any] = {}
            if deadline is not None:
                binding_kwargs["timeout_seconds"] = remaining_timeout(deadline)
            if contribution is not None:
                binding_kwargs["include_attempts"] = True
            raw_response = binding_function(driver_handle, prepared, **binding_kwargs)
        except TimeoutError as exc:
            if contribution is not None:
                contribution.error(exc)
            if deadline is None or is_credential_error(exc):
                raise
            raise operation_timeout_error(exc) from exc
        except ClientAuthenticationError as exc:
            if contribution is not None:
                contribution.error(exc)
            raise
        except _DRIVER_TRANSPORT_ERROR as exc:
            if contribution is not None:
                contribution.error(exc)
            raise ServiceResponseError(message=str(exc)) from exc
        except _DRIVER_RESPONSE_ERROR as exc:
            if contribution is not None:
                contribution.error(exc)
            error = response_exception_from_binding(exc)
            log_error_diagnostics(self, error, prepared.op)
            raise error from exc
        except Exception as exc:
            # Match the binding contract: only validation errors and binding-marked
            # credential errors carry attempt diagnostics.
            if contribution is not None and (isinstance(exc, ValueError) or is_credential_error(exc)):
                contribution.error(exc)
            raise
        return raw_response

    def get_container_metadata(
        self, container_link: str, *, deadline: Optional[float] = None, op: Optional[str] = None
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
        ``op`` names the operation that needs the lookup, such as
        ``"read_items"``. When that call is traced, a failed lookup's
        diagnostics are recorded as that call's binding result.

        :param container_link: Container resource address.
        :type container_link: str
        :keyword deadline: Absolute monotonic deadline, or None to use the client timeout.
        :paramtype deadline: float or None
        :keyword op: Operation requiring metadata, or None when no operation owns the lookup.
        :paramtype op: str or None
        :return: Validated container identity and partition-key definition.
        :rtype: ~azure.cosmos._backend.contracts.ContainerMetadata
        """
        deadline = self._request_deadline(deadline)
        if _rust_module is None:
            raise NotImplementedError(
                "BindingAdapter.get_container_metadata: the compiled "
                "azure.cosmos._rust module is not present in this environment."
            )
        binding_function = getattr(_rust_module, "get_container_metadata", None)
        if binding_function is None:
            raise NotImplementedError("The Rust binding does not expose get_container_metadata")
        operation = get_operation(self, op) if op is not None else None
        try:
            driver_handle = self._ensure_driver_handle(deadline=deadline)
        except Exception as exc:
            record_failed_lookup(operation, exc, setup=True)
            log_error_diagnostics(self, exc)
            raise
        binding_kwargs: dict[str, Any] = {}
        if deadline is not None:
            binding_kwargs["timeout_seconds"] = remaining_timeout(deadline)
        if operation is not None:
            binding_kwargs["include_attempts"] = True
        try:
            # The non-None export is a native callable; pylint cannot inspect the extension.
            # pylint: disable-next=not-callable
            raw_response = binding_function(driver_handle, container_link, **binding_kwargs)
        except TimeoutError as exc:
            record_failed_lookup(operation, exc)
            if deadline is None or is_credential_error(exc):
                raise
            raise operation_timeout_error(exc) from exc
        except ClientAuthenticationError as exc:
            record_failed_lookup(operation, exc)
            raise
        except _DRIVER_TRANSPORT_ERROR as exc:
            record_failed_lookup(operation, exc)
            raise ServiceResponseError(message=str(exc)) from exc
        except _DRIVER_RESPONSE_ERROR as exc:
            record_failed_lookup(operation, exc)
            error = response_exception_from_binding(exc)
            log_error_diagnostics(self, error)
            raise error from exc
        except Exception as exc:
            # Match the binding contract: only validation errors and binding-marked
            # credential errors carry attempt diagnostics.
            if isinstance(exc, ValueError) or is_credential_error(exc):
                record_failed_lookup(operation, exc)
            raise
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

        :param prepared: Inputs and optional retained cursor for one page fetch.
        :type prepared: ~azure.cosmos._backend.contracts.PreparedPageRequest
        :keyword deadline: Absolute monotonic deadline, or None to derive a budget from settings.
        :paramtype deadline: float or None
        :return: Iterator yielding one backend page.
        :rtype: typing.Iterator[azure.cosmos._backend.contracts.BackendPage]
        """
        self.validate_page_request(prepared)
        deadline = self._request_deadline(deadline, prepared.settings.timeout_seconds)
        binding_function_name = get_page_binding_function_name(
            prepared.op, uses_cursor=prepared.cursor is not None
        )
        binding_function = _binding_function_by_name(binding_function_name)
        if binding_function is None:
            raise BindingProtocolError("Validated page binding function is no longer available")
        operation = (
            get_operation(self, prepared.op)
            if prepared.op in ("list_databases", "query_databases", "list_containers", "query_containers")
            or (
                prepared.op in ("read_items", "read_all_items", "query_items", "query_items_change_feed")
                and prepared.cursor is not None
            )
            else None
        )
        contribution = operation.begin_contribution() if operation is not None else None
        try:
            driver_handle = self._ensure_driver_handle(deadline=deadline)
        except Exception as exc:
            if contribution is not None:
                contribution.setup_error(exc)
            log_error_diagnostics(self, exc, prepared.op)
            raise
        binding_request = self._with_client_headers(build_binding_request_from_page(prepared))
        _LOGGER.debug(
            "cosmos backend=%s op=%s binding_function=%s",
            BACKEND_NAME_RUST,
            prepared.op,
            binding_function_name,
        )
        with page_binding_call_errors(deadline, _UNSUPPORTED_QUERY_ERROR, _DRIVER_TRANSPORT_ERROR):
            args, kwargs = page_binding_call_arguments(driver_handle, binding_request, prepared, deadline)
            if contribution is not None:
                kwargs["include_attempts"] = True
            try:
                result = binding_function(*args, **kwargs)
            except (TimeoutError, ClientAuthenticationError) as exc:
                if contribution is not None:
                    contribution.error(exc)
                raise
            except _DRIVER_TRANSPORT_ERROR as exc:
                if contribution is not None:
                    contribution.error(exc)
                raise
            except _UNSUPPORTED_QUERY_ERROR as exc:
                if contribution is not None:
                    contribution.error(exc)
                raise
            except Exception as exc:
                # Match the binding contract: only validation errors and binding-marked
                # credential errors carry attempt diagnostics.
                if contribution is not None and (isinstance(exc, ValueError) or is_credential_error(exc)):
                    contribution.error(exc)
                raise
            if contribution is not None:
                result = contribution.response(result)
            response = build_backend_response(*result)
        log_response_diagnostics(self, prepared.op, response)
        yield build_backend_page(prepared, response)

    def validate_page_request(self, prepared: PreparedPageRequest) -> None:
        """Check page support before acquiring a driver or fetching results.

        Orders query with feed cursor -> require fetch_page_with_cursor.
        Orders query without feed cursor -> require query_items.
        Missing support raises here instead of after driver acquisition.

        :param prepared: Page request whose operation and cursor mode require validation.
        :type prepared: ~azure.cosmos._backend.contracts.PreparedPageRequest
        """
        validate_page_request(prepared, _rust_module, _binding_function_by_name, "BindingAdapter")

    def create_item_feed_cursor(self) -> _ItemFeedCursor:
        """Create an empty feed cursor retained by one page iterator.

        Create feed cursor C -> first page uses C -> later pages reuse C.
        This calls the binding's cursor constructor synchronously, but does not
        acquire a driver handle or fetch a page. One page iterator retains C.

        :return: New empty native item-feed cursor.
        :rtype: ~azure.cosmos._rust._ItemFeedCursor
        """
        if _rust_module is None:
            raise PagePreflightError(
                "The compiled azure.cosmos._rust module is not present."
            )
        if not hasattr(_rust_module, "_ItemFeedCursor"):
            raise RuntimeError(
                "The compiled binding lacks _ItemFeedCursor; rebuild it from the current source."
            )
        # This private export is the native cursor constructor used by the adapter.
        return _rust_module._ItemFeedCursor()  # pylint: disable=protected-access
