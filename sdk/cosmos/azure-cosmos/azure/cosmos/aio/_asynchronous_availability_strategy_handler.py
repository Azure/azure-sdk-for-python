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

"""Module for handling asynchronous request hedging strategies in Azure Cosmos DB."""
import asyncio  # pylint: disable=do-not-import-asyncio
import copy
import os
from asyncio import Task, CancelledError, Event  # pylint: disable=do-not-import-asyncio
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple, Callable, Awaitable

from azure.core.pipeline.transport import HttpRequest  # pylint: disable=no-legacy-azure-core-http-response-import

from ._global_partition_endpoint_manager_circuit_breaker_async import \
    _GlobalPartitionEndpointManagerForCircuitBreakerAsync
from .._availability_strategy_handler_base import AvailabilityStrategyHandlerMixin
from .._request_object import RequestObject

ResponseType = Tuple[Dict[str, Any], Dict[str, Any]]

class CrossRegionAsyncHedgingHandler(AvailabilityStrategyHandlerMixin):
    """Handler for CrossRegionHedgingStrategy that implements cross-region request hedging."""


    async def execute_single_request_with_delay(
        self,
        request_params: RequestObject,
        request: HttpRequest,
        execute_request_fn: Callable[..., Awaitable[ResponseType]],
        location_index: int,
        available_locations: List[str],
        complete_status: Event,
        first_request_params_holder: SimpleNamespace
    ) -> ResponseType:
        """Execute a single request with appropriate delay based on location index.

        This method is part of the cross-region hedging strategy implementation. It handles:
        1. Creating a copy of request parameters with hedging-specific modifications
        2. Setting up excluded regions for hedging requests
        3. Calculating and applying appropriate delays based on location index:
           - No delay for initial request (index 0)
           - Threshold delay for first hedged request (index 1)
           - Threshold + steps for subsequent requests (index > 1)
        4. Checking completion status before executing request

        :param request_params: Original request parameters to be copied and modified
        :type request_params: RequestObject
        :param request: The HTTP request to be executed
        :type request: HttpRequest
        :param execute_request_fn: Async function to execute the actual request
        :type execute_request_fn: Callable[..., Awaitable[ResponseType]]
        :param location_index:
            Index of target location determining delay behavior (0=initial, 1=first hedge, >1=subsequent)
        :type location_index: int
        :param available_locations: List of available locations for request routing
        :type available_locations: List[str]
        :param complete_status: Object tracking whether any request has completed successfully
        :type complete_status: asyncio.Event
        :param first_request_params_holder: Namespace object storing request parameters for the initial request
        :type first_request_params_holder: SimpleNamespace
        :returns: Tuple containing response data and headers from the request
        :rtype: ResponseType
        :raises: CancelledError if request is cancelled due to completion status
        """

        availability_strategy_config = request_params.availability_strategy_config
        if availability_strategy_config is None:
            raise ValueError("availability_strategy_config should not be null")

        delay: int
        # Calculate delay based on location index
        if location_index == 0:
            delay = 0  # No delay for initial request
        elif location_index == 1:
            # First hedged request after threshold
            delay = availability_strategy_config.threshold_ms
        else:
            # Subsequent requests after threshold steps
            steps = location_index - 1
            delay = (availability_strategy_config.threshold_ms+
                    (steps * availability_strategy_config.threshold_steps_ms))

        if delay > 0:
            await asyncio.sleep(delay / 1000)

        # Create request parameters for this location
        params = copy.deepcopy(request_params)
        params.is_hedging_request = location_index > 0
        params.completion_status = complete_status

        # Setup excluded regions for hedging requests
        params.excluded_locations = self._create_excluded_regions_for_hedging(
            location_index,
            available_locations,
            request_params.excluded_locations
        )

        req = copy.deepcopy(request)

        if location_index == 0:
            first_request_params_holder.request_params = params

        if complete_status is not None and complete_status.is_set():
            raise CancelledError("The request has been cancelled")

        return await execute_request_fn(params, req)

    async def execute_request(
        self,
        request_params: RequestObject,
        global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreakerAsync,
        request: HttpRequest,
        execute_request_fn: Callable[..., Awaitable[ResponseType]]
    ) -> ResponseType:
        """Execute request with cross-region hedging strategy.

        This method implements an asynchronous request hedging strategy across multiple regions.
        It creates parallel tasks for each available endpoint with appropriate delays between
        requests. The first successful response is returned while other pending requests are
        cancelled. If the first request fails but a subsequent request succeeds, the failure
        of the first request is recorded.

        :param request_params: Parameters for the request including operation type and strategy
        :type request_params: RequestObject
        :param global_endpoint_manager: Manager for handling global endpoints and circuit breaking
        :type global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreakerAsync
        :param request: The HTTP request to be executed
        :type request: HttpRequest
        :param execute_request_fn: Async function to execute the actual request
        :type execute_request_fn: Callable[..., Awaitable[ResponseType]]
        :returns: A tuple containing the response data and headers from the successful request
        :rtype: ResponseType
        :raises: Exception from the first request if all requests fail with transient errors
        """
        # Get available locations from global endpoint manager
        available_locations = self._get_applicable_endpoints(request_params, global_endpoint_manager)
        completion_status = Event()

        active_tasks = []
        pending_indices = list(range(len(available_locations)))
        first_task: Optional[Task] = None
        first_request_params_holder: SimpleNamespace = SimpleNamespace(request_params=None)
        max_concurrency = request_params.availability_strategy_max_concurrency or os.cpu_count()

        try:
            # Create initial batch of tasks up to max_concurrency
            initial_batch = pending_indices[:max_concurrency]
            pending_indices = pending_indices[max_concurrency:]

            for i in initial_batch:
                task = asyncio.create_task(
                    self.execute_single_request_with_delay(
                        request_params,
                        request,
                        execute_request_fn,
                        i,
                        available_locations,
                        completion_status,
                        first_request_params_holder
                    ))
                active_tasks.append(task)
                if i == 0:
                    first_task = task

            # Process tasks as they complete and create new ones if needed
            while active_tasks and not completion_status.is_set():
                done, pending = await asyncio.wait(active_tasks, return_when=asyncio.FIRST_COMPLETED)
                active_tasks = list(pending)

                # Process completed tasks first to check for success
                for completed_task in done:
                    try:
                        result = await completed_task
                        completion_status.set()

                        if completed_task is first_task:
                            return result

                        # successful response does not come from the initial request, record failure for it
                        await self._record_cancel_for_first_request(
                            first_request_params_holder,
                            global_endpoint_manager)
                        return result
                    except Exception as e:  # pylint: disable=broad-exception-caught
                        if completed_task is first_task:
                            completion_status.set()
                            raise e
                        if self._is_non_transient_error(e):
                            completion_status.set()
                            await self._record_cancel_for_first_request(
                                first_request_params_holder,
                                global_endpoint_manager)
                            raise e

                # If no success yet, create new tasks to replace completed ones
                if not completion_status.is_set():
                    num_completed = len(done)
                    for _ in range(min(num_completed, len(pending_indices))):
                        next_index = pending_indices.pop(0)
                        task = asyncio.create_task(
                            self.execute_single_request_with_delay(
                                request_params,
                                request,
                                execute_request_fn,
                                next_index,
                                available_locations,
                                completion_status,
                                first_request_params_holder
                            ))
                        active_tasks.append(task)

            # if we have reached here, it means all tasks completed_task but all failed with transient exceptions
            # in this case, raise the exception from the first task
            completion_status.set()
            if first_task is None:
                raise RuntimeError("first task can not be none")

            first_task_exception = first_task.exception()
            if first_task_exception is None:
                raise RuntimeError("first task should have failed")
            raise first_task_exception
        finally:
            for task in active_tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*active_tasks, return_exceptions=True)

    async def _record_cancel_for_first_request(
            self,
            request_params_holder: SimpleNamespace,
            global_endpoint_manager: Any) -> None:
        if request_params_holder.request_params is not None:
            await global_endpoint_manager.record_failure(request_params_holder.request_params)


