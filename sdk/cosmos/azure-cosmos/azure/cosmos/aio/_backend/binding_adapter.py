# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------


"""Run async client operations through the compiled Rust part of the SDK.

For example, when the customer app awaits a read of database "sales",
AsyncBindingAdapter passes the prepared read to read_database_async in
azure.cosmos._rust and awaits the result. azure.cosmos._rust sends the request
to the service backend and turns the result into Python values, or into a
Python exception if the read failed.

The binding runs Rust work with the Tokio runtime; service I/O does not use
a Python executor worker per request. Driver acquisition is different: it can
block, so both adapters use a daemon worker for each client's pending acquisition.
Python preparation, locks, token acquisition, and calling-thread cleanup can
still block.
"""
from __future__ import annotations

# Coordinate application-loop futures and cancellation; no transport sleeps are used.
import asyncio  # pylint: disable=do-not-import-asyncio
import logging
import threading
from concurrent.futures import Future
from typing import TYPE_CHECKING, Any, AsyncIterator, Optional

from azure.cosmos._backend.operations import (
    OP_TO_BINDING_FUNCTION_NAME,
    get_page_binding_function_name,
)
from azure.cosmos._backend.errors import BindingProtocolError, PagePreflightError
from azure.cosmos._backend.contracts import (
    BackendResponse,
    ContainerMetadata,
    PreparedClientConfig,
    PreparedPageRequest,
    PreparedRequest,
    BackendPage,
)
from azure.cosmos._backend._binding_conversions import (
    build_backend_response, build_binding_request_from_page,
    build_container_metadata, response_exception_from_binding,
    build_backend_page, page_binding_call_arguments,
)
from azure.cosmos._backend._binding_adapter_shared import (
    BindingAdapterShared,
    _binding_error_type,
    close_credential_bridge_quietly,
    driver_transport_error_type,
    driver_unsupported_query_error_type,
    finalize_adapter_resources,
    is_credential_error,
    operation_timeout_error,
    page_binding_call_errors,
    release_driver_handle_quietly,
    validate_page_request,
)
from azure.cosmos._backend.constants import BACKEND_NAME_RUST
from azure.cosmos._backend._async_credential_bridge import AsyncTokenCredentialBridge
from azure.cosmos._backend.credentials import _is_async_credential

from azure.core.exceptions import ClientAuthenticationError, ServiceResponseError
from ..._backend.request_settings import binding_settings_contract_error
from ..._operation_deadline import remaining_timeout, run_with_deadline

from .cosmos_backend import AsyncCosmosBackend
from ..._telemetry import get_operation, log_error_diagnostics, log_response_diagnostics, record_failed_lookup
from ...runtime import CosmosRuntime

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
        "_rust module not available; AsyncBindingAdapter construction raises "
        "ImportError if the compiled Rust extension cannot be loaded."
    )

# The binding's transport error means no HTTP response was received, not that
# the service backend performed no work. Convert it without legacy replay.
_DRIVER_TRANSPORT_ERROR = driver_transport_error_type(_rust_module)
_DRIVER_RESPONSE_ERROR = _binding_error_type(_rust_module, "_DriverResponseError")
_UNSUPPORTED_QUERY_ERROR = driver_unsupported_query_error_type(_rust_module)
_REQUEST_CONTRACT_ERROR = binding_settings_contract_error(_rust_module) if _rust_module is not None else None


# Look up functions per call so tests can install a stand-in binding.
def _binding_function_for_op(op: str) -> Optional[Any]:
    """Find the async binding function that runs one operation.

    Operation name "read_item" -> binding function read_item_async.
    Return None if the operation has no mapping, the binding is absent, or the
    async function is missing. A missing export does not establish why it is absent.

    :param op: The Python wrapper's operation name, from the prepared request.
    :type op: str
    :returns: The matching async binding function, or ``None``.
    :rtype: typing.Callable or None
    """
    binding_function_name = OP_TO_BINDING_FUNCTION_NAME.get(op)
    if binding_function_name is None or _rust_module is None:
        return None
    return getattr(_rust_module, binding_function_name + "_async", None)


def _binding_function_by_name(binding_function_name: Optional[str]) -> Optional[Any]:
    """Find an async binding function the caller has already named.

    For example, "fetch_page_with_cursor" selects fetch_page_with_cursor_async.
    Callers supply the synchronous function name, without the async suffix.
    None means no matching function for this call, not that the operation has
    no paging implementation in every cursor mode.

    :param binding_function_name: A binding function name, or ``None`` if none applies.
    :type binding_function_name: str or None
    :returns: The matching async binding function, or ``None``.
    :rtype: typing.Callable or None
    """
    if binding_function_name is None or _rust_module is None:
        return None
    return getattr(_rust_module, binding_function_name + "_async", None)


