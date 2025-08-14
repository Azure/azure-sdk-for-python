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

"""Module for handling request hedging strategies in Azure Cosmos DB."""
import abc
import copy
import threading
import time
from concurrent.futures import ThreadPoolExecutor, Future, as_completed, CancelledError
from threading import Event
from types import SimpleNamespace
from typing import List, Dict, Any, Tuple, Callable, Union, Optional

from . import exceptions
from ._availability_strategy import CrossRegionHedgingStrategy, DisabledStrategy
from ._request_object import RequestObject
from .documents import _OperationType

ResponseType = Tuple[Dict[str, Any], Dict[str, Any]]

class HedgingHandler(abc.ABC):
    """Abstract base class for hedging handlers."""
    
    @abc.abstractmethod
    def execute_request(
        self,
        client: Any,
        request_params: Any,
        global_endpoint_manager: Any,
        connection_policy: Any,
        pipeline_client: Any,
        request: Any,
        execute_request_fn: Callable,
        **kwargs: Any
    ) -> ResponseType:
        """Execute a request with the appropriate hedging behavior."""
        pass

class DisabledHedgingHandler(HedgingHandler):
    """Handler for DisabledStrategy that executes requests directly."""

    def execute_request(
        self,
        client: Any,
        request_params: Any,
        global_endpoint_manager: Any,
        connection_policy: Any,
        pipeline_client: Any,
        request: Any,
        execute_request_fn: Callable,
        **kwargs: Any
    ) -> ResponseType:
        """Execute request without hedging."""
        return execute_request_fn(
            client,
            global_endpoint_manager,
            request_params,
            connection_policy,
            pipeline_client,
            request,
            **kwargs
        )

class CrossRegionHedgingHandler(HedgingHandler):
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
        """Check if exception represents a non-transient error.
        
        :param result: exception
        :type result: Exception
        :returns: True if result is either successful or a non-transient error
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
        client: Any,
        request_params: RequestObject,
        global_endpoint_manager: Any,
        connection_policy: Any,
        pipeline_client: Any,
        request: Any,
        execute_request_fn: Callable,
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
        :param complete_event: Event to signal completion
        :param first_request_params_holder: a value holder for request object for first/initial request
        :param kwargs: Additional arguments for execute_request_fn
        :returns: Response tuple, exception, or None
        :rtype: Union[ResponseType, Exception, None]
        """
        # Create request parameters for this location
        params = copy.deepcopy(request_params)
        params.set_is_hedging_request(location_index > 0)
        params.set_completion_status(complete_status)
        
        # Setup excluded regions for hedging requests
        params.excluded_locations = self.setup_excluded_regions_for_hedging(
            location_index,
            available_locations,
            request_params.excluded_locations
        )

        req = copy.deepcopy(request)

        if location_index == 0:
            # No delay for initial request
            delay = 0
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
            time.sleep(delay)

        if complete_status.is_completed:
            raise CancelledError("The hedging request has been cancelled")

        return execute_request_fn(
            client,
            global_endpoint_manager,
            params,
            connection_policy,
            pipeline_client,
            req,
            **kwargs
        )

    def execute_request(
        self,
        client: Any,
        request_params: Any,
        global_endpoint_manager: Any,
        connection_policy: Any,
        pipeline_client: Any,
        request: Any,
        execute_request_fn: Callable,
        **kwargs: Any
    ) -> ResponseType:
        """Execute request with cross-region hedging."""
        # Determine locations based on operation type
        available_locations = self._get_applicable_endpoints(request_params, global_endpoint_manager)
        executor = ThreadPoolExecutor(max_workers=len(available_locations))

        try:
            futures: List[Future] = []
            first_request_future: Optional[Future] = None
            first_request_params_holder: SimpleNamespace = SimpleNamespace(request_params=None)
            completion_status = SimpleNamespace(is_completed=False)

            for i in range(len(available_locations)):
                future = executor.submit(
                        self.execute_single_request_with_delay,
                        client=client,
                        request_params=request_params,
                        global_endpoint_manager=global_endpoint_manager,
                        connection_policy=connection_policy,
                        pipeline_client=pipeline_client,
                        request=request,
                        execute_request_fn=execute_request_fn,
                        location_index=i,
                        available_locations=available_locations,
                        complete_status=completion_status,
                        first_request_params_holder=first_request_params_holder,
                        ** kwargs
                    )
                futures.append(future)
                if i == 0:
                    first_request_future = future

            for fut in as_completed(futures):
                # if the result is from the first request, then always treat it as non-transient result
                exception = fut.exception()

                # first future: always non-transient
                if fut is first_request_future:
                    completion_status.is_completed = True
                    if exception is None:
                        return fut.result()
                    raise exception

                # non-first futures
                if exception is None:
                    completion_status.is_completed = True
                    self._record_cancel_for_first_request(first_request_params_holder, global_endpoint_manager)
                    return fut.result()
                if self._is_non_transient_error(exception):
                    completion_status.is_completed = True
                    self._record_cancel_for_first_request(first_request_params_holder, global_endpoint_manager)
                    raise exception

            # if we have reached here,it means all the futures have completed but all failed with transient exceptions
            # in this case, return the result from the first futures
            completion_status.is_completed = True
            raise first_request_future.exception()
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

    def _record_cancel_for_first_request(self, request_params_holder: SimpleNamespace, global_endpoint_manager: Any) -> None:
        if request_params_holder.request_params is not None:
            global_endpoint_manager.record_failure(request_params_holder.request_params)

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

def create_hedging_handler(strategy: Any) -> HedgingHandler:
    """Create appropriate hedging handler based on availability strategy type."""
    if isinstance(strategy, DisabledStrategy):
        return DisabledHedgingHandler()
    elif isinstance(strategy, CrossRegionHedgingStrategy):
        return CrossRegionHedgingHandler()
    else:
        raise ValueError(f"Unsupported availability strategy type: {type(strategy)}")

def execute_with_hedging(
    client: Any,
    request_params: Any,
    global_endpoint_manager: Any,
    connection_policy: Any,
    pipeline_client: Any,
    request: Any,
    execute_request_fn: Callable,
    **kwargs: Any
) -> ResponseType:
    """Execute a request with hedging based on the availability strategy."""
    handler = create_hedging_handler(request_params.availability_strategy)
    return handler.execute_request(
        client,
        request_params,
        global_endpoint_manager,
        connection_policy,
        pipeline_client,
        request,
        execute_request_fn,
        **kwargs
    )