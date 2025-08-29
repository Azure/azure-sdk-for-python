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

"""Module for handling request availability strategies in Azure Cosmos DB."""
import copy
import time
from concurrent.futures import ThreadPoolExecutor, Future, as_completed, CancelledError
from types import SimpleNamespace
from typing import List, Dict, Any, Tuple, Callable, Optional, cast

from azure.core.pipeline.transport import HttpRequest  # pylint: disable=no-legacy-azure-core-http-response-import

from . import exceptions
from ._availability_strategy import CrossRegionHedgingStrategy
from ._global_partition_endpoint_manager_circuit_breaker import _GlobalPartitionEndpointManagerForCircuitBreaker
from ._request_hedging_completion_status import HedgingCompletionStatus, SyncHedgingCompletionStatus
from ._request_object import RequestObject
from .documents import _OperationType

ResponseType = Tuple[Dict[str, Any], Dict[str, Any]]

class CrossRegionHedgingHandler:
    """Handler for CrossRegionHedgingStrategy that implements cross-region request hedging."""

    def __init__(self) -> None:
        self._shared_executor = ThreadPoolExecutor()

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

    def _is_non_transient_error(self, result: BaseException) -> bool:
        """Check if exception represents a non-transient error.
        
        Determines if an error is non-transient based on HTTP status codes and sub-status.
        Non-transient errors include:
        - 400 Bad Request
        - 401 Unauthorized
        - 405 Method Not Allowed
        - 409 Conflict
        - 412 Precondition Failed
        - 413 Payload Too Large
        - 404 Not Found (only when sub_status is 0)
        
        :param result: The exception to evaluate
        :type result: BaseException
        :returns: True if the error is determined to be non-transient, False otherwise
        :rtype: bool
        """
        if isinstance(result, exceptions.CosmosHttpResponseError):
            # Check if error is non-transient
            status_code = result.status_code
            sub_status = result.sub_status
            return (status_code in [400, 409, 405, 412, 413, 401] or
                    (status_code == 404 and sub_status == 0))
        return False

    def execute_single_request_with_delay(
        self,
        request_params: RequestObject,
        request: HttpRequest,
        execute_request_fn: Callable[..., ResponseType],
        location_index: int,
        available_locations: List[str],
        complete_status: HedgingCompletionStatus,
        first_request_params_holder: SimpleNamespace
    ) -> ResponseType:
        """Execute a single request.

        :param request_params: Request parameters
        :type request_params: RequestObject
        :param request: HTTP request
        :type request: HttpRequest
        :param execute_request_fn: Function to execute request
        :type execute_request_fn: Callable[..., ResponseType]
        :param location_index: Index of target location
        :type location_index: int
        :param available_locations: List of available locations
        :type available_locations: List[str]
        :param complete_status: Value holder to track completion signal
        :type complete_status: SimpleNamespace
        :param first_request_params_holder: A value holder for request object for first/initial request
        :type first_request_params_holder: SimpleNamespace
        :returns: Response tuple
        :rtype: ResponseType
        """
        # Create request parameters for this location
        params = copy.deepcopy(request_params)
        params.set_is_hedging_request(location_index > 0)
        params.set_completion_status(complete_status)

        # Setup excluded regions for hedging requests
        params.excluded_locations = self._setup_excluded_regions_for_hedging(
            location_index,
            available_locations,
            request_params.excluded_locations
        )

        req = copy.deepcopy(request)

        if location_index == 0:
            # No delay for initial request
            delay: float = 0
            first_request_params_holder.request_params = params
        elif location_index == 1:
            # First hedged request after threshold
            delay = (cast(CrossRegionHedgingStrategy, request_params.availability_strategy)
                     .threshold
                     .total_seconds())
        else:
            # Subsequent requests after threshold steps
            steps = location_index - 1
            cross_region_hedging_strategy = cast(CrossRegionHedgingStrategy, request_params.availability_strategy)
            delay = (cross_region_hedging_strategy.threshold.total_seconds() +
                     (steps * cross_region_hedging_strategy.threshold_steps.total_seconds()))

        if delay > 0:
            time.sleep(delay)

        if complete_status.is_completed:
            raise CancelledError("The request has been cancelled")

        return execute_request_fn(params, req)

    def execute_request(
        self,
        request_params: RequestObject,
        global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreaker,
        request: HttpRequest,
        execute_request_fn: Callable[..., ResponseType]
    ) -> ResponseType:
        """Execute request with cross-region hedging strategy.

        :param request_params: Parameters for the request including operation type and strategy
        :type request_params: RequestObject
        :param global_endpoint_manager: Manager for handling global endpoints and circuit breaking
        :type global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreaker
        :param request: The HTTP request to be executed
        :type request: HttpRequest
        :param execute_request_fn: Function to execute the actual request
        :type execute_request_fn: Callable[..., ResponseType]
        :returns: A tuple containing the response data and headers
        :rtype: Tuple[Dict[str, Any], Dict[str, Any]]
        :raises: Exception from first request if all requests fail with transient errors
        """
        # Determine locations based on operation type
        available_locations = self._get_applicable_endpoints(request_params, global_endpoint_manager)
        effective_executor = self._get_effective_executor(request_params)

        futures: List[Future] = []
        first_request_future: Optional[Future] = None
        first_request_params_holder: SimpleNamespace = SimpleNamespace(request_params=None)
        completion_status = SyncHedgingCompletionStatus()

        for i in range(len(available_locations)):
            future = effective_executor.submit(
                self.execute_single_request_with_delay,
                request_params=request_params,
                request=request,
                execute_request_fn=execute_request_fn,
                location_index=i,
                available_locations=available_locations,
                complete_status=completion_status,
                first_request_params_holder=first_request_params_holder
            )
            futures.append(future)
            if i == 0:
                first_request_future = future

        for completed_future in as_completed(futures):
            exception = completed_future.exception()

            # if the result is from the first request, then always treat it as non-transient result
            if completed_future is first_request_future:
                completion_status.set_completed()
                if exception is None:
                    return completed_future.result()
                raise exception

            # non-first futures
            if exception is None:
                completion_status.set_completed()
                self._record_cancel_for_first_request(first_request_params_holder, global_endpoint_manager)
                return completed_future.result()
            if self._is_non_transient_error(exception):
                completion_status.set_completed()
                self._record_cancel_for_first_request(first_request_params_holder, global_endpoint_manager)
                raise exception

        # if we have reached here,it means all the futures have completed but all failed with transient exceptions
        # in this case, return the result from the first futures
        completion_status.set_completed()
        exc = cast(Future, first_request_future).exception()
        assert exc is not None
        raise exc

    def _get_effective_executor(self, request_param: RequestObject) -> ThreadPoolExecutor:
        if request_param.availability_strategy_executor is not None:
            return request_param.availability_strategy_executor
        return self._shared_executor

    def _record_cancel_for_first_request(
            self,
            request_params_holder: SimpleNamespace,
            global_endpoint_manager: Any) -> None:
        """Record failure for the first request when a subsequent hedged request succeeds.

        :param request_params_holder: Container holding the request parameters for the first request
        :type request_params_holder: SimpleNamespace
        :param global_endpoint_manager: Manager for endpoint routing and health tracking
        :type global_endpoint_manager: Any
        """
        if request_params_holder.request_params is not None:
            global_endpoint_manager.record_failure(request_params_holder.request_params)

    def _get_applicable_endpoints(self, request: RequestObject, global_endpoint_manager: Any) -> List[str]:
        """Get list of applicable endpoints for hedging based on operation type.

        :param request: Request object containing operation type and other parameters
        :type request: RequestObject
        :param global_endpoint_manager: Manager for endpoint routing and availability
        :type global_endpoint_manager: Any
        :returns: List of region names that can be used for hedging
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
_cross_region_hedging_handler = CrossRegionHedgingHandler()

def execute_with_hedging(
    request_params: RequestObject,
    global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreaker,
    request: HttpRequest,
    execute_request_fn: Callable[..., ResponseType]
) -> ResponseType:
    """Execute a request with hedging based on the availability strategy.

    :param request_params: Parameters for the request including operation type and strategy
    :type request_params: RequestObject
    :param global_endpoint_manager: Manager for handling global endpoints and circuit breaking
    :type global_endpoint_manager: _GlobalPartitionEndpointManagerForCircuitBreaker
    :param request: The HTTP request to be executed
    :type request: HttpRequest
    :param execute_request_fn: Function to execute the actual request
    :type execute_request_fn: Callable[..., ResponseType]
    :returns: A tuple containing the response data and headers
    :rtype: Tuple[Dict[str, Any], Dict[str, Any]]
    :raises: Any exceptions raised by the hedging handler's execute_request method
    """
    availability_strategy = request_params.availability_strategy
    if isinstance(availability_strategy, CrossRegionHedgingStrategy):
        return _cross_region_hedging_handler.execute_request(
            request_params,
            global_endpoint_manager,
            request,
            execute_request_fn
        )
    raise ValueError("Unsupported availability strategy type: {0}".format(CrossRegionHedgingStrategy.__class__))

