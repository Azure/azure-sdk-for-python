# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Internal class for timeout failover retry policy implementation in the Azure
Cosmos database service.
"""
from azure.cosmos.documents import _OperationType


class _TimeoutFailoverRetryPolicy(object):

    def __init__(self, connection_policy, global_endpoint_manager, *args):
        self.retry_after_in_milliseconds = 500
        self.args = args
        self.request = args[0] if args else None
        self.global_endpoint_manager = global_endpoint_manager
        # If an account only has 1 region, then we still want to retry once on the same region
        if self.request:
            if _OperationType.IsReadOnlyOperation(self.request.operation_type):
                self._max_retry_attempt_count = len(self.global_endpoint_manager.location_cache
                                                    .read_regional_routing_contexts) + 1
            else:
                # we only want to retry once on non-idempotent writes
                self._max_retry_attempt_count = 2
        self.retry_count = 0
        self.connection_policy = connection_policy

    def ShouldRetry(self, _exception):
        """Returns true if the request should retry based on the passed-in exception.

        :param exceptions.CosmosHttpResponseError _exception:
        :returns: a boolean stating whether the request should be retried
        :rtype: bool
        """
        # we don't retry on write operations for timeouts or any internal server errors
        if self.request and not self.is_operation_retryable():
            return False

        if not self.connection_policy.EnableEndpointDiscovery:
            return False

        self.retry_count += 1
        # Check if the next retry about to be done is safe
        if self.retry_count >= self._max_retry_attempt_count:
            return False

        # second check here ensures we only do cross-regional retries for read requests
        # non-idempotent write retries should be retried in the same region
        if self.request and _OperationType.IsReadOnlyOperation(self.request.operation_type):
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
        return self.global_endpoint_manager.resolve_service_endpoint(self.request)

    def is_operation_retryable(self):
        if _OperationType.IsReadOnlyOperation(self.request.operation_type):
            return True
        if _OperationType.IsWriteOperation(self.request.operation_type):
            if self.request.operation_type == _OperationType.Patch and not self.request.retry_write:
                return False
            if self.connection_policy.RetryNonIdempotentWrites or self.request.retry_write:
                return True
        return False
