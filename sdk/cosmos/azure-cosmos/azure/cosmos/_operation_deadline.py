# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Keep preparation, waiting, and execution within the same operation deadline.

A deadline is an end time from time.monotonic(), a clock unaffected by changes
to the system date and time. If the deadline is 105 and that clock now reads
102, three seconds remain. Passing that same deadline to the next step avoids
giving every step a fresh timeout. None means no deadline.

These helpers check remaining time and limit waits. They cannot interrupt a
running synchronous response hook or undo work performed by the service backend.
"""
from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import threading
import time
from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncIterator, Awaitable, Callable, Iterator, Optional, TypeVar, overload

from ._constants import _Constants, TimeoutScope
from ._telemetry import bind_operation_task
from .exceptions import CosmosClientTimeoutError

_T = TypeVar("_T")


@overload
def remaining_timeout(deadline: float) -> float: ...


@overload
def remaining_timeout(deadline: None) -> None: ...


def remaining_timeout(deadline: Optional[float]) -> Optional[float]:
    """Return remaining seconds, or None when no deadline was supplied.

    Raise CosmosClientTimeoutError when no time remains, including when the
    clock exactly equals the deadline.

    :param deadline: Absolute time on the monotonic clock, or None for no deadline.
    :type deadline: float or None
    :return: Positive remaining seconds, or None when no deadline was supplied.
    :rtype: float or None
    """
    if deadline is None:
        return None
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise CosmosClientTimeoutError()
    return remaining


def legacy_deadline_options(options: Any, deadline: Optional[float]) -> dict[str, Any]:
    """Copy legacy options and give them only the remaining operation time.

    Keep the original deadline in _item_operation_deadline. Legacy timeout
    handling also needs a time.time() start value and the remaining duration;
    those use a different clock from the deadline.

    :param options: Legacy request options to copy, or a falsy value for an empty mapping.
    :type options: Any
    :param deadline: Absolute monotonic deadline, or None for no deadline.
    :type deadline: float or None
    :return: Copied options with the remaining budget and legacy operation timing fields.
    :rtype: dict[str, Any]
    """
    result = dict(options or {})
    remaining = remaining_timeout(deadline)
    if remaining is not None:
        result["timeout"] = remaining
        result[_Constants.OperationStartTime] = time.time()
        result[_Constants.TimeoutScope] = TimeoutScope.OPERATION
        result["_item_operation_deadline"] = deadline
    return result


def legacy_deadline_kwargs(kwargs: Any, deadline: Optional[float]) -> dict[str, Any]:
    """Copy keyword arguments and set the timeout used by legacy item retries.

    Use remaining seconds rather than restarting the original timeout.
    With no deadline, return a copy without changing its timeout settings.

    :param kwargs: Legacy keyword arguments to copy, or a falsy value for an empty mapping.
    :type kwargs: Any
    :param deadline: Absolute monotonic deadline, or None for no deadline.
    :type deadline: float or None
    :return: Copied arguments with remaining timeout and operation start time when limited.
    :rtype: dict[str, Any]
    """
    result = dict(kwargs or {})
    remaining = remaining_timeout(deadline)
    if remaining is not None:
        result["timeout"] = remaining
        result[_Constants.OperationStartTime] = time.time()
    return result


async def run_with_deadline(operation: Callable[[], Awaitable[_T]], deadline: Optional[float]) -> _T:
    """Await the operation, cancelling its Python task when the deadline expires.

    With no deadline, await the operation directly. Otherwise, wait for a
    separate task. On timeout or cancellation of this caller, cancel that task
    and wait for it to finish handling cancellation before raising.

    The wait can exceed the deadline if the task is slow to stop or ignores
    cancellation. This is not a promise to interrupt synchronous code or undo
    a request already received by the service backend.

    :param operation: Zero-argument callable that creates the awaitable operation.
    :type operation: typing.Callable
    :param deadline: Absolute monotonic deadline, or None to await without a timer.
    :type deadline: float or None
    :return: Result of the completed operation.
    :rtype: Any
    """
    timeout = remaining_timeout(deadline)
    if timeout is None:
        return await operation()
    cancellation: Optional[asyncio.CancelledError] = None

    async def execute() -> _T:
        nonlocal cancellation
        try:
            return await operation()
        except asyncio.CancelledError as error:
            # Older asyncio Tasks replace this object when result() is called.
            cancellation = error
            raise

    task = asyncio.ensure_future(bind_operation_task(execute)())
    try:
        done, _ = await asyncio.wait({task}, timeout=timeout)
    except BaseException:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        raise
    if not done:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        raise CosmosClientTimeoutError()
    # A TimeoutError from the operation or response hook is not this timer
    # expiring. Raise that original error rather than replacing it.
    if cancellation is not None:
        raise cancellation
    return task.result()


@contextmanager
def deadline_lock(lock: Any, deadline: Optional[float]) -> Iterator[None]:
    """Wait for the lock using the remaining time, then release it on exit.

    Check the deadline again after acquiring the lock. This helper limits the
    wait for the lock, not the code run while the caller holds it.

    :param lock: Synchronous lock supporting acquire, release and context management.
    :type lock: Any
    :param deadline: Absolute monotonic deadline, or None to wait without a limit.
    :type deadline: float or None
    :return: Context manager that releases the acquired lock on exit.
    :rtype: contextlib.AbstractContextManager[None]
    """
    if deadline is None:
        with lock:
            yield
        return
    while not lock.acquire(timeout=min(remaining_timeout(deadline), threading.TIMEOUT_MAX)):
        remaining_timeout(deadline)
    try:
        remaining_timeout(deadline)
        yield
    finally:
        lock.release()


@asynccontextmanager
async def async_deadline_lock(lock: Any, deadline: Optional[float]) -> AsyncIterator[None]:
    """Await the lock using the remaining time, then release it on exit.

    Like deadline_lock, check the time after acquisition but do not put a timer
    around the code run while holding the lock. A timed-out wait becomes
    CosmosClientTimeoutError.

    :param lock: Async lock supporting acquire, release and async context management.
    :type lock: Any
    :param deadline: Absolute monotonic deadline, or None to wait without a limit.
    :type deadline: float or None
    :return: Async context manager that releases the acquired lock on exit.
    :rtype: contextlib.AbstractAsyncContextManager[None]
    """
    if deadline is None:
        async with lock:
            yield
        return
    try:
        await asyncio.wait_for(lock.acquire(), timeout=remaining_timeout(deadline))
    except asyncio.TimeoutError as exc:
        raise CosmosClientTimeoutError(error=exc) from exc
    try:
        remaining_timeout(deadline)
        yield
    finally:
        lock.release()
