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

"""Module containing base classes and mixins for availability strategy handlers."""

from typing import List, Optional, Union, TYPE_CHECKING

from . import exceptions
from ._location_cache import RegionalRoutingContext
from ._request_object import RequestObject

from .documents import _OperationType
from .http_constants import StatusCodes, SubStatusCodes

GlobalEndpointManagerType = Union['_GlobalPartitionEndpointManagerForCircuitBreaker',
                                '_GlobalPartitionEndpointManagerForCircuitBreakerAsync']

if TYPE_CHECKING:
    from ._global_partition_endpoint_manager_circuit_breaker import _GlobalPartitionEndpointManagerForCircuitBreaker
    from .aio._global_partition_endpoint_manager_circuit_breaker_async import \
        _GlobalPartitionEndpointManagerForCircuitBreakerAsync

class AvailabilityStrategyHandlerMixin:
    """Mixin class providing shared functionality for availability strategy handlers."""

    def _create_excluded_regions_for_hedging(
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
            excluded += available_locations[:location_index] + available_locations[location_index+1:]

        return excluded

    def _is_non_transient_error(self, result: BaseException) -> bool:
        """Check if exception represents a non-transient error.

        :param result: The exception to evaluate
        :type result: Exception
        :returns: True if the error is determined to be non-transient, False otherwise
        :rtype: bool
        """
        if isinstance(result, exceptions.CosmosHttpResponseError):
            status_code = result.status_code
            sub_status = result.sub_status
            non_transient_status_codes = [
                StatusCodes.BAD_REQUEST,
                StatusCodes.CONFLICT,
                StatusCodes.METHOD_NOT_ALLOWED,
                StatusCodes.PRECONDITION_FAILED,
                StatusCodes.REQUEST_ENTITY_TOO_LARGE,
                StatusCodes.UNAUTHORIZED
            ]
            return (status_code in non_transient_status_codes or
                    (status_code == StatusCodes.NOT_FOUND and sub_status == SubStatusCodes.UNKNOWN))
        return False

    def _get_applicable_endpoints(
            self,
            request: RequestObject, global_endpoint_manager: GlobalEndpointManagerType) -> List[str]:
        """Get list of applicable endpoints for hedging based on operation type.
        
        :param request: Request object containing operation type and other parameters
        :type request: RequestObject
        :param global_endpoint_manager: Manager for endpoint routing and availability
        :type global_endpoint_manager: Any
        :returns: List of region names that can be used for hedging
        :rtype: List[str]
        """
        applicable_endpoints: List[str] = []
        regional_context_list: List[RegionalRoutingContext]
        if _OperationType.IsWriteOperation(request.operation_type):
            regional_context_list = global_endpoint_manager.get_applicable_write_regional_routing_contexts(request)
        else:
            regional_context_list = global_endpoint_manager.get_applicable_read_regional_routing_contexts(request)

        if regional_context_list:
            for regional_context in regional_context_list:
                region_name = (
                    global_endpoint_manager.get_region_name(
                        regional_context.get_primary(),
                        _OperationType.IsWriteOperation(request.operation_type)))
                if region_name is not None:
                    applicable_endpoints.append(region_name)

        return applicable_endpoints
