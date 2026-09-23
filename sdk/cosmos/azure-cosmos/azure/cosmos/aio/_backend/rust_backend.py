# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Execute asynchronous requests through the binding and convert its results.

Like the synchronous RustBackend, this is Python wrapper code. It acquires a
driver handle identifying a CosmosDriver retained by the binding, then passes
prepared requests through azure.cosmos._rust.

For an order read, the sequence is:

    PreparedRequest -> call read_item_async on the calling thread
    -> await the binding result -> convert its tuple to BackendResponse

The binding runs Rust work with the Tokio runtime; service I/O does not use
a Python executor worker per request. Driver acquisition is different: it can
block, so _ensure_driver_handle submits it to a worker thread. Python preparation,
locks, token acquisition, and calling-thread cleanup can still block.
"""
from __future__ import annotations
from ..._backend.request_settings import binding_settings_contract_error

import asyncio
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
    build_container_metadata, metadata_exception_from_binding,
    build_backend_page, page_binding_call_arguments,
)
from azure.cosmos._backend._rust_backend_shared import (
    RustBackendShared,
    _binding_error_type,
    close_credential_bridge_quietly,
    driver_transport_error_type,
    driver_unsupported_query_error_type,
    finalize_backend_resources,
    page_binding_call_errors,
    validate_page_request,
)
from azure.cosmos._backend.constants import BACKEND_NAME_RUST

from azure.core.exceptions import ServiceResponseError
from ..._operation_deadline import remaining_timeout
from ...exceptions import CosmosClientTimeoutError

from .cosmos_backend import AsyncCosmosBackend

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
        "_rust module not available; AsyncRustBackend operations "
        "will raise NotImplementedError until the Rust module is built."
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
    :returns: The matching async binding function, or ``None``.
    """
    binding_function_name = OP_TO_BINDING_FUNCTION_NAME.get(op)
    if binding_function_name is None or _rust_module is None:
        return None
    return getattr(_rust_module, binding_function_name + "_async", None)


def _binding_function_by_name(binding_function_name: Optional[str]) -> Optional[Any]:
    """Find an async binding function the caller has already named.

    For example, "fetch_page_with_cursor" selects fetch_page_with_cursor_async.
    Callers supply the same unsuffixed function name as on the synchronous path.
    None means no matching function for this call, not that the operation has
    no paging implementation in every cursor mode.

    :param binding_function_name: A binding function name, or ``None`` if none applies.
    :returns: The matching async binding function, or ``None``.
    """
    if binding_function_name is None or _rust_module is None:
        return None
    return getattr(_rust_module, binding_function_name + "_async", None)


def _close_driver_handle_quietly(driver_handle: str) -> None:
    """Release one driver-handle acquisition when the binding export is available.

    Log raised cleanup errors without exposing the handle. Other clients and
    in-flight operations can keep the CosmosDriver alive after this release.
    """
    if _rust_module is None:
        return
    release_driver_handle = getattr(_rust_module, "release_driver_handle", None)
    if release_driver_handle is None:
        return
    try:
        release_driver_handle(driver_handle)
    except Exception:  # pylint: disable=broad-except
        # Binding exception text can contain the handle too.
        _LOGGER.debug("Failed releasing the driver handle")


