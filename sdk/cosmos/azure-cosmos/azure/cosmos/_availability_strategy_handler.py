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

"""Module for handling request availability strategies in Azure Cosmos DB."""
import copy
import os
import time
from concurrent.futures import ThreadPoolExecutor, Future, as_completed, CancelledError
from threading import Event
from types import SimpleNamespace
from typing import List, Dict, Any, Tuple, Callable, Optional, cast

from azure.core.pipeline.transport import HttpRequest  # pylint: disable=no-legacy-azure-core-http-response-import

from ._availability_strategy_handler_base import AvailabilityStrategyHandlerMixin
from ._global_partition_endpoint_manager_circuit_breaker import _GlobalPartitionEndpointManagerForCircuitBreaker
from ._request_object import RequestObject

ResponseType = Tuple[Dict[str, Any], Dict[str, Any]]

class CrossRegionHedgingHandler(AvailabilityStrategyHandlerMixin):
    """Handler for CrossRegionHedgingStrategy that implements cross-region request hedging."""

    def __init__(self) -> None:
        self._shared_executor = ThreadPoolExecutor(max_workers=os.cpu_count())

    def execute_single_request_with_delay(
        self,
        request_params: RequestObject,
        request: HttpRequest,
        execute_request_fn: Callable[..., ResponseType],
        location_index: int,
        available_locations: List[str],
        complete_status: Event,
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
        :type complete_status: threading.Event
        :param first_request_params_holder: A value holder for request object for first/initial request
        :type first_request_params_holder: SimpleNamespace
        :returns: Response tuple
        :rtype: ResponseType
        """

        availability_strategy_config = request_params.availability_strategy_config
        if availability_strategy_config is None:
            raise ValueError("availability_strategy_config should not be null")

        delay: int
        if location_index == 0:
            # No delay for initial request
            delay = 0
        elif location_index == 1:
            # First hedged request after threshold
            delay = availability_strategy_config.threshold_ms
        else:
            # Subsequent requests after threshold steps
            steps = location_index - 1
            delay = (availability_strategy_config.threshold_ms +
                    (steps * availability_strategy_config.threshold_steps_ms))

        if delay > 0:
            time.sleep(delay / 1000)

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

        if complete_status.is_set():
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
        effective_executor = request_params.availability_strategy_executor or self._shared_executor

        # reset the executor here else will get cannot pickle '_queue.SimpleQueue' object
        request_params.availability_strategy_executor = None

        futures: List[Future] = []
        first_request_future: Optional[Future] = None
        first_request_params_holder: SimpleNamespace = SimpleNamespace(request_params=None)
        completion_status = Event()

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
                completion_status.set()
                if exception is None:
                    return completed_future.result()
                raise exception

            # non-first futures
            if exception is None:
                completion_status.set()
                self._record_cancel_for_first_request(first_request_params_holder, global_endpoint_manager)
                return completed_future.result()

            if self._is_non_transient_error(exception):
                completion_status.set()
                self._record_cancel_for_first_request(first_request_params_holder, global_endpoint_manager)
                raise exception

        # if we have reached here,it means all the futures have completed but all failed with transient exceptions
        # in this case, return the result from the first futures
        completion_status.set()
        exc = cast(Future, first_request_future).exception()
        assert exc is not None
        raise exc

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
    return _cross_region_hedging_handler.execute_request(
        request_params,
        global_endpoint_manager,
        request,
        execute_request_fn
    )
