# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Async backend that sends operations to the rust driver through the compiled binding.

The sync version in azure/cosmos/_backend/binding.py defines the three terms
used throughout this layer -- binding, rust driver, driver handle -- and
explains why the import of the compiled module is guarded. Read it first.

What differs here is when work leaves the calling thread:

- Native I/O is awaited rather than run in a Python executor per request.
  Python preparation, result conversion, and credential callbacks still run
  Python code; token acquisition can involve additional threads.
- Building the handle the first time still blocks, so it is pushed to a
  background thread. AsyncRustBinding._ensure_driver_handle covers the rest.
- Closing normally offloads teardown and shields the shared completion from
  caller cancellation. If submission fails, cleanup can run on the calling thread.
"""
from __future__ import annotations
from ..._backend.request_settings import native_settings_contract_error

import asyncio
import logging
import threading
from concurrent.futures import Future
from typing import TYPE_CHECKING, Any, AsyncIterator, Optional

from azure.cosmos._backend.operations import (
    OP_TO_BINDING_METHOD,
    get_page_binding_method,
)
from azure.cosmos._backend.errors import BindingProtocolError, PagePreflightError
from azure.cosmos._backend.contracts import (
    BackendResponse,
    ContainerMetadata,
    PreparedClientConfig,
    PreparedQuery,
    PreparedRequest,
    QueryPage,
)
from azure.cosmos._backend._binding_conversions import (
    build_backend_response, build_binding_request_from_page,
    build_container_metadata, metadata_exception_from_binding,
    build_query_page, page_dispatch_arguments,
)
from azure.cosmos._backend._shared import (
    RustBindingShared,
    _binding_error_type,
    close_credential_bridge_quietly,
    driver_transport_error_type,
    driver_unsupported_query_error_type,
    page_dispatch_errors,
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

# Imported once when this module loads; not changed afterwards.
_rust_module: Optional[Any] = None
try:
    from azure.cosmos import _rust  # type: ignore[attr-defined]
    _rust_module = _rust
except ImportError:
    _LOGGER.debug(
        "_rust module not available; AsyncRustBinding operations "
        "will raise NotImplementedError until the Rust module is built."
    )

# The binding's response-less transport error, captured once at load. A driver
# op that fails before any wire response raises this; we re-raise it as
# azure-core's ServiceResponseError (see driver_transport_error_type).
_DRIVER_TRANSPORT_ERROR = driver_transport_error_type(_rust_module)
_DRIVER_RESPONSE_ERROR = _binding_error_type(_rust_module, "_DriverResponseError")
_UNSUPPORTED_QUERY_ERROR = driver_unsupported_query_error_type(_rust_module)
_native_runtime_module = _rust_module
_REQUEST_CONTRACT_ERROR = native_settings_contract_error(_rust_module) if _rust_module is not None else None


# Look up the binding's ``<op>_async`` function for an operation. Read live from
# ``_rust_module`` rather than cached at import, so the tests can swap in a fake
# binding; the extra getattr per call is tiny next to the network round trip.
def _get_binding_function(op: str) -> Optional[Any]:
    """Return the binding's ``<op>_async`` function, or ``None`` if the op is
    unsupported or the compiled module is absent."""
    method = OP_TO_BINDING_METHOD.get(op)
    if method is None or _rust_module is None:
        return None
    return getattr(_rust_module, method + "_async", None)


def _get_page_dispatch(method: Optional[str]) -> Optional[Any]:
    """Look up the selected async page binding without changing execution mode."""
    if method is None or _rust_module is None:
        return None
    return getattr(_rust_module, method + "_async", None)


def _close_driver_handle_quietly(driver_handle: str) -> None:
    """Release one native driver reference, logging cleanup failures.

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
        # Native exception text can contain the handle too.
        _LOGGER.debug("Failed releasing native resources")


def _runtime_configuration() -> Optional[tuple[Optional[bool], Optional[float], Optional[float]]]:
    if _native_runtime_module is None:
        return None
    return _native_runtime_module._runtime_configuration()


