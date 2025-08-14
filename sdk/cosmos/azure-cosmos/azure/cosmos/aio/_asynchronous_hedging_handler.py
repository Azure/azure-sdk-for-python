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
import abc
import asyncio
import copy
import logging
from asyncio import Task
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple, Union

from .._availability_strategy import CrossRegionHedgingStrategy, DisabledStrategy
from .._request_object import RequestObject
from ..documents import _OperationType
from ..exceptions import CosmosHttpResponseError

logger = logging.getLogger(__name__)
ResponseType = Tuple[Dict[str, Any], Dict[str, Any]]

class AsyncHedgingHandler(abc.ABC):
    """Abstract base class for async hedging handlers."""
    
    @abc.abstractmethod
    async def execute_request(
        self,
        client: Any,
        request_params: Any,
        global_endpoint_manager: Any,
        connection_policy: Any,
        pipeline_client: Any,
        request: Any,
        execute_request_fn: Any,
        **kwargs: Any
    ) -> ResponseType:
        """Execute a request with the appropriate hedging behavior."""
        pass

class DisabledAsyncHedgingHandler(AsyncHedgingHandler):
    """Handler for DisabledStrategy that executes requests directly."""

    async def execute_request(
        self,
        client: Any,
        request_params: Any,
        global_endpoint_manager: Any,
        connection_policy: Any,
        pipeline_client: Any,
        request: Any,
        execute_request_fn: Any,
        **kwargs: Any
    ) -> ResponseType:
        """Execute request without hedging."""
        return await execute_request_fn(
            client,
            global_endpoint_manager,
            request_params,
            connection_policy,
            pipeline_client,
            request,
            **kwargs
        )

