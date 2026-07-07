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
from asyncio import CancelledError, Event, Task
from typing import Any, Awaitable, Callable, Dict, List, Optional, Tuple

from azure.core.pipeline.transport import HttpRequest  # pylint: disable=no-legacy-azure-core-http-response-import

from .._availability_strategy_config import (
    DEFAULT_METADATA_HEDGING_CONCURRENCY_BUDGET,
    MetadataCrossRegionHedgingStrategy,
)
from .._availability_strategy_handler_base import AvailabilityStrategyHandlerMixin
from .._metadata_hedging import _status_codes_from_exception, is_regional_failure
from .._request_object import RequestObject
from ..http_constants import StatusCodes
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

    def is_acceptable_winner(  # pylint: disable=unused-argument
        self,
        result: Optional[ResponseType],
        exception: Optional[BaseException],
        is_hedge: bool,
    ) -> bool:
        """Return True if a settled branch is an acceptable winner.

        :param result: The successful response tuple, or None if the branch raised.
        :type result: Optional[Tuple[dict, dict]]
        :param exception: The exception raised by the branch, or None on success.
        :type exception: Optional[BaseException]
        :param is_hedge: Whether the branch is the hedge (non-primary) branch.
        :type is_hedge: bool
        :returns: True if the branch is an acceptable winner.
        :rtype: bool
        """
        if exception is None:
            return True

        if isinstance(exception, CancelledError):
            return False

        status_code, sub_status = _status_codes_from_exception(exception)

        if is_regional_failure(status_code, sub_status, exception):
            return False

        if is_hedge and status_code in (StatusCodes.UNAUTHORIZED, StatusCodes.FORBIDDEN):
            return False

        return True

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

            pending = set(active_tasks)
            while pending:
                done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
                for completed_task in done:
                    is_primary = completed_task is primary_task
                    exception = completed_task.exception()
                    result = None if exception is not None else completed_task.result()

                    if self.is_acceptable_winner(result, exception, is_hedge=not is_primary):
                        completion_status.set()
                        self._record_winner(winner_sink, is_primary, available_locations, request_params)
                        # Note: no per-region failure is recorded for the primary when the
                        # hedge wins. Metadata cache reads are account-global, not
                        # per-partition, so the circuit-breaker health tracker (keyed on
                        # partition-key ranges) does not apply here.
                        if exception is not None:
                            raise exception
                        return result  # type: ignore[return-value]

            # Neither branch produced an acceptable winner; prefer the primary's outcome.
            completion_status.set()
            self._record_winner(winner_sink, True, available_locations, request_params)
            primary_exception = primary_task.exception()
            if primary_exception is not None:
                raise primary_exception
            return primary_task.result()
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
