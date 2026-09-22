# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Execute asynchronous requests through the compiled Python/Rust binding.

Like the synchronous RustBackend, this is Python wrapper code. It acquires a
driver handle identifying a CosmosDriver retained by the binding, then passes
prepared requests through azure.cosmos._rust.

What differs here is when work leaves the calling thread:

- Binding functions are awaited rather than run in a Python executor per request.
  Python preparation, result conversion, and credential callbacks still run
  Python code; token acquisition can involve additional threads.
- Building the handle the first time still blocks, so it is pushed to a
  background thread. AsyncRustBackend._ensure_driver_handle covers the rest.
- Closing normally offloads teardown and shields the shared close future from
  caller cancellation. If submission fails, cleanup can run on the calling thread.
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

# The binding's response-less transport error, captured once at load. A driver
# op that fails before any wire response raises this; we re-raise it as
# azure-core's ServiceResponseError (see driver_transport_error_type).
_DRIVER_TRANSPORT_ERROR = driver_transport_error_type(_rust_module)
_DRIVER_RESPONSE_ERROR = _binding_error_type(_rust_module, "_DriverResponseError")
_UNSUPPORTED_QUERY_ERROR = driver_unsupported_query_error_type(_rust_module)
_REQUEST_CONTRACT_ERROR = binding_settings_contract_error(_rust_module) if _rust_module is not None else None


# Looked up per call, not cached at import, so tests can install a stand-in
# binding. One getattr costs nothing against a network round trip.
def _binding_function_for_op(op: str) -> Optional[Any]:
    """Find the async binding function that runs one operation.

    Same mapping and same meaning of ``None`` as the sync counterpart in
    ``azure.cosmos._backend.rust_backend``, with one difference: this looks up
    the ``_async`` name, so a binding that exports only the sync form reads
    here as "too old to export this operation".

    :param op: The Python wrapper's operation name, from the prepared request.
    :returns: The matching async binding function, or ``None``.
    """
    binding_function_name = OP_TO_BINDING_FUNCTION_NAME.get(op)
    if binding_function_name is None or _rust_module is None:
        return None
    return getattr(_rust_module, binding_function_name + "_async", None)


def _binding_function_by_name(binding_function_name: Optional[str]) -> Optional[Any]:
    """Find an async binding function the caller has already named.

    Same role and same meaning of ``None`` as the sync counterpart in
    ``azure.cosmos._backend.rust_backend``, with one difference: the function name is
    the sync name and the ``_async`` suffix is appended here, so callers pass
    the same name on both paths.

    :param binding_function_name: A binding function name, or ``None`` if none applies.
    :returns: The matching async binding function, or ``None``.
    """
    if binding_function_name is None or _rust_module is None:
        return None
    return getattr(_rust_module, binding_function_name + "_async", None)


