# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Monotonic operation budgets, shared across preparation and dispatch."""
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
    """Return the remaining seconds without rounding up or restarting the budget."""
    if deadline is None:
        return None
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise CosmosClientTimeoutError()
    return remaining


def legacy_deadline_options(options: Any, deadline: Optional[float]) -> dict[str, Any]:
    """Give a legacy operation only the remaining budget, including all its pages."""
    result = dict(options or {})
    remaining = remaining_timeout(deadline)
    if remaining is not None:
        result["timeout"] = remaining
        result[_Constants.OperationStartTime] = time.time()
        result[_Constants.TimeoutScope] = TimeoutScope.OPERATION
        result["_item_operation_deadline"] = deadline
    return result


def legacy_deadline_kwargs(kwargs: Any, deadline: Optional[float]) -> dict[str, Any]:
    """Pass the remaining budget where legacy point-request retries consume it."""
    result = dict(kwargs or {})
    remaining = remaining_timeout(deadline)
    if remaining is not None:
        result["timeout"] = remaining
        result[_Constants.OperationStartTime] = time.time()
    return result


async def run_with_deadline(operation: Callable[[], Awaitable[_T]], deadline: Optional[float]) -> _T:
    """Bound async work and drain its cancellation before returning a timeout."""
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
    # A TimeoutError raised by the operation (including a customer hook) is not
    # our timer expiring and must retain its original identity.
    return task.result()


@contextmanager
def deadline_lock(lock: Any, deadline: Optional[float]) -> Iterator[None]:
    """Acquire a metadata lock without allowing it to restart the read budget."""
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
    """Cancel a timed-out lock waiter; do not leave metadata work running."""
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
