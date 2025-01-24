"""Internal class for service request read errors implementation in the Azure
Cosmos database service.
"""

from azure.cosmos.documents import _OperationType

# This Retry policy is for the requests which were never sent to the service.
class ServiceRequestRetryPolicy(object):

    def __init__(self, connection_policy, global_endpoint_manager, *args):
        self.args = args
        self.global_endpoint_manager = global_endpoint_manager
        self.total_retries = len(self.global_endpoint_manager.location_cache.read_endpoints)
        self.in_region_retry_count = 0
        self.failover_retry_count = 0
        self.connection_policy = connection_policy
        self.request = args[0] if args else None
        if self.request:
            self.location_endpoint = self.global_endpoint_manager.resolve_service_endpoint(self.request)

    def ShouldRetry(self):
        """Returns true if the request should retry based on preferred regions and retries already done.

        """
        # Fed A
        #
        if not self.connection_policy.EnableEndpointDiscovery:
            return False
        if self.args[0].resource_type != 'docs':
            return False

        # We just failed on regional endpoint, let's mark it unavailable and send the cache refresh flag
        # Cache refresh flag should only be true if we have already tried both current and previous regional endpoints
        if self.request:
            if self.location_endpoint:
                if _OperationType.IsReadOnlyOperation(self.request.operation_type):
                    # Mark current read endpoint as unavailable
                    self.global_endpoint_manager.mark_endpoint_unavailable_for_read(self.location_endpoint,
                                                                                    self.request.use_previous_endpoint_within_region)
                else:
                    self.global_endpoint_manager.mark_endpoint_unavailable_for_write(self.location_endpoint,
                                                                                     self.request.use_previous_endpoint_within_region)

        self.in_region_retry_count += 1
        self.request.use_previous_endpoint_within_region = True
        # The reason for this check is that we retry on
        # current and previous regional endpoint for every region before moving to next region
        if self.in_region_retry_count > 1:
            self.in_region_retry_count = 0
            self.failover_retry_count += 1
            self.request.use_previous_endpoint_within_region = False

        if self.request:
            # clear previous location-based routing directive
            self.request.clear_route_to_location()

            # set location-based routing directive based on retry count
            # ensuring usePreferredLocations is set to True for retry
            self.request.route_to_location_with_preferred_location_flag(self.failover_retry_count, True)

            # Resolve the endpoint for the request and pin the resolution to the resolved endpoint
            # This enables marking the endpoint unavailability on endpoint failover/unreachability
            self.location_endpoint = self.global_endpoint_manager.resolve_service_endpoint(self.request)
            self.request.route_to_location(self.location_endpoint)
        return True