class AsyncRustBackend(RustBackendShared, AsyncCosmosBackend):
    """Retain one client's settings and execute its prepared requests.

    As with RustBackend, the driver handle identifies a CosmosDriver retained
    by the binding. First use acquires a handle; later calls reuse it. Closing
    releases this client's acquisition, not another client's or an in-flight
    operation's reference.

    Same-loop callers can share an acquisition attempt. Worker jobs from
    different loops take turns acquiring or reusing the stored handle.
    Close callers share _close_future; each loop uses its own awaitable for
    that shared result.
    """

    name = BACKEND_NAME_RUST

    def __init__(
        self,
        endpoint: str,
        master_key: Optional[str] = None,
        client_config: Optional[PreparedClientConfig] = None,
        token_credential: Optional[Any] = None,
    ) -> None:
        """Store inputs and check CosmosDriverRuntime settings without acquiring a driver handle.

        RustBackendShared performs the same setup as for RustBackend, including
        checking completed CosmosDriverRuntime initialization. This constructor
        also creates locks and empty future fields. Acquisition and close create
        their futures later; construction does not reserve CosmosDriverRuntime settings.
        """
        # Fields must exist even if shared validation fails and the finalizer runs.
        # _driver_acquisition_lock allows one acquisition attempt at a time.
        # A successfully acquired handle is reused; failed attempts can run again.
        # Acquisition does not hold _driver_handle_lock, so close can mark the
        # Python backend closed without waiting for that call to finish.
        self._driver_acquisition_lock = threading.Lock()
        self._close_lock = threading.Lock()
        self._close_future: Optional[Future[None]] = None
        # Same-loop callers share _init_future while an acquisition attempt runs.
        # Different loops may submit separate acquisition jobs that take turns.
        self._init_future: Optional["asyncio.Future[str]"] = None
        self._init_future_loop: Optional[asyncio.AbstractEventLoop] = None
        self._init_shared(
            endpoint, master_key, client_config, token_credential
        )

    def _acquire_driver_handle(self) -> str:
        """Return the stored driver handle or acquire one through the binding.

        This runs on a worker thread. Acquisition may reuse a CosmosDriver from
        the binding's driver cache; it does not necessarily create a new object.
        If close wins before the handle is stored, release that acquisition here.
        """
        # Only one worker at a time acquires a handle, without holding
        # _driver_handle_lock during the binding call. If close wins before
        # the handle is stored, release the new acquisition here.
        if _rust_module is None:
            raise NotImplementedError(
                "AsyncRustBackend: the compiled azure.cosmos._rust "
                "module is not present in this environment. Build it "
                "with `maturin develop` from the repo root."
            )
        surplus_driver_handle: Optional[str] = None
        with self._driver_acquisition_lock:
            with self._driver_handle_lock:
                if self._closing:
                    raise RuntimeError("AsyncRustBackend: the client is closed.")
                if self._driver_handle is not None:
                    return self._driver_handle
            new_driver_handle: Optional[str] = self._initialize_driver(_rust_module)
            with self._driver_handle_lock:
                if self._closing:
                    surplus_driver_handle, new_driver_handle = new_driver_handle, None
                else:
                    self._driver_handle = new_driver_handle
        if surplus_driver_handle is not None:
            _close_driver_handle_quietly(surplus_driver_handle)
        if new_driver_handle is None:
            raise RuntimeError(
                "AsyncRustBackend: the client was closed during initialization."
            )
        return new_driver_handle

    def _take_driver_handle_for_close(self) -> Optional[str]:
        """Mark the client closed and remove its stored driver handle for release."""
        with self._driver_handle_lock:
            self._closing = True
            driver_handle = self._driver_handle
            self._driver_handle = None
            return driver_handle

    async def _ensure_driver_handle(self) -> str:
        """Reuse the driver handle or await a worker-thread acquisition attempt.

        Same-loop callers can share _init_future. Different loops can
        submit separate jobs; _driver_acquisition_lock makes them take turns.
        Each job rechecks the stored handle before acquiring one through the
        binding. A failed attempt can be retried on a later call.
        Shielding prevents a waiter's cancellation from cancelling that shared
        future. It does not cancel the worker job or release its eventual handle;
        acquisition and close coordinate that ownership separately.
        """
        if _REQUEST_CONTRACT_ERROR is not None:
            raise RuntimeError(_REQUEST_CONTRACT_ERROR)
        loop = asyncio.get_running_loop()
        with self._driver_handle_lock:
            if self._closing:
                raise RuntimeError("AsyncRustBackend: the client is closed.")
            if self._driver_handle is not None:
                return self._driver_handle
            init_future = self._init_future
            if init_future is None or self._init_future_loop is not loop:
                init_future = loop.run_in_executor(None, self._acquire_driver_handle)
                self._init_future = init_future
                self._init_future_loop = loop
                init_future.add_done_callback(self._driver_acquisition_finished)
        return await asyncio.shield(init_future)

    def _driver_acquisition_finished(self, future: "asyncio.Future[str]") -> None:
        """Clear this attempt's stored future and observe any unawaited error."""
        with self._driver_handle_lock:
            if self._init_future is future:
                self._init_future = None
                self._init_future_loop = None
        # Observe failures even when every waiter was cancelled; active waiters
        # still receive the original exception through their shielded await.
        if not future.cancelled() and future.exception() is not None:
            _LOGGER.debug("Rust driver initialization failed")

    async def close(self) -> None:
        """Release this client's driver acquisition and async credential bridge use.

        Same release rules as the synchronous ``RustBackend.close``, with one
        difference: cleanup normally runs on a worker thread. Each caller
        waits for the result recorded in _close_future through an awaitable
        for its own event loop. Cancelling one caller stops its wait but not
        the cleanup. Later callers wait for that same result.

        Caller A starts close -> _close_future records the shared result.
        Caller B awaits that same result through an awaitable for B's event loop.
        Neither caller closes the customer app's token credential.

        If background cleanup fails to start or complete successfully, cleanup
        also runs on the calling thread. A lock prevents duplicate release.
        Close is therefore not unconditionally nonblocking.
        """
        loop = asyncio.get_running_loop()
        with self._close_lock:
            close_future = self._close_future
            if close_future is None:
                with self._driver_handle_lock:
                    self._closing = True
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
                                _close_driver_handle_quietly(driver_handle)
                    except BaseException as error:
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
        await asyncio.shield(asyncio.wrap_future(close_future))

    def __del__(self) -> None:
        """Hand abandoned resources to the cleanup helper without raising.

        Same last-resort cleanup as RustBackend.__del__; an awaited close()
        remains the normal path.
        """
        try:
            credential = self._take_token_credential_for_close()
            driver_handle = self._take_driver_handle_for_close()
            finalize_backend_resources(credential, driver_handle, _rust_module)
        except Exception:  # pylint: disable=broad-except
            # Never raise from object finalization.
            pass

    async def execute(
        self, prepared: PreparedRequest, *, deadline: Optional[float] = None
    ) -> BackendResponse:
        """Execute one prepared request and return a backend response.

        Same function selection and error translation as the synchronous
        ``RustBackend.execute``, with one difference: the ``_async`` binding
        function is called on the calling thread and its returned awaitable is
        awaited rather than waiting synchronously for its result.
        """
        if not isinstance(prepared, PreparedRequest):
            raise TypeError("execute requires a PreparedRequest")
        if _rust_module is None:
            raise NotImplementedError(
                "AsyncRustBackend.execute: the compiled "
                "azure.cosmos._rust module is not present in this "
                "environment. Build it with `maturin develop` from "
                "the repo root."
            )

        # Resolve the operation name to an async binding function before acquisition.
        binding_function = _binding_function_for_op(prepared.op)
        if binding_function is None:
            raise NotImplementedError(
                "AsyncRustBackend.execute does not yet support op={!r}.".format(prepared.op)
            )
        driver_handle = await self._ensure_driver_handle()
        # Record the selected binding function, not successful execution or
        # service I/O. Omit the credential-bearing handle.
        _LOGGER.debug(
            "cosmos backend=%s op=%s binding_function=%s_async",
            BACKEND_NAME_RUST,
            prepared.op,
            OP_TO_BINDING_FUNCTION_NAME.get(prepared.op),
        )
        # Call the binding function and await its result, without a Python executor
        # job for service I/O. Translate response-less errors to ServiceResponseError,
        # without assuming no request was sent or invoking legacy retry policies.
        try:
            result = (
                await binding_function(driver_handle, prepared)
                if deadline is None
                else await binding_function(driver_handle, prepared, timeout_seconds=remaining_timeout(deadline))
            )
        except TimeoutError as exc:
            if deadline is None:
                raise
            raise CosmosClientTimeoutError(error=exc) from exc
        except _DRIVER_TRANSPORT_ERROR as exc:
            raise ServiceResponseError(message=str(exc)) from exc
        except _DRIVER_RESPONSE_ERROR as exc:
            raise metadata_exception_from_binding(exc) from exc
        if result is None:
            raise BindingProtocolError(f"The binding returned no response for {prepared.op!r}")
        return build_backend_response(*result)

    async def get_container_metadata(
        self, container_link: str, *, deadline: Optional[float] = None
    ) -> ContainerMetadata:
        """Obtain container properties needed to prepare an item operation.

        Same result as the synchronous ``RustBackend.get_container_metadata``,
        with one difference: the ``_async`` binding function is awaited.
        """
        if _rust_module is None:
            raise NotImplementedError(
                "AsyncRustBackend.get_container_metadata: the compiled "
                "azure.cosmos._rust module is not present in this environment."
            )
        binding_function = getattr(_rust_module, "get_container_metadata_async", None)
        if binding_function is None:
            raise NotImplementedError("The Rust binding does not expose get_container_metadata_async")
        driver_handle = await self._ensure_driver_handle()
        try:
            result = (
                await binding_function(driver_handle, container_link)
                if deadline is None
                else await binding_function(driver_handle, container_link, timeout_seconds=remaining_timeout(deadline))
            )
        except TimeoutError as exc:
            if deadline is None:
                raise
            raise CosmosClientTimeoutError(error=exc) from exc
        except _DRIVER_TRANSPORT_ERROR as exc:
            raise ServiceResponseError(message=str(exc)) from exc
        except _DRIVER_RESPONSE_ERROR as exc:
            raise metadata_exception_from_binding(exc) from exc
        return build_container_metadata(result)

    async def execute_pages(
        self, prepared: PreparedPageRequest, *, deadline: Optional[float] = None
    ) -> AsyncIterator[BackendPage]:
        """Yield one backend page when the caller advances this async generator.

        PreparedPageRequest -> PreparedRequest -> async binding call with an
        optional feed cursor -> response tuple -> BackendResponse -> BackendPage.
        The caller uses async for or awaits __anext__(); this method does not
        fetch all subsequent pages itself.
        """
        self.validate_page_request(prepared)
        binding_function_name = get_page_binding_function_name(
            prepared.op, uses_cursor=prepared.cursor is not None
        )
        binding_function = _binding_function_by_name(binding_function_name)
        if binding_function is None:
            raise BindingProtocolError("Validated page binding function is no longer available")
        driver_handle = await self._ensure_driver_handle()
        binding_request = build_binding_request_from_page(prepared)
        _LOGGER.debug(
            "cosmos backend=%s op=%s binding_function=%s_async",
            BACKEND_NAME_RUST,
            prepared.op,
            binding_function_name,
        )
        with page_binding_call_errors(deadline, _UNSUPPORTED_QUERY_ERROR, _DRIVER_TRANSPORT_ERROR):
            args, kwargs = page_binding_call_arguments(driver_handle, binding_request, prepared, deadline)
            result = await binding_function(*args, **kwargs)
            response = build_backend_response(*result)
        yield build_backend_page(prepared, response)

    def validate_page_request(self, prepared: PreparedPageRequest) -> None:
        """Perform page preflight before acquiring a driver handle or fetching results.

        Same checks as the synchronous ``RustBackend.validate_page_request``,
        with one difference: it requires the ``_async`` form of each binding
        function.
        """
        validate_page_request(prepared, _rust_module, _binding_function_by_name, "AsyncRustBackend", "_async")

    def create_item_feed_cursor(self) -> _ItemFeedCursor:
        """Create an empty feed cursor retained by one page iterator.

        Same as the synchronous ``RustBackend.create_item_feed_cursor``:
        call the binding's cursor constructor synchronously, without acquiring
        a driver handle or fetching a page.
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
