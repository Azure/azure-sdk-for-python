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
import asyncio  # pylint: disable=do-not-import-asyncio
import copy
import logging
from asyncio import Task, CancelledError
from types import SimpleNamespace
from typing import Any, Dict, List, Optional, Tuple, Callable, Awaitable, TYPE_CHECKING, cast

from azure.core import AsyncPipelineClient
from azure.core.pipeline.transport import HttpRequest, \
    AsyncHttpResponse  # pylint: disable=no-legacy-azure-core-http-response-import

from ._global_partition_endpoint_manager_circuit_breaker_async import \
    _GlobalPartitionEndpointManagerForCircuitBreakerAsync
from .._availability_strategy import CrossRegionHedgingStrategy, DisabledStrategy, AvailabilityStrategy
from .._request_object import RequestObject
from ..documents import _OperationType, ConnectionPolicy
from ..exceptions import CosmosHttpResponseError

if TYPE_CHECKING:
    from . import CosmosClient

logger = logging.getLogger(__name__)
ResponseType = Tuple[Dict[str, Any], Dict[str, Any]]

class AsyncHedgingHandler(abc.ABC):
    """Abstract base class for async hedging handlers."""

    @abc.abstractmethod
    async def execute_request(
        self,
        client: "CosmosClient",
        request_params: RequestObject,
        global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreakerAsync,
        connection_policy: ConnectionPolicy,
        pipeline_client: AsyncPipelineClient[HttpRequest, AsyncHttpResponse],
        request: HttpRequest,
        execute_request_fn: Callable[..., Awaitable[ResponseType]],
        **kwargs: Any
    ) -> ResponseType:
        """Execute an async request with the appropriate hedging behavior.

        :param client: The Cosmos client instance making the request
        :type client: CosmosClient
        :param request_params: Parameters for the request including operation type and strategy
        :type request_params: RequestObject
        :param global_endpoint_manager: Manager for handling global endpoints and circuit breaking
        :type global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreakerAsync
        :param connection_policy: Policy defining connection behaviors and preferences
        :type connection_policy: ConnectionPolicy
        :param pipeline_client: Client for executing the async HTTP pipeline
        :type pipeline_client: AsyncPipelineClient[HttpRequest, AsyncHttpResponse]
        :param request: The HTTP request to be executed
        :type request: HttpRequest
        :param execute_request_fn: Async function to execute the actual request
        :type execute_request_fn: Callable[..., Awaitable[ResponseType]]
        :returns: A tuple containing the response data and headers
        :rtype: Tuple[Dict[str, Any], Dict[str, Any]]
        """

