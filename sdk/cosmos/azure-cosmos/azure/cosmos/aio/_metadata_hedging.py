# The MIT License (MIT)
# Copyright (c) Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Asynchronous cold-start metadata cache cross-region hedging for Azure Cosmos DB.

Async port of the .NET ``MetadataHedgingStrategy`` (PR
Azure/azure-cosmos-dotnet-v3#5999). See :mod:`azure.cosmos._metadata_hedging` for the
synchronous counterpart and design notes.
"""

import asyncio  # pylint: disable=do-not-import-asyncio
import copy
import logging
from asyncio import CancelledError, Event, Task  # pylint: disable=do-not-import-asyncio
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

from azure.core.pipeline.transport import HttpRequest  # pylint: disable=no-legacy-azure-core-http-response-import

from .._availability_strategy_config import (
    DEFAULT_METADATA_HEDGING_CONCURRENCY_BUDGET,
    MetadataCrossRegionHedgingStrategy,
)
from .._availability_strategy_handler_base import AvailabilityStrategyHandlerMixin
from .._metadata_hedging import _BranchOutcome, classify_branch_outcome
from .._request_object import RequestObject
from ._global_partition_endpoint_manager_circuit_breaker_async import \
    _GlobalPartitionEndpointManagerForCircuitBreakerAsync

logger = logging.getLogger("azure.cosmos.metadata_hedging")

ResponseType = Tuple[Dict[str, Any], Dict[str, Any]]


class MetadataCrossRegionAsyncHedgingHandler(AvailabilityStrategyHandlerMixin):
    """Bounded async cross-region hedging handler for cold-start metadata cache reads.

    One instance per client. The per-client concurrency budget caps the number of
    in-flight metadata hedges; when it is exhausted, eligible requests fall back to a
    primary-only send.

    :param concurrency_budget: Max number of in-flight metadata hedges for this client.
    :type concurrency_budget: int
    """

    def __init__(self, concurrency_budget: int = DEFAULT_METADATA_HEDGING_CONCURRENCY_BUDGET) -> None:
        self._budget = asyncio.Semaphore(max(1, concurrency_budget))

    def _classify_task(self, task: Task) -> str:
        """Classify a COMPLETED task into a :class:`_BranchOutcome`.

        :param task: A task that is guaranteed to be done.
        :type task: ~asyncio.Task
        :returns: One of the :class:`_BranchOutcome` string constants.
        :rtype: str
        """
        if task.cancelled():
            return _BranchOutcome.CANCELLED
        exception = task.exception()
        if isinstance(exception, CancelledError):
            return _BranchOutcome.CANCELLED
        return classify_branch_outcome(exception)

    @staticmethod
    async def _wait_settled(task: Task) -> None:
        """Wait until ``task`` settles, without propagating its outcome (classified separately).

        :param task: The task to wait for.
        :type task: ~asyncio.Task
        :rtype: None
        """
        await asyncio.wait({task})

    def _finish(
        self,
        task: Task,
        winner_sink: Optional[List[Any]],
        is_primary: bool,
        available_locations: List[str],
        request_params: RequestObject,
    ) -> ResponseType:
        """Record the winner and return/raise the winning branch's outcome.

        :param task: The winning (completed) task whose outcome is returned.
        :type task: ~asyncio.Task
        :param winner_sink: Optional length-1 sink for the winner descriptor.
        :type winner_sink: Optional[List[Any]]
        :param is_primary: Whether the winning branch is the primary.
        :type is_primary: bool
        :param available_locations: Ordered applicable region names (index 0 = primary).
        :type available_locations: List[str]
        :param request_params: The originating request parameters.
        :type request_params: ~azure.cosmos._request_object.RequestObject
        :returns: The winning response tuple.
        :rtype: Tuple[dict, dict]
        """
        self._record_winner(winner_sink, is_primary, available_locations, request_params)
        if task.cancelled():
            raise CancelledError("The request has been cancelled")
        exception = task.exception()
        if exception is not None:
            raise exception
        return task.result()  # type: ignore[return-value]

    async def _send_with_delay(
        self,
        request_params: RequestObject,
        request: HttpRequest,
        execute_request_fn: Callable[..., Awaitable[ResponseType]],
        location_index: int,
        available_locations: List[str],
        complete_status: Event,
    ) -> ResponseType:
        strategy = request_params.availability_strategy
        if strategy is None:
            raise ValueError("availability_strategy should not be null for metadata hedging")

        delay = 0 if location_index == 0 else strategy.threshold_ms
        if delay > 0:
            await asyncio.sleep(delay / 1000)

        params = copy.deepcopy(request_params)
        params.is_hedging_request = location_index > 0
        params.completion_status = complete_status
        params.excluded_locations = self._create_excluded_regions_for_hedging(
            location_index,
            available_locations,
            request_params.excluded_locations,
        )

        req = copy.deepcopy(request)

        if complete_status.is_set():
            raise CancelledError("The request has been cancelled")

        return await execute_request_fn(params, req)

    async def _resolve_winner(
        self,
        done: set,
        primary_task: Task,
        hedge_task: Task,
    ) -> Tuple[Task, bool]:
        """Resolve which settled branch wins, keeping the primary authoritative.

        A hedge can win only by settling first with a ``SUCCESS``, and even then never over
        a primary that has already produced a definitive (non-regional) outcome. A primary
        regional failure yields to a successful hedge; otherwise the primary's outcome (its
        exception rethrown by :meth:`_finish`) is authoritative. Mirrors the .NET
        ``ResolveWinnerAsync``.

        :param done: The set of tasks completed by the first ``asyncio.wait``.
        :type done: set
        :param primary_task: The primary branch task.
        :type primary_task: ~asyncio.Task
        :param hedge_task: The hedge branch task.
        :type hedge_task: ~asyncio.Task
        :returns: The winning task and whether it is the primary branch.
        :rtype: Tuple[~asyncio.Task, bool]
        """
        # If both settled together, treat the primary as first so it stays authoritative.
        if primary_task in done:
            if self._classify_task(primary_task) != _BranchOutcome.REGIONAL_FAILURE:
                # Success or a definitive error -> authoritative; never overridden.
                return primary_task, True
            # Primary regional failure -> a successful hedge may now win; otherwise the
            # primary's (authoritative) regional failure is returned.
            await self._wait_settled(hedge_task)
            if self._classify_task(hedge_task) == _BranchOutcome.SUCCESS:
                return hedge_task, False
            return primary_task, True

        # Hedge settled first.
        if self._classify_task(hedge_task) == _BranchOutcome.SUCCESS:
            # A successful hedge wins unless the primary has ALREADY settled with a
            # definitive (non-regional) outcome, which the hedge must never override.
            if primary_task.done() and \
                    self._classify_task(primary_task) != _BranchOutcome.REGIONAL_FAILURE:
                return primary_task, True
            return hedge_task, False
        # A non-success hedge can never win; wait for the primary's authoritative outcome.
        await self._wait_settled(primary_task)
        return primary_task, True

    async def execute_request(
        self,
        request_params: RequestObject,
        global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreakerAsync,
        request: HttpRequest,
        execute_request_fn: Callable[..., Awaitable[ResponseType]],
        winner_sink: Optional[List[Any]] = None,
    ) -> ResponseType:
        """Execute a metadata read with bounded primary + single-hedge cross-region hedging.

        :param request_params: Request parameters for the metadata read.
        :type request_params: ~azure.cosmos._request_object.RequestObject
        :param global_endpoint_manager: Manager for endpoint routing and health tracking.
        :type global_endpoint_manager:
            ~azure.cosmos.aio._GlobalPartitionEndpointManagerForCircuitBreakerAsync
        :param request: The HTTP request to be executed.
        :type request: ~azure.core.pipeline.transport.HttpRequest
        :param execute_request_fn: Async function that executes the actual request.
        :type execute_request_fn: Callable[..., Awaitable[Tuple[dict, dict]]]
        :param winner_sink: Optional length-1 list to receive the winner descriptor for
            PartitionKeyRange continuation pinning (``hedge_won`` / ``winning_region`` /
            ``pin_excluded_locations``).
        :type winner_sink: Optional[List[Any]]
        :returns: The winning response tuple.
        :rtype: Tuple[dict, dict]
        """
        available_locations = self._get_applicable_endpoints(request_params, global_endpoint_manager)
        if len(available_locations) <= 1:
            logger.debug("Metadata hedge skipped: SingleRegion")
            return await execute_request_fn(request_params, request)

        # Non-blocking budget check: locked() is True only when the budget is fully
        # exhausted (value == 0). There is no await between this check and acquire(),
        # so in single-threaded asyncio no other coroutine can consume the slot in
        # between and acquire() completes immediately without blocking.
        if self._budget.locked():
            logger.debug("Metadata hedge skipped: BudgetExhausted")
            return await execute_request_fn(request_params, request)

        await self._budget.acquire()
        completion_status = Event()
        active_tasks: List[Task] = []
        try:
            primary_task = asyncio.create_task(self._send_with_delay(
                request_params, request, execute_request_fn,
                0, available_locations, completion_status))
            hedge_task = asyncio.create_task(self._send_with_delay(
                request_params, request, execute_request_fn,
                1, available_locations, completion_status))
            active_tasks = [primary_task, hedge_task]

            # Resolve the primary-vs-hedge race, keeping the primary authoritative: a hedge
            # can win only by settling first with a SUCCESS, and even then only while the
            # primary has not already produced a definitive (non-regional) answer. Mirrors
            # the .NET ``ResolveWinnerAsync``.
            #
            # Note: no per-region failure is recorded when the hedge wins. Metadata cache
            # reads are account-global, not per-partition, so the circuit-breaker health
            # tracker (keyed on partition-key ranges) does not apply here.
            done, _pending = await asyncio.wait(
                {primary_task, hedge_task}, return_when=asyncio.FIRST_COMPLETED)
            winner_task, is_primary = await self._resolve_winner(done, primary_task, hedge_task)
            return self._finish(
                winner_task, winner_sink, is_primary, available_locations, request_params)
        finally:
            completion_status.set()
            for task in active_tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*active_tasks, return_exceptions=True)
            self._budget.release()


async def execute_metadata_hedging(
    handler: MetadataCrossRegionAsyncHedgingHandler,
    request_params: RequestObject,
    global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreakerAsync,
    request: HttpRequest,
    execute_request_fn: Callable[..., Awaitable[ResponseType]],
    winner_sink: Optional[List[Any]] = None,
) -> ResponseType:
    """Execute a metadata read with cold-start cross-region hedging.

    :param handler: The per-client metadata hedging handler.
    :type handler: ~azure.cosmos.aio._metadata_hedging.MetadataCrossRegionAsyncHedgingHandler
    :param request_params: Request parameters for the metadata read.
    :type request_params: ~azure.cosmos._request_object.RequestObject
    :param global_endpoint_manager: Manager for endpoint routing and health tracking.
    :type global_endpoint_manager:
        ~azure.cosmos.aio._GlobalPartitionEndpointManagerForCircuitBreakerAsync
    :param request: The HTTP request to be executed.
    :type request: ~azure.core.pipeline.transport.HttpRequest
    :param execute_request_fn: Async function that executes the actual request.
    :type execute_request_fn: Callable[..., Awaitable[Tuple[dict, dict]]]
    :param winner_sink: Optional length-1 list to receive the winner descriptor
        (``hedge_won`` / ``winning_region`` / ``pin_excluded_locations``) so a
        PartitionKeyRange drain can pin later pages to the winning region.
    :type winner_sink: Optional[List[Any]]
    :returns: The winning response tuple.
    :rtype: Tuple[dict, dict]
    """
    if request_params.availability_strategy is None:
        request_params.availability_strategy = MetadataCrossRegionHedgingStrategy()
    return await handler.execute_request(
        request_params, global_endpoint_manager, request, execute_request_fn, winner_sink=winner_sink)
