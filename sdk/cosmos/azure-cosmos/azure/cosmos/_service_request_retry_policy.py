# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Internal class for service request errors implementation in the Azure
Cosmos database service. Exceptions caught in this policy have the guarantee that they never
reached the service, and as such we will attempt cross regional retries depending on the
operation type.
"""

import logging
from azure.cosmos.documents import _OperationType
from azure.cosmos.http_constants import ResourceType

class ServiceRequestRetryPolicy(object):

    def __init__(self, connection_policy, global_endpoint_manager, *args):
        self.args = args
        self.global_endpoint_manager = global_endpoint_manager
        self.total_retries = len(self.global_endpoint_manager.location_cache.read_regional_endpoints)
        self.total_in_region_retries = 2
        self.in_region_retry_count = 0
        self.failover_retry_count = 0
        self.connection_policy = connection_policy
        self.request = args[0] if args else None
        self.logger = logging.getLogger("azure.cosmos.ServiceRequestRetryPolicy")
        if self.request:
            self.location_endpoint = self.global_endpoint_manager.resolve_service_endpoint(self.request)
            if _OperationType.IsReadOnlyOperation(self.request.operation_type):
                self.total_retries = len(self.global_endpoint_manager.location_cache.read_regional_endpoints)
            else:
                self.total_retries = len(self.global_endpoint_manager.location_cache.write_regional_endpoints)

    def ShouldRetry(self):
        """Returns true if the request should retry based on preferred regions and retries already done.

        :returns: a boolean stating whether the request should be retried
        :rtype: bool
        """
        if not self.connection_policy.EnableEndpointDiscovery:
            return False

        if self.request:
            # For database account calls, we loop through preferred locations
            # in global endpoint manager
            if self.request.resource_type == ResourceType.DatabaseAccount:
                return False

            refresh_cache = self.request.last_routed_location_endpoint_within_region is not None
            self.mark_endpoint_unavailable(refresh_cache)

            # Check if it is safe to do another retry
            if self.in_region_retry_count >= self.total_in_region_retries:
                # reset the in region retry count
                self.in_region_retry_count = 0
                self.failover_retry_count += 1
                if self.failover_retry_count >= self.total_retries:
                    return False

            self.request.last_routed_location_endpoint_within_region = self.request.location_endpoint_to_route
            if _OperationType.IsReadOnlyOperation(self.request.operation_type):
                self.mark_endpoint_unavailable(True)
                # We just directly got to the next location in case of read requests
                # We don't retry again on the same region for regional endpoint
                self.failover_retry_count += 1
                if self.failover_retry_count >= self.total_retries:
                    return False
                # # Check if it is safe to failover to another region
                self.location_endpoint = self.resolve_next_region_service_endpoint()
            else:
                self.location_endpoint = self.resolve_current_region_service_endpoint()
                # This is the case where both current and previous point to the same writable endpoint
                # In this case we don't want to retry again, rather failover to the next region
                if self.request.last_routed_location_endpoint_within_region == self.location_endpoint:
                    # Since both the endpoints (current and previous) are same, we mark them unavailable
                    # and refresh the cache.
                    print("In service request - Both current and previous are same, marking them unavailable")
                    self.mark_endpoint_unavailable(True)
                    # Although we are not retrying again in this region
                    # but since this is the same endpoint, our in region retries are done for this region
                    # and we reset the in region retry count
                    self.in_region_retry_count = 0
                    self.failover_retry_count += 1
                    # # Check if it is safe to failover to another region
                    if self.failover_retry_count >= self.total_retries:
                        return False
                    self.location_endpoint = self.resolve_next_region_service_endpoint()

            print("In service request - Location endpoint: {}".format(self.location_endpoint))
            self.request.route_to_location(self.location_endpoint)
        return True

    # This function prepares the request to go to the second endpoint in the same region
    def resolve_current_region_service_endpoint(self):
        # clear previous location-based routing directive
        self.request.clear_route_to_location()
        self.in_region_retry_count += 1
        print("In service request retry policy - Resolving current region endpoint - in region retry count: {}"
              .format(self.in_region_retry_count))
        # resolve the next service endpoint in the same region
        # since we maintain 2 endpoints per region for write operations
        self.request.route_to_location_with_preferred_location_flag(0, True)
        return self.global_endpoint_manager.resolve_service_endpoint(self.request)

    # This function prepares the request to go to the next region
    def resolve_next_region_service_endpoint(self):
        # This acts as an index for next location in the list of available locations
        # clear previous location-based routing directive
        print("In service request retry policy - Resolving next region endpoint - failover retry count: {}"
              .format(self.failover_retry_count))
        self.request.clear_route_to_location()
        # clear the last routed endpoint within same region since we are going to a new region now
        self.request.clear_last_routed_location()
        # set location-based routing directive based on retry count
        # ensuring usePreferredLocations is set to True for retry
        self.request.route_to_location_with_preferred_location_flag(0, True)
        # Resolve the endpoint for the request and pin the resolution to the resolved endpoint
        # This enables marking the endpoint unavailability on endpoint failover/unreachability
        return self.global_endpoint_manager.resolve_service_endpoint(self.request)

    def mark_endpoint_unavailable(self, refresh_cache: bool):
        print("Marking endpoint unavailable - refresh_cache : {}".format(refresh_cache))
        if _OperationType.IsReadOnlyOperation(self.request.operation_type):
            self.global_endpoint_manager.mark_endpoint_unavailable_for_read(self.location_endpoint, True)
            self.logger.warning("Marking %s unavailable for read", self.location_endpoint)
        else:
            self.global_endpoint_manager.mark_endpoint_unavailable_for_write(self.location_endpoint, refresh_cache)
            self.logger.warning("Marking %s unavailable for write", self.location_endpoint)

    def force_refresh_cache(self):
        self.global_endpoint_manager.force_refresh(None)