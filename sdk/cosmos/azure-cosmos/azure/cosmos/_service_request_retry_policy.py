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
        self.failover_retry_count = 0
        self.total_retries = 1
        self.connection_policy = connection_policy
        self.request = args[0] if args else None
        self.logger = logging.getLogger("azure.cosmos.ServiceRequestRetryPolicy")
        if self.request:
            self.location_endpoint = self.global_endpoint_manager.resolve_service_endpoint(self.request)
            if _OperationType.IsReadOnlyOperation(self.request.operation_type):
                self.total_retries = len(self.global_endpoint_manager.location_cache.read_endpoints)
            else:
                self.total_retries = len(self.global_endpoint_manager.location_cache.write_endpoints)

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
            if self.request.operation_type == ResourceType.DatabaseAccount:
                return False

            if self.location_endpoint:
                if _OperationType.IsReadOnlyOperation(self.request.operation_type):
                    self.global_endpoint_manager.mark_endpoint_unavailable_for_read(self.location_endpoint)
                    self.logger.warning("Marking %s unavailable for read", self.location_endpoint)
                else:
                    self.global_endpoint_manager.mark_endpoint_unavailable_for_write(self.location_endpoint)
                    self.logger.warning("Marking %s unavailable for write", self.location_endpoint)

        self.failover_retry_count += 1
        if self.failover_retry_count >= self.total_retries:
            return False

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