def _close_driver_handle_quietly(driver_handle: str) -> None:
    """Release one driver handle, logging cleanup failures.

    Other clients and operations can keep the driver alive after this release.
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

    Driver handles work exactly as on the synchronous RustBackend: a handle is
    a string identifying a CosmosDriver retained by the binding, this backend
    acquires one on first use and reuses it, and closing releases only this
    client's acquisition. Clients with matching account, credential, and
    configuration can share a CosmosDriver, so an operation still running can
    keep one alive after the last client closes.

    Two differences follow from being asynchronous:

    - The Python wrapper calls an async binding function on the calling thread,
      then awaits its returned awaitable. Service I/O does not occupy a Python
      executor worker.
      Token acquisition, Python preparation, locks, and the cleanup fallback
      can still block, so concurrency is not set by the connection pool alone.
    - Acquiring the first handle blocks, so it runs on a worker thread.
      Callers on one or more event loops share that single acquisition, and
      share a single close.
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

        Same stored inputs as the synchronous ``RustBackend.__init__``, with
        one difference: this also creates the locks and futures that let
        callers on one or more event loops share a single handle acquisition
        and a single close.
        """
        # Fields must exist even if shared validation fails and the finalizer runs.
        # _build_lock serializes acquisition attempts across loops. Successful
        # initialization is reused; failed attempts can run again. Handle
        # acquisition does not hold _driver_handle_lock, so close can mark the
        # backend closed without waiting for that call to finish.
        self._build_lock = threading.Lock()
        self._close_lock = threading.Lock()
        self._close_future: Optional[Future[None]] = None
        # When many operations start at once on a fresh client they all need the
        # handle. These hold the one running build so they share it instead of each
        # starting their own on the same loop (see _ensure_driver_handle).
        # Callers on different loops may submit separate serialized build jobs.
        self._init_future: Optional["asyncio.Future[str]"] = None
        self._init_future_loop: Optional[asyncio.AbstractEventLoop] = None
        self._init_shared(
            endpoint, master_key, client_config, token_credential
        )

    def _build_driver_handle(self) -> str:
        """Create or share the Rust driver handle on a worker thread."""
        # Handle acquisition can block, so it runs on a worker. _build_lock
        # serializes attempts without holding the handle-state lock. If close
        # wins before publication, release the newly acquired handle here.
        if _rust_module is None:
            raise NotImplementedError(
                "AsyncRustBackend: the compiled azure.cosmos._rust "
                "module is not present in this environment. Build it "
                "with `maturin develop` from the repo root."
            )
        surplus_driver_handle: Optional[str] = None
        with self._build_lock:
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
        """Mark the client closed and remove its current Rust handle."""
        with self._driver_handle_lock:
            self._closing = True
            driver_handle = self._driver_handle
            self._driver_handle = None
            return driver_handle

    async def _ensure_driver_handle(self) -> str:
        """Reuse the handle or await a worker-thread initialization attempt.

        Same-loop callers can share the stored future. Different loops can
        submit separate jobs; ``_build_lock`` serializes their handle acquisition
        and rechecks the handle. A failed attempt can be retried on a later call.
        Cancelling an await does not necessarily stop its executor job.
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
                init_future = loop.run_in_executor(None, self._build_driver_handle)
                self._init_future = init_future
                self._init_future_loop = loop
                init_future.add_done_callback(self._driver_initialization_finished)
        return await asyncio.shield(init_future)

    def _driver_initialization_finished(self, future: "asyncio.Future[str]") -> None:
        with self._driver_handle_lock:
            if self._init_future is future:
                self._init_future = None
                self._init_future_loop = None
        # Observe failures even when every waiter was cancelled; active waiters
        # still receive the original exception through their shielded await.
        if not future.cancelled() and future.exception() is not None:
            _LOGGER.debug("Rust driver initialization failed")

    async def close(self) -> None:
        """Release this client's resources without closing another client's driver.

        Same release rules as the synchronous ``RustBackend.close``, with one
        difference: teardown normally runs on a worker thread and every caller
        awaits the same shared close future, so cancelling one caller stops
        its wait but not the cleanup. Later callers, including callers on
        another event loop, wait on that same future.

        If background cleanup cannot start or finish, the fallback runs on the
        calling thread. Cleanup is therefore not unconditionally nonblocking.
        """
        loop = asyncio.get_running_loop()
        with self._close_lock:
            completion = self._close_future
            if completion is None:
                with self._driver_handle_lock:
                    self._closing = True
                driver_handle = self._take_driver_handle_for_close()
                credential = self._take_token_credential_for_close()
                pending_close: Future[None] = Future()
                self._close_future = completion = pending_close
                teardown_lock = threading.Lock()

                def teardown() -> None:
                    # Submission can queue the job before raising; the fallback must not release it twice.
                    with teardown_lock:
                        if pending_close.running() or pending_close.done():
                            return
                        if not pending_close.set_running_or_notify_cancel():
                            return
                    try:
                        try:
                            close_credential_bridge_quietly(credential)
                        finally:
                            if driver_handle is not None:
                                _close_driver_handle_quietly(driver_handle)
                    except BaseException as error:
                        pending_close.set_exception(error)
                    else:
                        pending_close.set_result(None)

                if driver_handle is None and credential is None:
                    pending_close.set_result(None)
                else:
                    def worker_finished(work: asyncio.Future[None]) -> None:
                        error = None if work.cancelled() else work.exception()
                        if not work.cancelled() and error is None:
                            return
                        _LOGGER.warning(
                            "Background client cleanup did not complete; cleaning up on the calling thread",
                            exc_info=(type(error), error, error.__traceback__) if error is not None else None,
                        )
                        teardown()

                    try:
                        work = loop.run_in_executor(None, teardown)
                        work.add_done_callback(worker_finished)
                    except Exception:  # pylint: disable=broad-except
                        _LOGGER.warning(
                            "Could not start background client cleanup; cleaning up on the calling thread",
                            exc_info=True,
                        )
                        teardown()

        if completion.done():
            completion.result()
            return
        # Each loop gets its own awaitable; cancelling it must not cancel the shared work.
        await asyncio.shield(asyncio.wrap_future(completion))

    def __del__(self) -> None:
        """Hand abandoned resources to the cleanup helper without raising.

        Same fallback as the synchronous ``RustBackend.__del__``; explicit
        ``close`` remains the normal path.
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
        """Send one prepared operation and return a BackendResponse.

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

        # Look up the binding's _async function for this op; None if unsupported.
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
        # Await the binding function directly rather than allocating an executor
        # job for its I/O. Translate response-less errors to ServiceResponseError,
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
        """Yield one page when the caller iterates this async generator.

        Same page selection as the synchronous ``RustBackend.execute_pages``,
        with one difference: the chosen binding function is awaited, and the
        caller iterates with ``async for``.
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
        """Check page support before acquiring a driver or fetching results.

        Same checks as the synchronous ``RustBackend.validate_page_request``,
        with one difference: it requires the ``_async`` form of each binding
        function.
        """
        validate_page_request(prepared, _rust_module, _binding_function_by_name, "AsyncRustBackend", "_async")

    def create_item_feed_cursor(self) -> _ItemFeedCursor:
        """Create an empty feed cursor retained by one page iterator.

        Same as the synchronous ``RustBackend.create_item_feed_cursor``:
        call the binding's cursor constructor synchronously, without acquiring
        a driver handle or fetching a page. There is no asynchronous difference.
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
