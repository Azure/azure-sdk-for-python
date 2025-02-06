# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""Internal class for timeout failover retry policy implementation in the Azure
Cosmos database service.
"""
from azure.cosmos.documents import _OperationType
from . import http_constants


class _TimeoutFailoverRetryPolicy(object):

    def __init__(self, connection_policy, global_endpoint_manager, *args):
        self._max_retry_attempt_count = 120
        self._max_service_unavailable_retry_count = 1
        self.retry_after_in_milliseconds = 0
        self.args = args

        self.global_endpoint_manager = global_endpoint_manager
        self.retry_count = 0
        self.connection_policy = connection_policy
        self.request = args[0] if args else None

    def ShouldRetry(self, _exception):
        """Returns true if the request should retry based on the passed-in exception.

        :param exceptions.CosmosHttpResponseError _exception:
        :returns: a boolean stating whether the request should be retried
        :rtype: bool
        """
        # we don't retry on write operations for timeouts or service unavailable
        if self.request and (not _OperationType.IsReadOnlyOperation(self.request.operation_type)):
            return False

        if not self.connection_policy.EnableEndpointDiscovery:
            return False

        # Check if the next retry about to be done is safe
        if _exception.status_code == http_constants.StatusCodes.SERVICE_UNAVAILABLE and \
                self.retry_count >= self._max_service_unavailable_retry_count:
            return False
        self.retry_count += 1
        # Check if the next retry about to be done is safe
        if self.retry_count >= self._max_retry_attempt_count:
            return False

        if self.request:
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
