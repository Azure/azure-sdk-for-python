# The MIT License (MIT)
# Copyright (c) 2025 Microsoft Corporation

"""Class for global endpoint manager for per partition automatic failover. This class inherits the circuit breaker
endpoint manager, since enabling per partition automatic failover also enables the circuit breaker logic.
"""
import logging
import os
import threading

from typing import Dict, Set, TYPE_CHECKING, Optional

from azure.cosmos.http_constants import ResourceType
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos.aio._global_partition_endpoint_manager_circuit_breaker_async import \
    _GlobalPartitionEndpointManagerForCircuitBreakerAsync
from azure.cosmos.documents import _OperationType

from azure.cosmos._request_object import RequestObject
from azure.cosmos._routing.routing_range import PartitionKeyRangeWrapper

if TYPE_CHECKING:
    from azure.cosmos.aio._cosmos_client_connection_async import CosmosClientConnection

logger = logging.getLogger("azure.cosmos._GlobalPartitionEndpointManagerForPerPartitionAutomaticFailover")

# pylint: disable=name-too-long, protected-access

class PartitionLevelFailoverInfo:
    """
    Holds information about the partition level regional failover.
    Used to track the partition key range and the regions where it is available.
    """
    def __init__(self):
        self.unavailable_regional_endpoints = set()
        self.current_regional_endpoint = None
        self._lock = threading.Lock()

    def try_move_to_next_location(self, available_account_regional_endpoints: Set[str], request: RequestObject) -> bool:
        with self._lock:
            failed_regional_endpoint = request.location_endpoint_to_route
            if failed_regional_endpoint != self.current_regional_endpoint:
                logger.info("Moving to next available regional endpoint: %s", self.current_regional_endpoint)
                request.route_to_location(self.current_regional_endpoint)
                return True

            for regional_endpoint in available_account_regional_endpoints:
                if regional_endpoint == self.current_regional_endpoint:
                    continue

                if regional_endpoint in self.unavailable_regional_endpoints:
                    continue

                self.current_regional_endpoint = regional_endpoint
                logger.info("Moving to next available regional endpoint: %s", self.current_regional_endpoint)
                request.route_to_location(self.current_regional_endpoint)
                return True

            return False

class _GlobalPartitionEndpointManagerForPerPartitionAutomaticFailoverAsync(
    _GlobalPartitionEndpointManagerForCircuitBreakerAsync):
    """
    This internal class implements the logic for partition endpoint management for
    geo-replicated database accounts.
    """
    def __init__(self, client: "CosmosClientConnection"):
        super(_GlobalPartitionEndpointManagerForPerPartitionAutomaticFailoverAsync, self).__init__(client)
        self.partition_range_to_failover_info: Dict[PartitionKeyRangeWrapper, PartitionLevelFailoverInfo] = {}

    def is_per_partition_automatic_failover_applicable(self, request: RequestObject) -> bool:
        if not request:
            return False

        if (self.location_cache.can_use_multiple_write_locations_for_request(request)
                or _OperationType.IsReadOnlyOperation(request.operation_type)):
            return False

        # TODO: This check here needs to be verified once we test against a live account with the config enabled.
        if not self._database_account_cache._EnablePerPartitionFailoverBehavior:
            return False

        # if we have at most one region available in the account, we cannot do per partition automatic failover
        available_regions = self.compute_available_preferred_regions(request)
        if len(available_regions) <= 1:
            return False

        # if the request is not for a document or if the request is not executing a stored procedure, return False
        if (request.resource_type != ResourceType.Document and
                request.operation_type != _OperationType.ExecuteJavaScript):
            return False

        return True

    def resolve_service_endpoint_for_partition(
            self,
            request: RequestObject,
            pk_range_wrapper: Optional[PartitionKeyRangeWrapper]
    ) -> str:
        if self.is_per_partition_automatic_failover_applicable(request) and pk_range_wrapper:
            # If per partition automatic failover is applicable, we check partition unavailability
            if pk_range_wrapper in self.partition_range_to_failover_info:
                logger.info("Resolving service endpoint for partition with per partition automatic failover enabled.")
                partition_failover_info = self.partition_range_to_failover_info[pk_range_wrapper]
                if request.location_endpoint_to_route is not None:
                    if request.location_endpoint_to_route in partition_failover_info.unavailable_regional_endpoints:
                        # If the current region is unavailable, we try to move to the next available region
                        if not partition_failover_info.try_move_to_next_location(
                                self.compute_available_preferred_regions(request),
                                request):
                            logger.info("All available regions for partition are unavailable. Refreshing cache.")
                            # If no other region is available, we invalidate the cache and start once again from our
                            # main write region in the account configurations
                            self.partition_range_to_failover_info[pk_range_wrapper] = PartitionLevelFailoverInfo()
                            request.clear_route_to_location()
                            return self._resolve_service_endpoint(request)
                    else:
                        # Update the current regional endpoint to whatever the request is routing to
                        partition_failover_info.current_regional_endpoint = request.location_endpoint_to_route
            else:
                partition_failover_info = PartitionLevelFailoverInfo()
                partition_failover_info.current_regional_endpoint = request.location_endpoint_to_route
                self.partition_range_to_failover_info[pk_range_wrapper] = partition_failover_info
            return self._resolve_service_endpoint(request)
        return self._resolve_service_endpoint_for_partition_circuit_breaker(request, pk_range_wrapper)

    def compute_available_preferred_regions(
            self,
            request: RequestObject
    ) -> Set[str]:
        """
        Computes the available regional endpoints for the request based on customer-set preferred and excluded regions.
        :param RequestObject request: The request object containing the routing context.
        :return: A set of available regional endpoints.
        :rtype: Set[str]
        """
        excluded_locations = request.excluded_locations + self.location_cache.connection_policy.ExcludedLocations
        preferred_locations = self.PreferredLocations
        available_regions = [item for item in preferred_locations if item not in excluded_locations]
        available_regional_endpoints = {
            self.location_cache.account_read_regional_routing_contexts_by_location[region].primary_endpoint
            for region in available_regions
        }
        return available_regional_endpoints
