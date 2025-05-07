# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Internal class for service response read errors implementation in the Azure
Cosmos database service. Exceptions caught in this policy have had some issue receiving a response
from the service, and as such we do not know what the output of the operation was. As such, we
only do cross regional retries for read operations.
"""

import logging
from azure.cosmos.documents import _OperationType

class ServiceResponseRetryPolicy(object):

    def __init__(self, connection_policy, global_endpoint_manager, *args):
        self.args = args
        self.global_endpoint_manager = global_endpoint_manager
        self.total_retries = len(self.global_endpoint_manager.location_cache.read_regional_routing_contexts)
        self.failover_retry_count = 0
        self.connection_policy = connection_policy
        self.request = args[0] if args else None
        if self.request:
            self.location_endpoint = self.global_endpoint_manager.resolve_service_endpoint(self.request)
        self.logger = logging.getLogger('azure.cosmos.ServiceResponseRetryPolicy')

    def ShouldRetry(self):
        """Returns true if the request should retry based on preferred regions and retries already done.

        :returns: a boolean stating whether the request should be retried
        :rtype: bool
        """
        if not self.connection_policy.EnableEndpointDiscovery:
            return False

        # Check if the next retry about to be done is safe
        if (self.failover_retry_count + 1) >= self.total_retries:
            return False

        if self.request:
            if not _OperationType.IsReadOnlyOperation(self.request.operation_type):
                return False

            self.location_endpoint = self.resolve_next_region_service_endpoint()
            self.request.route_to_location(self.location_endpoint)
        return True

    # This function prepares the request to go to the next region
    def resolve_next_region_service_endpoint(self):
        # This acts as an index for next location in the list of available locations
        self.failover_retry_count += 1
        # clear previous location-based routing directive
        self.request.clear_route_to_location()
        # clear the last routed endpoint within same region since we are going to a new region now
        self.request.last_routed_location_endpoint_within_region = None
        # set location-based routing directive based on retry count
        # ensuring usePreferredLocations is set to True for retry
        self.request.route_to_location_with_preferred_location_flag(self.failover_retry_count, True)
        # Resolve the endpoint for the request and pin the resolution to the resolved endpoint
        # This enables marking the endpoint unavailability on endpoint failover/unreachability
        return self.global_endpoint_manager.resolve_service_endpoint(self.request)
