# The MIT License (MIT)
# Copyright (c) 2025 Microsoft Corporation

"""Class for global endpoint manager for per partition automatic failover. This class inherits the circuit breaker
endpoint manager, since enabling per partition automatic failover also enables the circuit breaker logic.
"""
import logging
import threading
import os

from typing import TYPE_CHECKING, Optional

from azure.cosmos.http_constants import ResourceType
from azure.cosmos._constants import _Constants as Constants
from azure.cosmos._global_partition_endpoint_manager_circuit_breaker import \
    _GlobalPartitionEndpointManagerForCircuitBreaker
from azure.cosmos._partition_health_tracker import _PPAFPartitionThresholdsTracker
from azure.cosmos.documents import _OperationType
from azure.cosmos._request_object import RequestObject
from azure.cosmos._routing.routing_range import PartitionKeyRangeWrapper

if TYPE_CHECKING:
    from azure.cosmos._cosmos_client_connection import CosmosClientConnection
    from azure.cosmos._location_cache import RegionalRoutingContext

logger = logging.getLogger("azure.cosmos._GlobalPartitionEndpointManagerForPerPartitionAutomaticFailover")

# pylint: disable=name-too-long, protected-access, too-many-nested-blocks
#cspell:ignore PPAF, ppaf, ppcb

class PartitionLevelFailoverInfo:
    """
    Holds information about the partition level regional failover.
    Used to track the partition key range and the regions where it is available.
    """
    def __init__(self) -> None:
        self.unavailable_regional_endpoints: dict[str, "RegionalRoutingContext"] = {}
        self._lock = threading.Lock()
        self.current_region: Optional[str] = None

    def try_move_to_next_location(
            self,
            available_account_regional_endpoints: dict[str, "RegionalRoutingContext"],
            endpoint_region: str,
            request: RequestObject) -> bool:
        """
        Tries to move to the next available regional endpoint for the partition key range.
        :param Dict[str, RegionalRoutingContext] available_account_regional_endpoints: The available regional endpoints
        :param str endpoint_region: The current regional endpoint
        :param RequestObject request: The request object containing the routing context.
        :return: True if the move was successful, False otherwise.
        :rtype: bool
        """
        with self._lock:
            if endpoint_region != self.current_region and self.current_region is not None:
                regional_endpoint = available_account_regional_endpoints[self.current_region]
                request.route_to_location(regional_endpoint.primary_endpoint)
                return True

            for regional_endpoint in available_account_regional_endpoints:
                if regional_endpoint == self.current_region:
                    continue

                if regional_endpoint in self.unavailable_regional_endpoints:
                    continue

                self.current_region = regional_endpoint
                logger.warning("PPAF - Moving to next available regional endpoint: %s", self.current_region)
                regional_endpoint = available_account_regional_endpoints[self.current_region]
                request.route_to_location(regional_endpoint.primary_endpoint)
                return True

            return False

