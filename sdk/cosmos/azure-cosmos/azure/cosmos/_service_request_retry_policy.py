# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Internal class for service request errors implementation in the Azure
Cosmos database service. Exceptions caught in this policy have the guarantee that they never
reached the service, and as such we will attempt cross regional retries depending on the
operation type.
"""

from azure.cosmos.documents import _OperationType
from azure.cosmos.http_constants import ResourceType

class ServiceRequestRetryPolicy(object):

    def __init__(self, connection_policy, global_endpoint_manager, pk_range_wrapper, *args):
        self.args = args
        self.global_endpoint_manager = global_endpoint_manager
        self.pk_range_wrapper = pk_range_wrapper
        self.total_retries = len(self.global_endpoint_manager.location_cache.read_regional_routing_contexts)
        self.failover_retry_count = 0
        self.connection_policy = connection_policy
        self.request = args[0] if args else None

        if self.request:
            if _OperationType.IsReadOnlyOperation(self.request.operation_type):
                self.total_retries = len(
                    self.global_endpoint_manager.location_cache._get_applicable_read_regional_routing_contexts(
                        self.request))
            else:
                self.total_retries = len(
                    self.global_endpoint_manager.location_cache._get_applicable_write_regional_routing_contexts(
                        self.request))


    def ShouldRetry(self):  # pylint: disable=too-many-return-statements
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

            # This logic is for the last retry and mark the region unavailable
            self.mark_endpoint_unavailable(self.request.location_endpoint_to_route)

            # We just directly got to the next location in case of read requests
            self.failover_retry_count += 1
            if self.failover_retry_count >= self.total_retries:
                return False
            # Check if it is safe to failover to another region
            location_endpoint = self.resolve_next_region_service_endpoint()

            self.request.route_to_location(location_endpoint)
            return True
        # Check if the next retry about to be done is safe
        if (self.failover_retry_count + 1) >= self.total_retries:
            return False
        self.failover_retry_count += 1
        return True

    # This function prepares the request to go to the next region
    def resolve_next_region_service_endpoint(self):
        # This acts as an index for next location in the list of available locations
        # clear previous location-based routing directive
        self.request.clear_route_to_location()
        # set location-based routing directive based on retry count
        # ensuring usePreferredLocations is set to True for retry
        self.request.route_to_location_with_preferred_location_flag(0, True)
        # Resolve the endpoint for the request and pin the resolution to the resolved endpoint
        # This enables marking the endpoint unavailability on endpoint failover/unreachability
        return self.global_endpoint_manager.resolve_service_endpoint_for_partition(self.request, self.pk_range_wrapper)

    def mark_endpoint_unavailable(self, unavailable_endpoint):
        context = self.__class__.__name__
        if _OperationType.IsReadOnlyOperation(self.request.operation_type):
            self.global_endpoint_manager.mark_endpoint_unavailable_for_read(unavailable_endpoint, True, context)
        else:
            self.global_endpoint_manager.mark_endpoint_unavailable_for_write(unavailable_endpoint, True, context)

    def update_location_cache(self):
        self.global_endpoint_manager.update_location_cache()