class AsyncBindingAdapter(BindingAdapterShared, AsyncCosmosBackend):
    """Keep one client's settings and run its operations.

    The adapter connects to the service at the start of ``async with client:``,
    or at the first operation if ``async with`` is not used. Later operations
    reuse that connection. Closing releases only this client's hold on the
    connection. It does not affect other clients or operations still running.

    If several operations start before the client has connected, it makes only
    one connection attempt, and they all wait for it. If close is called several
    times at once, the cleanup runs once, and every caller waits for it to finish.

    A client that uses an async token credential must stay on the event loop
    where it was first used. A client that uses an account key has no such limit.
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
        settings are rejected. This constructor also sets up the fields used
        by close.
        """
        # Fields must exist even if shared validation fails and the finalizer runs.
        self._close_lock = threading.Lock()
        self._close_future: Optional[Future[None]] = None
        self._init_shared(
            endpoint, master_key, client_config, token_credential, runtime
        )

    async def initialize(self) -> None:
        """Await driver acquisition, including account setup when creating a driver."""
        operation = get_operation(self, "initialize")
        try:
            await self._ensure_driver_handle()
        except Exception as exc:
            record_failed_lookup(operation, exc, setup=True)
            raise

    def _take_driver_handle_for_close(self) -> Optional[_DriverHandle]:
        """Mark the client closed and remove its stored driver handle for release.

        :return: Detached owning driver handle, or None when no handle remains.
        :rtype: ~azure.cosmos._rust._DriverHandle or None
        """
        with self._driver_handle_lock:
            self._closing = True
            driver_handle = self._driver_handle
            self._driver_handle = None
            self._runtime = None
            return driver_handle

    async def _ensure_driver_handle(self) -> _DriverHandle:
        """Reuse the driver handle or await a worker-thread acquisition attempt.

        Each caller wraps the shared concurrent future for its customer event loop.
        Async credentials still require their original customer event loop.
        Waiting makes cancellation stop only this caller's wait, not the
        shared worker. A failed attempt can be retried; close releases late handles.

        :return: Shared owning driver handle.
        :rtype: ~azure.cosmos._rust._DriverHandle
        """
        if _REQUEST_CONTRACT_ERROR is not None:
            raise RuntimeError(_REQUEST_CONTRACT_ERROR)
        if _rust_module is None:
            raise NotImplementedError(
                "AsyncBindingAdapter: the compiled azure.cosmos._rust "
                "module is not present in this environment. Build it "
                "with `maturin develop` from the repo root."
            )
        loop = asyncio.get_running_loop()
        with self._driver_handle_lock:
            if self._closing:
                raise RuntimeError("AsyncBindingAdapter: the client is closed.")
            if isinstance(self._token_credential, AsyncTokenCredentialBridge):
                self._token_credential.check_owner_loop(loop)
            elif _is_async_credential(self._token_credential):
                self._token_credential = AsyncTokenCredentialBridge.acquire(self._token_credential, loop=loop)
            if self._driver_handle is not None:
                return self._driver_handle
            init_future = self._start_driver_acquisition(_rust_module, _LOGGER)
        waiter = asyncio.wrap_future(init_future, loop=loop)
        waiter.add_done_callback(self._driver_acquisition_finished)
        # Older asyncio versions recreate some exceptions when wrapping futures.
        # Wait without cancelling shared work, then retrieve the original result.
        await asyncio.wait((waiter,))
        return init_future.result()

    @staticmethod
    def _driver_acquisition_finished(future: "asyncio.Future[_DriverHandle]") -> None:
        """Observe this loop's result even if its caller stopped waiting.

        :param future: Event-loop future carrying the shared acquisition result.
        :type future: asyncio.Future[azure.cosmos._rust._DriverHandle]
        """
        if not future.cancelled():
            future.exception()

    async def close(self) -> None:
        """Release this client's driver acquisition and async credential bridge use.

        Cleanup normally uses the event loop's default Python thread pool and
        starts at most once. Callers on different loops share _close_future;
        cancelling one caller stops its wait, not cleanup.

        If submission fails or the worker job fails or is cancelled, the
        calling thread attempts cleanup and may block the event loop.
        Cleanup helpers log ordinary release errors; escaping errors are
        stored in _close_future for waiting callers, not retried.
        The customer app still owns and closes its token credential.
        """
        loop = asyncio.get_running_loop()
        with self._close_lock:
            close_future = self._close_future
            if close_future is None:
                driver_handle = self._take_driver_handle_for_close()
                credential = self._take_token_credential_for_close()
                pending_close_future: Future[None] = Future()
                self._close_future = close_future = pending_close_future
                teardown_lock = threading.Lock()

                def teardown() -> None:
                    # Submission can queue the job before raising; calling-thread cleanup must not release twice.
                    with teardown_lock:
                        if pending_close_future.running() or pending_close_future.done():
                            return
                        if not pending_close_future.set_running_or_notify_cancel():
                            return
                    try:
                        try:
                            close_credential_bridge_quietly(credential)
                        finally:
                            if driver_handle is not None:
                                release_driver_handle_quietly(driver_handle, _rust_module)
                    # Every worker failure must settle the future shared by close callers.
                    except BaseException as error:  # pylint: disable=broad-exception-caught
                        pending_close_future.set_exception(error)
                    else:
                        pending_close_future.set_result(None)

                if driver_handle is None and credential is None:
                    pending_close_future.set_result(None)
                else:
                    def worker_finished(worker_future: asyncio.Future[None]) -> None:
                        error = None if worker_future.cancelled() else worker_future.exception()
                        if not worker_future.cancelled() and error is None:
                            return
                        _LOGGER.warning(
                            "Background client cleanup did not complete; cleaning up on the calling thread",
                            exc_info=(type(error), error, error.__traceback__) if error is not None else None,
                        )
                        teardown()

                    try:
                        worker_future = loop.run_in_executor(None, teardown)
                        worker_future.add_done_callback(worker_finished)
                    except Exception:  # pylint: disable=broad-except
                        _LOGGER.warning(
                            "Could not start background client cleanup; cleaning up on the calling thread",
                            exc_info=True,
                        )
                        teardown()

        if close_future.done():
            close_future.result()
            return
        # Each loop gets its own awaitable; cancellation must not cancel _close_future.
        close_wait = asyncio.wrap_future(close_future)
        try:
            await asyncio.shield(close_wait)
        except asyncio.CancelledError:
            def observe_cleanup_result(future: "asyncio.Future[None]") -> None:
                # Observe errors after this caller leaves; later close calls still receive them.
                if not future.cancelled() and future.exception() is not None:
                    _LOGGER.debug("Async client cleanup failed after its close wait was cancelled")

            close_wait.add_done_callback(observe_cleanup_result)
            raise

    def __del__(self) -> None:
        """Hand abandoned resources to the cleanup helper without raising.

        Same last-resort cleanup as BindingAdapter.__del__; an awaited close()
        remains the normal path.
        """
        try:
            credential = self._take_token_credential_for_close()
            driver_handle = self._take_driver_handle_for_close()
            finalize_adapter_resources(credential, driver_handle, _rust_module)
        except Exception:  # pylint: disable=broad-except
            # Never raise from object finalization.
            pass

    async def execute(
        self, prepared: PreparedRequest, *, deadline: Optional[float] = None
    ) -> BackendResponse:
        """Execute one prepared request and return a backend response.

        Same function selection and error translation as the synchronous
        ``BindingAdapter.execute``, with one difference: the ``_async`` binding
        function is called on the calling thread and its returned awaitable is
        awaited rather than waiting synchronously for its result.

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
                "AsyncBindingAdapter.execute: the compiled "
                "azure.cosmos._rust module is not present in this "
                "environment. Install an azure-cosmos wheel built for this "
                "operating system, processor, and Python version, or rebuild "
                "the extension from the current source.",
                name="azure.cosmos._rust",
            )

        # Resolve the operation name to an async binding function before acquisition.
        binding_function = _binding_function_for_op(prepared.op)
        if not callable(binding_function):
            binding_name = OP_TO_BINDING_FUNCTION_NAME.get(prepared.op)
            if binding_name is not None:
                raise RuntimeError(
                    f"The compiled azure.cosmos._rust extension does not export a callable {binding_name}_async; "
                    "install a matching azure-cosmos wheel or rebuild the extension from the current source."
                )
            raise NotImplementedError("AsyncBindingAdapter.execute does not yet support op={!r}.".format(prepared.op))
        operation = get_operation(self, prepared.op)
        contribution = operation.begin_contribution() if operation is not None else None
        # Bound this caller's wait, not the shielded acquisition shared with other callers.
        try:
            driver_handle = await run_with_deadline(self._ensure_driver_handle, deadline)
        except Exception as exc:
            if contribution is not None:
                contribution.setup_error(exc)
            log_error_diagnostics(self, exc, prepared.op)
            raise
        # Record the selected binding function, not successful execution or
        # service I/O. Omit the internal owning handle.
        _LOGGER.debug(
            "cosmos backend=%s op=%s binding_function=%s_async",
            BACKEND_NAME_RUST,
            prepared.op,
            OP_TO_BINDING_FUNCTION_NAME.get(prepared.op),
        )
        result = await self._call_operation(binding_function, driver_handle, prepared, deadline, contribution)
        if result is None:
            raise BindingProtocolError(f"The binding returned no response for {prepared.op!r}")
        if contribution is not None:
            result = contribution.response(result)
        response = build_backend_response(*result)
        log_response_diagnostics(self, prepared.op, response)
        return response

    async def _call_operation(
        self,
        binding_function: Any,
        driver_handle: _DriverHandle,
        prepared: PreparedRequest,
        deadline: Optional[float],
        contribution: Any,
    ) -> Any:
        """Await the selected binding export and translate operation failures.

        :param binding_function: Callable async export validated before driver acquisition.
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
        # Call the binding function and await its result, without a Python executor
        # job for service I/O. Translate response-less errors to ServiceResponseError,
        # without assuming no request was sent or invoking legacy retry policies.
        try:
            binding_kwargs: dict[str, Any] = {}
            if deadline is not None:
                binding_kwargs["timeout_seconds"] = remaining_timeout(deadline)
            if contribution is not None:
                binding_kwargs["include_attempts"] = True
            result = await binding_function(driver_handle, prepared, **binding_kwargs)
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
        return result

    async def get_container_metadata(
        self, container_link: str, *, deadline: Optional[float] = None, op: Optional[str] = None
    ) -> ContainerMetadata:
        """Obtain container properties needed to prepare an item operation.

        Same result and ``op`` handling as the synchronous
        ``BindingAdapter.get_container_metadata``, with one difference: the
        ``_async`` binding function is awaited.

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
                "AsyncBindingAdapter.get_container_metadata: the compiled "
                "azure.cosmos._rust module is not present in this environment."
            )
        binding_function = getattr(_rust_module, "get_container_metadata_async", None)
        if binding_function is None:
            raise NotImplementedError("The Rust binding does not expose get_container_metadata_async")
        operation = get_operation(self, op) if op is not None else None
        try:
            driver_handle = await run_with_deadline(self._ensure_driver_handle, deadline)
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
            result = await binding_function(driver_handle, container_link, **binding_kwargs)
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
        return build_container_metadata(result)

    # An async generator implements the base method's synchronous AsyncIterator-returning contract.
    async def execute_pages(  # pylint: disable=invalid-overridden-method
        self, prepared: PreparedPageRequest, *, deadline: Optional[float] = None
    ) -> AsyncIterator[BackendPage]:
        """Yield one backend page when the caller advances this async generator.

        PreparedPageRequest -> PreparedRequest -> async binding call with an
        optional feed cursor -> response tuple -> BackendResponse -> BackendPage.
        The caller uses async for or awaits __anext__(); this method does not
        fetch all subsequent pages itself.

        :param prepared: Inputs and optional retained cursor for one page fetch.
        :type prepared: ~azure.cosmos._backend.contracts.PreparedPageRequest
        :keyword deadline: Absolute monotonic deadline, or None to derive a budget from settings.
        :paramtype deadline: float or None
        :return: Asynchronous iterator yielding one backend page.
        :rtype: typing.AsyncIterator[azure.cosmos._backend.contracts.BackendPage]
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
            driver_handle = await run_with_deadline(self._ensure_driver_handle, deadline)
        except Exception as exc:
            if contribution is not None:
                contribution.setup_error(exc)
            log_error_diagnostics(self, exc, prepared.op)
            raise
        binding_request = self._with_client_headers(build_binding_request_from_page(prepared))
        _LOGGER.debug(
            "cosmos backend=%s op=%s binding_function=%s_async",
            BACKEND_NAME_RUST,
            prepared.op,
            binding_function_name,
        )
        with page_binding_call_errors(deadline, _UNSUPPORTED_QUERY_ERROR, _DRIVER_TRANSPORT_ERROR):
            args, kwargs = page_binding_call_arguments(driver_handle, binding_request, prepared, deadline)
            if contribution is not None:
                kwargs["include_attempts"] = True
            try:
                result = await binding_function(*args, **kwargs)
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
        """Perform page preflight before acquiring a driver handle or fetching results.

        Same checks as the synchronous ``BindingAdapter.validate_page_request``,
        with one difference: it requires the ``_async`` form of each binding
        function.

        :param prepared: Page request whose operation and cursor mode require validation.
        :type prepared: ~azure.cosmos._backend.contracts.PreparedPageRequest
        """
        validate_page_request(prepared, _rust_module, _binding_function_by_name, "AsyncBindingAdapter", "_async")

    def create_item_feed_cursor(self) -> _ItemFeedCursor:
        """Create an empty feed cursor retained by one page iterator.

        Same as the synchronous ``BindingAdapter.create_item_feed_cursor``:
        call the binding's cursor constructor synchronously, without acquiring
        a driver handle or fetching a page.

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
