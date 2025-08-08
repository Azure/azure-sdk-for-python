# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Internal class for timeout failover retry policy implementation in the Azure
Cosmos database service.
"""
import os
from azure.cosmos.documents import _OperationType
from azure.cosmos._constants import _Constants as Constants

# cspell:ignore PPAF, ppaf

class _TimeoutFailoverRetryPolicy(object):

    def __init__(self, connection_policy, global_endpoint_manager, pk_range_wrapper, *args):
        self.retry_after_in_milliseconds = 500
        self.args = args
        self.request = args[0] if args else None

        self.global_endpoint_manager = global_endpoint_manager
        self.pk_range_wrapper = pk_range_wrapper
        # If an account only has 1 region, then we still want to retry once on the same region
        # We want this to be the default retry attempts as paging through a query means there are requests without
        # a request object
        self._max_retry_attempt_count = len(self.global_endpoint_manager.location_cache
                                            .read_regional_routing_contexts) + 1
       # If the request is a write operation, we only want to retry once if retry write is enabled
        if self.request and _OperationType.IsWriteOperation(self.request.operation_type):
            self._max_retry_attempt_count = len(
                self.global_endpoint_manager.location_cache.write_regional_routing_contexts
            ) + 1
        self.retry_count = 0
        self.connection_policy = connection_policy
        self.request = args[0] if args else None

    def ShouldRetry(self, _exception):
        """Returns true if the request should retry based on the passed-in exception.

        :param exceptions.CosmosHttpResponseError _exception:
        :returns: a boolean stating whether the request should be retried
        :rtype: bool
        """
        # PPAF will have its own retry logic based on consecutive failures before failing over to the next region
        if self.request and self.global_endpoint_manager.is_per_partition_automatic_failover_applicable(self.request):
            if (self.global_endpoint_manager.ppaf_thresholds_tracker.get_pk_failures(self.pk_range_wrapper)
                >= int(os.environ.get(Constants.TIMEOUT_ERROR_THRESHOLD_PPAF,
                                      Constants.TIMEOUT_ERROR_THRESHOLD_PPAF_DEFAULT))):
                # If the PPAF threshold is reached, we reset the count and retry to the next region
                self.global_endpoint_manager.ppaf_thresholds_tracker.clear_pk_failures(self.pk_range_wrapper)
                partition_level_info = self.global_endpoint_manager.partition_range_to_failover_info[
                    self.pk_range_wrapper]
                partition_level_info.unavailable_regional_endpoints.add(self.request.location_endpoint_to_route)
                self.global_endpoint_manager.resolve_service_endpoint_for_partition(self.request, self.pk_range_wrapper)
                return True

        # we retry only if the request is a read operation or if it is a write operation with retry enabled
        if self.request and not self.is_operation_retryable():
            return False

        if not self.connection_policy.EnableEndpointDiscovery:
            return False

        self.retry_count += 1
        # Check if the next retry about to be done is safe
        if self.retry_count >= self._max_retry_attempt_count:
            return False

        # second check here ensures we only do cross-regional retries for read requests
        # non-idempotent write retries should only be retried once, using preferred locations if available (MM)
        if self.request and (self.is_operation_retryable()
                             or self.global_endpoint_manager.can_use_multiple_write_locations(self.request)):
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

    def is_operation_retryable(self):
        if _OperationType.IsReadOnlyOperation(self.request.operation_type):
            return True
        return self.request.retry_write