class _GlobalPartitionEndpointManagerForPerPartitionAutomaticFailover(_GlobalPartitionEndpointManagerForCircuitBreaker):
    """
    This internal class implements the logic for partition endpoint management for
    geo-replicated database accounts.
    """
    def __init__(self, client: "CosmosClientConnection") -> None:
        super(_GlobalPartitionEndpointManagerForPerPartitionAutomaticFailover, self).__init__(client)
        self.partition_range_to_failover_info: dict[PartitionKeyRangeWrapper, PartitionLevelFailoverInfo] = {}
        self.ppaf_thresholds_tracker = _PPAFPartitionThresholdsTracker()
        self._threshold_lock = threading.Lock()

    def is_per_partition_automatic_failover_enabled(self) -> bool:
        if not self._database_account_cache or not self._database_account_cache._EnablePerPartitionFailoverBehavior:
            return False
        return True

    def is_per_partition_automatic_failover_applicable(self, request: RequestObject) -> bool:
        if not self.is_per_partition_automatic_failover_enabled():
            return False

        if not request:
            return False

        if (self.location_cache.can_use_multiple_write_locations_for_request(request)
                or _OperationType.IsReadOnlyOperation(request.operation_type)):
            return False

        # if we have at most one region available in the account, we cannot do per partition automatic failover
        available_regions = self.location_cache.account_read_regional_routing_contexts_by_location
        if len(available_regions) <= 1:
            return False

        # if the request is not a non-query plan document request
        # or if the request is not executing a stored procedure, return False
        if (request.resource_type != ResourceType.Document and
                request.operation_type != _OperationType.ExecuteJavaScript):
            return False

        return True

    def try_ppaf_failover_threshold(
            self,
            pk_range_wrapper: "PartitionKeyRangeWrapper",
            request: "RequestObject"):
        """Verifies whether the per-partition failover threshold has been reached for consecutive errors. If so,
        it marks the current region as unavailable for the given partition key range, and moves to the next available
        region for the request.

        :param PartitionKeyRangeWrapper pk_range_wrapper: The wrapper containing the partition key range information
            for the request.
        :param RequestObject request: The request object containing the routing context.
        :returns: None
        """
        # If PPAF is enabled, we track consecutive failures for certain exceptions, and only fail over at a partition
        # level after the threshold is reached
        if request and self.is_per_partition_automatic_failover_applicable(request):
            if (self.ppaf_thresholds_tracker.get_pk_failures(pk_range_wrapper)
                    >= int(os.environ.get(Constants.TIMEOUT_ERROR_THRESHOLD_PPAF,
                                          Constants.TIMEOUT_ERROR_THRESHOLD_PPAF_DEFAULT))):
                # If the PPAF threshold is reached, we reset the count and mark the endpoint unavailable
                # Once we mark the endpoint unavailable, the PPAF endpoint manager will try to move to the next
                # available region for the partition key range
                with self._threshold_lock:
                    # Check for count again, since a previous request may have now reset the count
                    if (self.ppaf_thresholds_tracker.get_pk_failures(pk_range_wrapper)
                            >= int(os.environ.get(Constants.TIMEOUT_ERROR_THRESHOLD_PPAF,
                                                  Constants.TIMEOUT_ERROR_THRESHOLD_PPAF_DEFAULT))):
                        self.ppaf_thresholds_tracker.clear_pk_failures(pk_range_wrapper)
                        partition_level_info = self.partition_range_to_failover_info[pk_range_wrapper]
                        location = self.location_cache.get_location_from_endpoint(
                            str(request.location_endpoint_to_route))
                        logger.warning("PPAF - Failover threshold reached for partition key range: %s for region: %s", #pylint: disable=line-too-long
                                       pk_range_wrapper, location)
                        regional_context = (self.location_cache.
                                            account_read_regional_routing_contexts_by_location.
                                            get(location).primary_endpoint)
                        partition_level_info.unavailable_regional_endpoints[location] = regional_context

    def resolve_service_endpoint_for_partition(
            self,
            request: RequestObject,
            pk_range_wrapper: Optional[PartitionKeyRangeWrapper]
    ) -> str:
        """Resolves the endpoint to be used for the request. In a PPAF-enabled account, this method checks whether
        the partition key range has any unavailable regions, and if so, it tries to move to the next available region.
        If all regions are unavailable, it invalidates the cache and starts once again from the main write region in the
        account configurations.

        :param PartitionKeyRangeWrapper pk_range_wrapper: The wrapper containing the partition key range information
            for the request.
        :param RequestObject request: The request object containing the routing context.
        :returns: The regional endpoint to be used for the request.
        :rtype: str
        """
        if self.is_per_partition_automatic_failover_applicable(request) and pk_range_wrapper:
            # If per partition automatic failover is applicable, we check partition unavailability
            if pk_range_wrapper in self.partition_range_to_failover_info:
                partition_failover_info = self.partition_range_to_failover_info[pk_range_wrapper]
                if request.location_endpoint_to_route is not None:
                    endpoint_region = self.location_cache.get_location_from_endpoint(request.location_endpoint_to_route)
                    if endpoint_region in partition_failover_info.unavailable_regional_endpoints:
                        available_account_regional_endpoints = self.location_cache.account_read_regional_routing_contexts_by_location #pylint: disable=line-too-long
                        if (partition_failover_info.current_region is not None and
                                endpoint_region != partition_failover_info.current_region):
                            # this request has not yet seen there's an available region being used for this partition
                            regional_endpoint = available_account_regional_endpoints[
                                partition_failover_info.current_region].primary_endpoint
                            request.route_to_location(regional_endpoint)
                        else:
                            if (len(self.location_cache.account_read_regional_routing_contexts_by_location)
                                    == len(partition_failover_info.unavailable_regional_endpoints)):
                                # If no other region is available, we invalidate the cache and start once again
                                # from our main write region in the account configurations
                                logger.warning("PPAF - All available regions for partition %s are unavailable."
                                               " Refreshing cache.", pk_range_wrapper)
                                self.partition_range_to_failover_info[pk_range_wrapper] = PartitionLevelFailoverInfo()
                                request.clear_route_to_location()
                            else:
                                # If the current region is unavailable, we try to move to the next available region
                                partition_failover_info.try_move_to_next_location(
                                    self.location_cache.account_read_regional_routing_contexts_by_location,
                                    endpoint_region,
                                    request)
                    else:
                        # Update the current regional endpoint to whatever the request is routing to
                        partition_failover_info.current_region = endpoint_region
            else:
                partition_failover_info = PartitionLevelFailoverInfo()
                endpoint_region = self.location_cache.get_location_from_endpoint(
                    request.location_endpoint_to_route)
                partition_failover_info.current_region = endpoint_region
                self.partition_range_to_failover_info[pk_range_wrapper] = partition_failover_info
        return self._resolve_service_endpoint_for_partition_circuit_breaker(request, pk_range_wrapper)

    def record_failure(self,
                       request: RequestObject,
                       pk_range_wrapper: Optional[PartitionKeyRangeWrapper] = None) -> None:
        """Records a failure for the given partition key range and request.
        :param RequestObject request: The request object containing the routing context.
        :param PartitionKeyRangeWrapper pk_range_wrapper: The wrapper containing the partition key range information
            for the request.
        :return: None
        """
        if self.is_per_partition_automatic_failover_applicable(request):
            if pk_range_wrapper is None:
                pk_range_wrapper = self.create_pk_range_wrapper(request)
            if pk_range_wrapper:
                self.ppaf_thresholds_tracker.add_failure(pk_range_wrapper)
        else:
            self.record_ppcb_failure(request, pk_range_wrapper)

    def record_success(self,
                       request: RequestObject,
                       pk_range_wrapper: Optional[PartitionKeyRangeWrapper] = None) -> None:
        """Records a success for the given partition key range and request, effectively clearing the failure count.
        :param RequestObject request: The request object containing the routing context.
        :param PartitionKeyRangeWrapper pk_range_wrapper: The wrapper containing the partition key range information
            for the request.
        :return: None
        """
        if self.is_per_partition_automatic_failover_applicable(request):
            if pk_range_wrapper is None:
                pk_range_wrapper = self.create_pk_range_wrapper(request)
            if pk_range_wrapper:
                self.ppaf_thresholds_tracker.clear_pk_failures(pk_range_wrapper)
        else:
            self.record_ppcb_success(request, pk_range_wrapper)
