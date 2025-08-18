# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Internal class for service unavailable retry policy implementation in the Azure
Cosmos database service.
"""
from azure.cosmos._base import try_ppaf_failover_threshold

class _ServiceUnavailableRetryPolicy(object):

    def __init__(self, connection_policy, global_endpoint_manager, pk_range_wrapper, *args):
        self.retry_after_in_milliseconds = 500
        self.global_endpoint_manager = global_endpoint_manager
        self.pk_range_wrapper = pk_range_wrapper
        self.retry_count = 0
        self.connection_policy = connection_policy
        self.request = args[0] if args else None
        # If an account only has 1 region, then we still want to retry once on the same region
        self._max_retry_attempt_count = max(2, (len(self.global_endpoint_manager.location_cache.read_regional_routing_contexts)))

    def ShouldRetry(self, _exception):
        """Returns true if the request should retry based on the passed-in exception.

        :param exceptions.CosmosHttpResponseError _exception:
        :returns: a boolean stating whether the request should be retried
        :rtype: bool
        """
        # writes are retried for 503s
        if not self.connection_policy.EnableEndpointDiscovery:
            return False

        self.retry_count += 1
        # Check if the next retry about to be done is safe
        if self.retry_count >= self._max_retry_attempt_count:
            return False

        if self.request:
            try_ppaf_failover_threshold(self.global_endpoint_manager, self.pk_range_wrapper, self.request)
            location_endpoint = self.resolve_next_region_service_endpoint()
            self.request.route_to_location(location_endpoint)
        return True

    # This function prepares the request to go to the next region
    def resolve_next_region_service_endpoint(self):
        # clear previous location-based routing directive
        self.request.clear_route_to_location()
        # clear the last routed endpoint within same region since we are going to a new region now
        self.request.last_routed_location_endpoint_within_region = None
        # set location-based routing directive based on retry count
        # ensuring usePreferredLocations is set to True for retry
        self.request.route_to_location_with_preferred_location_flag(self.retry_count, True)
        # Resolve the endpoint for the request and pin the resolution to the resolved endpoint
        # This enables marking the endpoint unavailability on endpoint failover/unreachability
        return self.global_endpoint_manager.resolve_service_endpoint_for_partition(self.request, self.pk_range_wrapper)