# Global handler instance
_cross_region_hedging_handler = CrossRegionAsyncHedgingHandler()

async def execute_with_availability_strategy(
    request_params: RequestObject,
    global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreakerAsync,
    request: HttpRequest,
    execute_request_fn: Callable[..., Awaitable[ResponseType]]
) -> ResponseType:
    """Execute a request with hedging based on the availability strategy.

    This function is the main entry point for request hedging in the Azure Cosmos DB SDK.
    It creates an appropriate hedging handler based on the availability strategy specified
    in the request parameters and delegates request execution to that handler.

    The hedging behavior depends on the strategy:
    - With DisabledStrategy: Executes request directly without hedging
    - With CrossRegionHedgingStrategy: Implements cross-region request hedging with delays

    :param request_params: Parameters containing operation type, strategy, and routing preferences
    :type request_params: RequestObject
    :param global_endpoint_manager: Manager for handling global endpoints and circuit breaking
    :type global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreakerAsync
    :param request: The HTTP request to be executed
    :type request: HttpRequest
    :param execute_request_fn: Async function to execute the actual request
    :type execute_request_fn: Callable[..., Awaitable[ResponseType]]
    :returns: Tuple containing response data and headers from the successful request
    :rtype: ResponseType
    :raises: CosmosClientError if all hedged requests fail
    """

    return await _cross_region_hedging_handler.execute_request(
        request_params,
        global_endpoint_manager,
        request,
        execute_request_fn
    )