class DisabledAsyncHedgingHandler(AsyncHedgingHandler):
    """Handler for DisabledStrategy that executes requests directly."""

    async def execute_request(
        self,
        client: "CosmosClient",
        request_params: RequestObject,
        global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreakerAsync,
        connection_policy: ConnectionPolicy,
        pipeline_client: AsyncPipelineClient[HttpRequest, AsyncHttpResponse],
        request: HttpRequest,
        execute_request_fn: Callable[..., Awaitable[ResponseType]],
        **kwargs: Any
    ) -> ResponseType:
        """Execute async request without any hedging behavior.

        This implementation directly executes the async request without hedging strategy,
        suitable for scenarios where hedging is explicitly disabled.

        :param client: The Cosmos client instance making the request
        :type client: CosmosClient
        :param request_params: Parameters for the request including operation type and strategy
        :type request_params: RequestObject
        :param global_endpoint_manager: Manager for handling global endpoints and circuit breaking
        :type global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreakerAsync
        :param connection_policy: Policy defining connection behaviors and preferences
        :type connection_policy: ConnectionPolicy
        :param pipeline_client: Client for executing the async HTTP pipeline
        :type pipeline_client: AsyncPipelineClient[HttpRequest, AsyncHttpResponse]
        :param request: The HTTP request to be executed
        :type request: HttpRequest
        :param execute_request_fn: Async function to execute the actual request
        :type execute_request_fn: Callable[..., Awaitable[ResponseType]]
        :returns: A tuple containing the response data and headers
        :rtype: Tuple[Dict[str, Any], Dict[str, Any]]
        """
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
        client: "CosmosClient",
        request_params: RequestObject,
        global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreakerAsync,
        connection_policy: ConnectionPolicy,
        pipeline_client: AsyncPipelineClient[HttpRequest, AsyncHttpResponse],
        request: HttpRequest,
        execute_request_fn: Callable[..., Awaitable[ResponseType]],
        location_index: int,
        available_locations: List[str],
        complete_status: SimpleNamespace,
        first_request_params_holder: SimpleNamespace,
        **kwargs: Any
    ) -> ResponseType:
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
        :returns: Response
        :rtype: ResponseType
        """

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
            delay: float = 0  # No delay for initial request
            first_request_params_holder.request_params = params
        elif location_index == 1:
            # First hedged request after threshold
            delay: float = cast(CrossRegionHedgingStrategy, request_params.availability_strategy).threshold.total_seconds()
        else:
            # Subsequent requests after threshold steps
            steps = location_index - 1
            cross_region_hedging_strategy = cast(CrossRegionHedgingStrategy, request_params.availability_strategy)
            delay: float = (cross_region_hedging_strategy.threshold.total_seconds() +
                     (steps * cross_region_hedging_strategy.threshold_steps.total_seconds()))

        if delay > 0:
            await asyncio.sleep(delay)

        if complete_status and complete_status.is_completed:
            raise CancelledError("The request has been cancelled")

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
        client: "CosmosClient",
        request_params: RequestObject,
        global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreakerAsync,
        connection_policy: ConnectionPolicy,
        pipeline_client: AsyncPipelineClient[HttpRequest, AsyncHttpResponse],
        request: HttpRequest,
        execute_request_fn: Callable[..., Awaitable[ResponseType]],
        **kwargs: Any
    ) -> ResponseType:
        """Execute request with cross-region hedging strategy.

        This method implements an asynchronous request hedging strategy across multiple regions.
        It creates parallel tasks for each available endpoint with appropriate delays between
        requests. The first successful response is returned while other pending requests are
        cancelled. If the first request fails but a subsequent request succeeds, the failure
        of the first request is recorded.

        :param client: The Cosmos client instance making the request
        :type client: CosmosClient
        :param request_params: Parameters for the request including operation type and strategy
        :type request_params: RequestObject
        :param global_endpoint_manager: Manager for handling global endpoints and circuit breaking
        :type global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreakerAsync
        :param connection_policy: Policy defining connection behaviors and preferences
        :type connection_policy: ConnectionPolicy
        :param pipeline_client: Client for executing the async HTTP pipeline
        :type pipeline_client: AsyncPipelineClient[HttpRequest, AsyncHttpResponse]
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
                    completion_status.is_completed = True

                    if completed is first_task:
                        return result

                    # successful response does not come from the initial request, record failure for it
                    await self._record_cancel_for_first_request(first_request_params_holder, global_endpoint_manager)
                    return result
                except Exception as e:
                    if completed is first_task:
                        completion_status.is_completed = True
                        raise e
                    if self._is_non_transient_error(e):
                        completion_status.is_completed = True
                        await self._record_cancel_for_first_request(
                            first_request_params_holder,
                            global_endpoint_manager)
                        raise e

            # if we have reached here, it means all tasks completed but all failed with transient exceptions
            # in this case, raise the exception from the first task
            completion_status.is_completed = True
            assert first_task is not None
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

def create_async_hedging_handler(strategy: Optional[AvailabilityStrategy]) -> AsyncHedgingHandler:
    """Create appropriate hedging handler based on availability strategy type.
    
    :param strategy: The availability strategy to create a handler for
    :type strategy: Any
    :returns: An appropriate hedging handler for the strategy
    :rtype: AsyncHedgingHandler
    :raises ValueError: If the strategy type is not supported
    """

    if strategy is None:
        raise ValueError("Strategy can not be null in create_async_hedging_handler")

    if isinstance(strategy, DisabledStrategy):
        return DisabledAsyncHedgingHandler()
    elif isinstance(strategy, CrossRegionHedgingStrategy):
        return CrossRegionAsyncHedgingHandler()
    else:
        raise ValueError(f"Unsupported availability strategy type: {type(strategy)}")

async def execute_with_hedging(
    client: "CosmosClient",
    request_params: RequestObject,
    global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreakerAsync,
    connection_policy: ConnectionPolicy,
    pipeline_client: AsyncPipelineClient[HttpRequest, AsyncHttpResponse],
    request: HttpRequest,
    execute_request_fn: Callable[..., Awaitable[ResponseType]],
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
