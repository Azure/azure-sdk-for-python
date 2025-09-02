# The MIT License (MIT)
# Copyright (c) 2021 Microsoft Corporation

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
from asyncio import Task, CancelledError  # pylint: disable=do-not-import-asyncio
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple, Callable, Awaitable, cast

from azure.core.pipeline.transport import HttpRequest  # pylint: disable=no-legacy-azure-core-http-response-import

from ._asynchronous_hedging_completion_status import AsyncHedgingCompletionStatus
from ._global_partition_endpoint_manager_circuit_breaker_async import \
    _GlobalPartitionEndpointManagerForCircuitBreakerAsync
from .._availability_strategy import CrossRegionHedgingStrategy
from .._request_object import RequestObject
from ..documents import _OperationType
from ..exceptions import CosmosHttpResponseError

ResponseType = Tuple[Dict[str, Any], Dict[str, Any]]

class CrossRegionAsyncHedgingHandler:
    """Handler for CrossRegionHedgingStrategy that implements cross-region request hedging."""

    def _setup_excluded_regions_for_hedging(
        self,
        location_index: int,
        available_locations: List[str],
        existing_excluded_locations: Optional[List[str]] = None
    ) -> List[str]:
        """Set up excluded regions for hedging requests.
        
        Excludes all regions except the target region, while preserving any existing exclusions.
        
        :param location_index: Index of current target location
        :type location_index: int
        :param available_locations: List of available locations
        :type available_locations: List[str]
        :param existing_excluded_locations: Existing excluded locations from request parameters
        :type existing_excluded_locations: List[str]
        :returns: List of regions to exclude
        :rtype: List[str]
        """
        # Start with any existing excluded locations
        excluded = list(existing_excluded_locations) if existing_excluded_locations else []

        # Add additional excluded regions for hedging
        if location_index > 0:
            for i, loc in enumerate(available_locations):
                if i != location_index and loc not in excluded:  # Exclude all non-target regions
                    excluded.append(loc)

        return excluded

    def _is_non_transient_error(self, exception: Exception) -> bool:
        """Check if exception a non-transient error.
        
        :param exception: exception
        :type exception: Exception
        :returns: True if exception is non-transient
        :rtype: bool
        """
        if isinstance(exception, CosmosHttpResponseError):
            status_code = exception.status_code
            sub_status = exception.sub_status
            return (status_code in [400, 409, 405, 412, 413, 401] or
                    (status_code == 404 and sub_status == 0))
        return False

    async def execute_single_request_with_delay(
        self,
        request_params: RequestObject,
        request: HttpRequest,
        execute_request_fn: Callable[..., Awaitable[ResponseType]],
        location_index: int,
        available_locations: List[str],
        complete_status: AsyncHedgingCompletionStatus,
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
        :type complete_status: AsyncHedgingCompletionStatus
        :param first_request_params_holder: Namespace object storing request parameters for the initial request
        :type first_request_params_holder: SimpleNamespace
        :returns: Tuple containing response data and headers from the request
        :rtype: ResponseType
        :raises: CancelledError if request is cancelled due to completion status
        """

        # Create request parameters for this location
        params = copy.deepcopy(request_params)
        params.is_hedging_request = location_index > 0
        params.completion_status = complete_status

        # Setup excluded regions for hedging requests
        params.excluded_locations = self._setup_excluded_regions_for_hedging(
            location_index,
            available_locations,
            request_params.excluded_locations
        )

        req = copy.deepcopy(request)

        # Calculate delay based on location index
        if location_index == 0:
            delay: int = 0  # No delay for initial request
            first_request_params_holder.request_params = params
        elif location_index == 1:
            # First hedged request after threshold
            delay = cast(CrossRegionHedgingStrategy, request_params.availability_strategy).threshold_ms
        else:
            # Subsequent requests after threshold steps
            steps = location_index - 1
            cross_region_hedging_strategy = cast(CrossRegionHedgingStrategy, request_params.availability_strategy)
            delay = (cross_region_hedging_strategy.threshold_ms +
                     (steps * cross_region_hedging_strategy.threshold_steps_ms))

        if delay > 0:
            await asyncio.sleep(delay / 1000)

        if complete_status is not None and complete_status.is_completed:
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
        completion_status = AsyncHedgingCompletionStatus()

        tasks = []
        first_task: Optional[Task] = None
        first_request_params_holder: SimpleNamespace = SimpleNamespace(request_params=None)
        try:
            # Create tasks for each location
            for i in range(len(available_locations)):
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
                tasks.append(task)
                if i == 0:
                    first_task = task

            # Wait for tasks to complete
            for completed_task in asyncio.as_completed(tasks):
                try:
                    result = await completed_task
                    completion_status.set_completed()

                    if completed_task is first_task:
                        return result

                    # successful response does not come from the initial request, record failure for it
                    await self._record_cancel_for_first_request(first_request_params_holder, global_endpoint_manager)
                    return result
                except Exception as e: #pylint: disable=broad-exception-caught
                    if completed_task is first_task:
                        completion_status.set_completed()
                        raise e
                    if self._is_non_transient_error(e):
                        completion_status.set_completed()
                        await self._record_cancel_for_first_request(
                            first_request_params_holder,
                            global_endpoint_manager)
                        raise e

            # if we have reached here, it means all tasks completed_task but all failed with transient exceptions
            # in this case, raise the exception from the first task
            completion_status.set_completed()
            if first_task is None or first_task.exception() is None:
                raise RuntimeError("first task can not be none and it should have failed")
            raise first_task.exception()
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _record_cancel_for_first_request(
            self,
            request_params_holder: SimpleNamespace,
            global_endpoint_manager: Any) -> None:
        if request_params_holder.request_params is not None:
            await global_endpoint_manager.record_failure(request_params_holder.request_params)

    def _get_applicable_endpoints(self, request: RequestObject, global_endpoint_manager: Any) -> List[str]:
        """Get the list of applicable endpoints for request routing.

        Determines the appropriate endpoints for request routing based on the operation type
        (read or write) and the current state of regional routing contexts. For write
        operations, it fetches write-specific routing contexts, while for read operations
        it uses read-specific routing contexts.

        :param request: The request object containing operation type and routing preferences
        :type request: RequestObject
        :param global_endpoint_manager: Manager handling endpoint routing and availability
        :type global_endpoint_manager: Any
        :returns: List of region names that are applicable for the request
        :rtype: List[str]
        """

        applicable_endpoints = []
        if _OperationType.IsWriteOperation(request.operation_type):
            regional_context_list = global_endpoint_manager.get_applicable_write_regional_routing_contexts(request)
        else:
            regional_context_list = global_endpoint_manager.get_applicable_read_regional_routing_contexts(request)

        if regional_context_list is not None:
            for regional_context in regional_context_list:
                applicable_endpoints.append(
                    global_endpoint_manager.get_region_name(
                        regional_context.get_primary(),
                        _OperationType.IsWriteOperation(request.operation_type)
                    )
                )

        return applicable_endpoints

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
    :raises: ValueError if availability strategy is not supported
    """

    availability_strategy = request_params.availability_strategy
    if isinstance(availability_strategy, CrossRegionHedgingStrategy):
        return await _cross_region_hedging_handler.execute_request(
            request_params,
            global_endpoint_manager,
            request,
            execute_request_fn
        )

    raise ValueError(f"Unsupported availability strategy type: {type(CrossRegionHedgingStrategy)}")

