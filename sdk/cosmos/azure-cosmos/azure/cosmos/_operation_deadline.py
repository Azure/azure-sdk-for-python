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

import asyncio
import threading
import time
from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncIterator, Awaitable, Callable, Iterator, Optional, TypeVar, overload

from ._constants import _Constants, TimeoutScope
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
    """
    timeout = remaining_timeout(deadline)
    if timeout is None:
        return await operation()
    task = asyncio.ensure_future(operation())
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
    return task.result()


@contextmanager
def deadline_lock(lock: Any, deadline: Optional[float]) -> Iterator[None]:
    """Wait for the lock using the remaining time, then release it on exit.

    Check the deadline again after acquiring the lock. This helper limits the
    wait for the lock, not the code run while the caller holds it.
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
