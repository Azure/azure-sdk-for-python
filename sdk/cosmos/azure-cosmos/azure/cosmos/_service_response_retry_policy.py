# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Internal class for service response read errors implementation in the Azure
Cosmos database service. Exceptions caught in this policy have had some issue receiving a response
from the service, and as such we do not know what the output of the operation was. As such, we
only do cross regional retries for read operations.
"""
#cspell:ignore PPAF, ppaf

from azure.cosmos.documents import _OperationType

class ServiceResponseRetryPolicy(object):

    def __init__(self, connection_policy, global_endpoint_manager, pk_range_wrapper, *args):
        self.args = args
        self.global_endpoint_manager = global_endpoint_manager
        self.pk_range_wrapper = pk_range_wrapper
        self.total_retries = len(self.global_endpoint_manager.location_cache.read_regional_routing_contexts)
        self.failover_retry_count = 0
        self.connection_policy = connection_policy
        self.request = args[0] if args else None
        if self.request:
            if self.request.retry_write > 0:
                # If the request is a write operation, we set the maximum retry count to be the number of
                # write retries provided by the customer.
                self.max_write_retry_count = self.request.retry_write
            self.location_endpoint = (self.global_endpoint_manager
                                      .resolve_service_endpoint_for_partition(self.request, pk_range_wrapper))

    def ShouldRetry(self):
        """Returns true if the request should retry based on preferred regions and retries already done.

        :returns: a boolean stating whether the request should be retried
        :rtype: bool
        """
        if not self.connection_policy.EnableEndpointDiscovery:
            return False

        # Check if the next retry about to be done is safe
        if ((self.failover_retry_count + 1) >= self.total_retries and
                _OperationType.IsReadOnlyOperation(self.request.operation_type)):
            return False

        if self.request:
            # We track consecutive failures for per partition automatic failover, and only fail over at a partition
            # level after the threshold is reached
            self.global_endpoint_manager.try_ppaf_failover_threshold(self.pk_range_wrapper, self.request)
            if not _OperationType.IsReadOnlyOperation(self.request.operation_type) and not self.request.retry_write > 0:
                return False
            if self.request.retry_write > 0 and self.failover_retry_count + 1 >= self.max_write_retry_count:
                # If we have already retried the write operation to the maximum allowed number of times,
                # we do not retry further.
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
        # set location-based routing directive based on retry count
        # ensuring usePreferredLocations is set to True for retry
        self.request.route_to_location_with_preferred_location_flag(self.failover_retry_count, True)
        # Resolve the endpoint for the request and pin the resolution to the resolved endpoint
        # This enables marking the endpoint unavailability on endpoint failover/unreachability
        return self.global_endpoint_manager.resolve_service_endpoint_for_partition(self.request, self.pk_range_wrapper)
