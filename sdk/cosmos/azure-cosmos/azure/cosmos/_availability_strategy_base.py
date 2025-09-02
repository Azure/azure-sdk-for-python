# The MIT License (MIT)
# Copyright (c) 2021 Microsoft Corporation

"""Module containing base classes and mixins for availability strategy handlers."""

from typing import List, Optional, Union, TYPE_CHECKING

from . import exceptions
from ._request_object import RequestObject
from .documents import _OperationType

if TYPE_CHECKING:
    from ._global_partition_endpoint_manager_circuit_breaker import _GlobalPartitionEndpointManagerForCircuitBreaker
    from .aio._global_partition_endpoint_manager_circuit_breaker_async import _GlobalPartitionEndpointManagerForCircuitBreakerAsync

GlobalEndpointManagerType = Union['_GlobalPartitionEndpointManagerForCircuitBreaker', 
                                '_GlobalPartitionEndpointManagerForCircuitBreakerAsync']

class AvailabilityStrategyMixin:
    """Mixin class providing shared functionality for availability strategy handlers."""

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

    def _is_non_transient_error(self, result: Exception) -> bool:
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
        :type result: Exception
        :returns: True if the error is determined to be non-transient, False otherwise
        :rtype: bool
        """
        if isinstance(result, exceptions.CosmosHttpResponseError):
            status_code = result.status_code
            sub_status = result.sub_status
            return (status_code in [400, 409, 405, 412, 413, 401] or
                    (status_code == 404 and sub_status == 0))
        return False

    def _get_applicable_endpoints(self, request: RequestObject, global_endpoint_manager: GlobalEndpointManagerType) -> List[str]:
        """Get list of applicable endpoints for hedging based on operation type.
        
        :param request: Request object containing operation type and other parameters
        :type request: RequestObject
        :param global_endpoint_manager: Manager for endpoint routing and availability
        :type global_endpoint_manager: Union[_GlobalPartitionEndpointManagerForCircuitBreaker, _GlobalPartitionEndpointManagerForCircuitBreakerAsync]
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