class CrossRegionAsyncHedgingHandler(AsyncHedgingHandler):
    """Handler for CrossRegionHedgingStrategy that implements cross-region request hedging."""

    def setup_excluded_regions_for_hedging(
        self,
        location_index: int,
        available_locations: List[str],
        existing_excluded_locations: List[str] = None
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

    def _is_non_transient_error(self, result: Exception) -> bool:
        """Check if result represents either a successful response or a non-transient error.
        
        A non-transient result is either:
        1. A valid response (including responses with null body)
        2. A non-transient error (e.g. 400, 401, 409 etc.)
        
        :param result: Response tuple, exception, or None
        :type result: Union[ResponseType, Exception, None]
        :returns: True if result is either successful or a non-transient error
        :rtype: bool
        """
        if isinstance(result, CosmosHttpResponseError):
            status_code = result.status_code
            sub_status = result.sub_status
            return (status_code in [400, 409, 405, 412, 413, 401] or
                    (status_code == 404 and sub_status == 0))
        return False

    async def execute_single_request_with_delay(
        self,
        client: Any,
        request_params: Any,
        global_endpoint_manager: Any,
        connection_policy: Any,
        pipeline_client: Any,
        request: Any,
        execute_request_fn: Any,
        location_index: int,
        available_locations: List[str],
        complete_status: SimpleNamespace,
        first_request_params_holder: SimpleNamespace,
        **kwargs: Any
    ) -> Union[ResponseType, Exception, None]:
        """Execute a single request.

        :param client: Document client instance
        :param request_params: Request parameters
        :param global_endpoint_manager: Global endpoint manager
        :param connection_policy: Connection policy
        :param pipeline_client: Pipeline client
        :param request: HTTP request
        :param execute_request_fn: Function to execute request
        :param location_index: Index of target location
        :param available_locations: List of available locations
        :param complete_event: Optional event to signal completion
        :param first_request_params_holder: a value holder for request object for first/initial request
        :param kwargs: Additional arguments for execute_request_fn
        :returns: Response tuple, exception, or None
        :rtype: Union[ResponseType, Exception, None]
        """
        if complete_status and complete_status.is_completed:
            return None

        # Create request parameters for this location
        params = copy.deepcopy(request_params)
        params.is_hedging_request = location_index > 0
        params.set_completion_status(complete_status)
        
        # Setup excluded regions for hedging requests
        params.excluded_locations = self.setup_excluded_regions_for_hedging(
            location_index,
            available_locations,
            request_params.excluded_locations
        )

        req = copy.deepcopy(request)

        # Calculate delay based on location index
        if location_index == 0:
            delay = 0  # No delay for initial request
            first_request_params_holder.request_params = params
        elif location_index == 1:
            # First hedged request after threshold
            delay = request_params.availability_strategy.threshold.total_seconds()
        else:
            # Subsequent requests after threshold steps
            steps = location_index - 1
            delay = (request_params.availability_strategy.threshold.total_seconds() +
                     (steps * request_params.availability_strategy.threshold_steps.total_seconds()))

        if delay > 0:
            await asyncio.sleep(delay)

        if complete_status and complete_status.is_completed:
            return None

        return await execute_request_fn(
            client,
            global_endpoint_manager,
            params,
            connection_policy,
            pipeline_client,
            req,
            **kwargs
        )

    async def execute_request(
        self,
        client: Any,
        request_params: Any,
        global_endpoint_manager: Any,
        connection_policy: Any,
        pipeline_client: Any,
        request: Any,
        execute_request_fn: Any,
        **kwargs: Any
    ) -> ResponseType:
        """Execute request with cross-region hedging."""
        # Get available locations from global endpoint manager
        available_locations = self._get_applicable_endpoints(request_params, global_endpoint_manager)

        # Filter out excluded locations
        if request_params.excluded_locations:
            available_locations = [loc for loc in available_locations
                                if loc not in request_params.excluded_locations]

        completion_status = SimpleNamespace(is_completed=False)
        tasks = []
        first_task: Optional[Task] = None
        first_request_params_holder: SimpleNamespace = SimpleNamespace(request_params=None)
        try:
            # Create tasks for each location
            for i in range(len(available_locations)):
                task = asyncio.create_task(
                    self.execute_single_request_with_delay(
                        client,
                        request_params,
                        global_endpoint_manager,
                        connection_policy,
                        pipeline_client,
                        request,
                        execute_request_fn,
                        i,
                        available_locations,
                        completion_status,
                        first_request_params_holder,
                        **kwargs
                    ))
                tasks.append(task)
                if i == 0:
                    first_task = task

            # Wait for tasks to complete
            for completed in asyncio.as_completed(tasks):
                try:
                    result = await completed
                    if completed is first_task:
                        completion_status.is_completed = True
                        return result
                    if result is not None:
                        completion_status.is_completed = True
                        await self._record_cancel_for_first_request(first_request_params_holder, global_endpoint_manager)
                        return result
                except Exception as e:
                    if completed is first_task:
                        completion_status.is_completed = True
                        raise e
                    if self._is_non_transient_error(e):
                        completion_status.is_completed = True
                        await self._record_cancel_for_first_request(first_request_params_holder, global_endpoint_manager)
                        raise e

            # if we have reached here, it means all tasks completed but all failed with transient exceptions
            # in this case, raise the exception from the first task
            completion_status.is_completed = True
            raise await first_task

        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _record_cancel_for_first_request(self, request_params_holder: SimpleNamespace, global_endpoint_manager: Any) -> None:
        if request_params_holder.request_params is not None:
            await global_endpoint_manager.record_failure(request_params_holder.request_params)

    def _get_applicable_endpoints(self, request: RequestObject, global_endpoint_manager: Any) -> List[str]:

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

def create_async_hedging_handler(strategy: Any) -> AsyncHedgingHandler:
    """Create appropriate hedging handler based on availability strategy type.
    
    :param strategy: The availability strategy to create a handler for
    :type strategy: Any
    :returns: An appropriate hedging handler for the strategy
    :rtype: AsyncHedgingHandler
    :raises ValueError: If the strategy type is not supported
    """
    if isinstance(strategy, DisabledStrategy):
        return DisabledAsyncHedgingHandler()
    elif isinstance(strategy, CrossRegionHedgingStrategy):
        return CrossRegionAsyncHedgingHandler()
    else:
        raise ValueError(f"Unsupported availability strategy type: {type(strategy)}")

async def execute_with_hedging(
    client: Any,
    request_params: Any,
    global_endpoint_manager: Any,
    connection_policy: Any,
    pipeline_client: Any,
    request: Any,
    execute_request_fn: Any,
    **kwargs: Any
) -> ResponseType:
    """Execute a request with hedging based on the availability strategy.
    
    :param client: Document client instance
    :param request_params: Request parameters
    :param global_endpoint_manager: Global endpoint manager
    :param connection_policy: Connection policy
    :param pipeline_client: Pipeline client
    :param request: HTTP request to execute
    :param execute_request_fn: Function to execute the request
    :param kwargs: Additional arguments for execute_request_fn
    :returns: Response tuple from successful request
    :rtype: ResponseType
    :raises: CosmosClientError if all hedged requests fail
    """
    handler = create_async_hedging_handler(request_params.availability_strategy)
    return await handler.execute_request(
        client,
        request_params,
        global_endpoint_manager,
        connection_policy,
        pipeline_client,
        request,
        execute_request_fn,
        **kwargs
    )