# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Internal class for service unavailable errors implementation in the Azure Cosmos database service.

Service unavailable errors can occur when a request does not make it to the service, or when there is an issue with
the service. In either case, we know the request did not get processed successfully, so service unavailable errors are
 retried in the next available preferred region.
"""
from azure.cosmos.documents import _OperationType
from azure.cosmos.exceptions import CosmosHttpResponseError

#cspell:ignore ppaf

class _ServiceUnavailableRetryPolicy(object):
    def __init__(
            self,
            connection_policy,
            global_endpoint_manager,
            pk_range_wrapper,
            *args):
        self.retry_after_in_milliseconds = 500
        self.global_endpoint_manager = global_endpoint_manager
        self.pk_range_wrapper = pk_range_wrapper
        self.retry_count = 0
        self.connection_policy = connection_policy
        self.request = args[0] if args else None
        # If an account only has 1 region, then we still want to retry once on the same region
        self._max_retry_attempt_count = len(self.global_endpoint_manager.
                                            location_cache.read_regional_routing_contexts) + 1
        if self.request and _OperationType.IsWriteOperation(self.request.operation_type):
            self._max_retry_attempt_count = len(self.global_endpoint_manager.location_cache.
                                                write_regional_routing_contexts) + 1

    def ShouldRetry(self, _exception: CosmosHttpResponseError):
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
            # If per partition automatic failover is applicable, we mark the current endpoint as unavailable
            # and resolve the service endpoint for the partition range - otherwise, continue the default retry logic
            if self.global_endpoint_manager.is_per_partition_automatic_failover_applicable(self.request):
                partition_level_info = self.global_endpoint_manager.partition_range_to_failover_info[
                    self.pk_range_wrapper]
                location = self.global_endpoint_manager.location_cache.get_location_from_endpoint(
                    str(self.request.location_endpoint_to_route))
                regional_context = (self.global_endpoint_manager.location_cache.
                                    account_read_regional_routing_contexts_by_location.get(location))
                partition_level_info.unavailable_regional_endpoints[location] = regional_context
                self.global_endpoint_manager.resolve_service_endpoint_for_partition(self.request, self.pk_range_wrapper)
                return True
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