class AsyncRustBinding(RustBindingShared, AsyncCosmosBackend):
    """Sends async operations from one ``CosmosClient`` to a shared rust driver.

    Driver sharing works exactly as described on the sync RustBinding: one
    rust driver per distinct endpoint, credential, and config, reference
    counted. Closing releases this client's reference; active operations can
    keep the driver alive after the last client closes.

    Native I/O does not reserve a dedicated Python executor worker per request.
    Initialization and normal teardown are offloaded, but token acquisition,
    synchronous Python work, locks, and cleanup fallback can still block.
    Concurrency is not determined by the service/connection pool alone.

    RustBindingShared stores common client state and registrations. This class
    owns async dispatch and shares driver initialization and cleanup across
    callers, including callers on different event loops.
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
        """Store client settings and prepare lazy Rust driver initialization."""
        # Backend-specific fields first, so they exist even if the shared init's
        # strict-mode registration raises and the finalizer then runs.
        # _build_lock serializes acquisition attempts across loops. Successful
        # initialization is reused; failed attempts can run again. Native
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
        # Shared per-client state + endpoint registration (may raise in strict mode).
        self._init_shared(
            endpoint, master_key, client_config, token_credential, strict_isolation
        )

    def _build_driver_handle(self) -> str:
        """Create or share the Rust driver handle on a worker thread."""
        # Native acquisition can block, so it runs on a worker. _build_lock
        # serializes attempts without holding the handle-state lock. If close
        # wins before publication, release the newly acquired handle here.
        if _rust_module is None:
            raise NotImplementedError(
                "AsyncRustBinding: the compiled azure.cosmos._rust "
                "module is not present in this environment. Build it "
                "with `maturin develop` from the repo root."
            )
        if self._driver_handle is not None:
            return self._driver_handle
        surplus_driver_handle: Optional[str] = None
        with self._build_lock:
            # Another loop may have built it while we waited for _build_lock.
            if self._driver_handle is not None:
                return self._driver_handle
            if self._closing:
                raise RuntimeError("AsyncRustBinding: the client is closed.")
            new_driver_handle: Optional[str] = self._initialize_driver(_rust_module, _runtime_configuration)
            with self._driver_handle_lock:
                if self._closing:
                    surplus_driver_handle, new_driver_handle = new_driver_handle, None
                else:
                    self._driver_handle = new_driver_handle
        if surplus_driver_handle is not None:
            _close_driver_handle_quietly(surplus_driver_handle)
        if new_driver_handle is None:
            raise RuntimeError(
                "AsyncRustBinding: the client was closed during initialization."
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
        submit separate jobs; ``_build_lock`` serializes their native acquisition
        and rechecks the handle. A failed attempt can be retried on a later call.
        Cancelling an await does not necessarily stop its executor job.
        """
        if _REQUEST_CONTRACT_ERROR is not None:
            raise RuntimeError(_REQUEST_CONTRACT_ERROR)
        if self._closing:
            raise RuntimeError("AsyncRustBinding: the client is closed.")
        # Already built: return it without taking any lock.
        driver_handle = self._driver_handle
        if driver_handle is not None:
            return driver_handle
        loop = asyncio.get_running_loop()
        init_future = self._init_future
        if init_future is None or self._init_future_loop is not loop:
            init_future = loop.run_in_executor(None, self._build_driver_handle)
            self._init_future = init_future
            self._init_future_loop = loop
        try:
            return await init_future
        finally:
            # Clear this future on completion, failure, or cancelled waiting.
            # Its executor job may still be running after cancellation.
            if self._init_future is init_future:
                self._init_future = None
                self._init_future_loop = None

    async def close(self) -> None:
        """Release this client's Rust resources once.

        Finish operations before closing. Other clients and operations can retain
        the driver. Cancelling a close caller stops its wait, not the cleanup.
        Subsequent callers wait for the same cleanup, even on another event loop.
        """
        loop = asyncio.get_running_loop()
        with self._close_lock:
            completion = self._close_future
            if completion is None:
                with self._driver_handle_lock:
                    self._closing = True
                self._release_config_once()
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
        """Release resources if the client was not closed explicitly."""
        # Fallback for a client that was never closed explicitly; prefer calling
        # close() (or `async with`). The teardown calls into the Rust driver
        # (release_driver_handle) and may join the credential-bridge thread, both of which
        # can block. A finalizer can run on ANY thread -- including the
        # event-loop thread, when GC collects the client mid-run -- so blocking
        # here would stall that loop. Release the config registration inline
        # (including its locking), then offload native/bridge teardown to a
        # daemon thread if a loop is running on this thread, or inline otherwise
        # (the usual finalizer case, and interpreter shutdown where a new thread
        # may not start). The closure captures only the handle and credential, not
        # self, so the finalizer does not resurrect the object.
        try:
            self._release_config_once()
            credential = self._take_token_credential_for_close()
            driver_handle = self._take_driver_handle_for_close()
            if driver_handle is None and credential is None:
                return

            def _blocking_teardown() -> None:
                """Release resources that may block the current thread."""
                close_credential_bridge_quietly(credential)
                if driver_handle is not None:
                    _close_driver_handle_quietly(driver_handle)

            try:
                asyncio.get_running_loop()
            except RuntimeError:
                # No running event loop on this thread; perform cleanup inline.
                _blocking_teardown()
                return
            try:
                threading.Thread(
                    target=_blocking_teardown,
                    name="cosmos-rust-finalizer",
                    daemon=True,
                ).start()
            except Exception:  # pylint: disable=broad-except
                # Could not start a thread (e.g. during interpreter shutdown);
                # fall back to inline cleanup.
                _blocking_teardown()
        except Exception:  # pylint: disable=broad-except
            # Never raise from object finalization.
            pass

    async def execute(
        self, prepared: PreparedRequest, *, deadline: Optional[float] = None
    ) -> BackendResponse:
        """Send one prepared single-response operation."""
        if not isinstance(prepared, PreparedRequest):
            raise TypeError("execute requires a PreparedRequest")
        if _rust_module is None:
            raise NotImplementedError(
                "AsyncRustBinding.execute: the compiled "
                "azure.cosmos._rust module is not present in this "
                "environment. Build it with `maturin develop` from "
                "the repo root."
            )

        driver_handle = await self._ensure_driver_handle()
        # Look up the binding's *_item_async function for this op; None if unsupported.
        binding_function = _get_binding_function(prepared.op)
        if binding_function is None:
            raise NotImplementedError(
                "AsyncRustBinding.execute does not yet support op={!r}.".format(prepared.op)
            )
        # Record selected dispatch, not successful execution or service I/O.
        # Omit the credential-bearing handle.
        _LOGGER.debug(
            "cosmos backend=%s op=%s dispatch=%s_async",
            BACKEND_NAME_RUST,
            prepared.op,
            OP_TO_BINDING_METHOD.get(prepared.op),
        )
        # Await native dispatch directly rather than allocating an executor job
        # for its I/O. Translate response-less errors to ServiceResponseError,
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
        """Get routing facts from the driver's cache, fetching on a miss."""
        if _rust_module is None:
            raise NotImplementedError(
                "AsyncRustBinding.get_container_metadata: the compiled "
                "azure.cosmos._rust module is not present in this environment."
            )
        dispatch = getattr(_rust_module, "get_container_metadata_async", None)
        if dispatch is None:
            raise NotImplementedError("The Rust binding does not expose get_container_metadata_async")
        driver_handle = await self._ensure_driver_handle()
        try:
            result = (
                await dispatch(driver_handle, container_link)
                if deadline is None
                else await dispatch(driver_handle, container_link, timeout_seconds=remaining_timeout(deadline))
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
        self, prepared: PreparedQuery, *, deadline: Optional[float] = None
    ) -> AsyncIterator[QueryPage]:
        """Yield one page from the selected async stateless or cursor dispatch."""
        self.validate_page_request(prepared)
        method = get_page_binding_method(
            prepared.op, uses_cursor=prepared.cursor is not None
        )
        dispatch = _get_page_dispatch(method)
        if dispatch is None:
            raise BindingProtocolError("Validated page dispatch is no longer available")
        driver_handle = await self._ensure_driver_handle()
        binding_request = build_binding_request_from_page(prepared)
        _LOGGER.debug(
            "cosmos backend=%s op=%s dispatch=%s_async",
            BACKEND_NAME_RUST,
            prepared.op,
            method,
        )
        with page_dispatch_errors(deadline, _UNSUPPORTED_QUERY_ERROR, _DRIVER_TRANSPORT_ERROR):
            args, kwargs = page_dispatch_arguments(driver_handle, binding_request, prepared, deadline)
            result = await dispatch(*args, **kwargs)
            response = build_backend_response(*result)
        yield build_query_page(prepared, response)

    def validate_page_request(self, prepared: PreparedQuery) -> None:
        """Check module/export availability without acquiring a driver."""
        validate_page_request(prepared, _rust_module, _get_page_dispatch, "AsyncRustBinding", "_async")

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
