# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Internal class for endpoint discovery retry policy implementation in the
Azure Cosmos database service.
"""

# cspell:ignore PPAF

from azure.cosmos.documents import _OperationType

class EndpointDiscoveryRetryPolicy(object):
    """The endpoint discovery retry policy class used for geo-replicated database accounts
       to handle the write forbidden exceptions due to writable/readable location changes
       (say, after a failover).
    """

    Max_retry_attempt_count = 120
    Retry_after_in_milliseconds = 1000

    def __init__(self, connection_policy, global_endpoint_manager, pk_range_wrapper, *args):
        self.global_endpoint_manager = global_endpoint_manager
        self.pk_range_wrapper = pk_range_wrapper
        self._max_retry_attempt_count = EndpointDiscoveryRetryPolicy.Max_retry_attempt_count
        self.failover_retry_count = 0
        self.retry_after_in_milliseconds = EndpointDiscoveryRetryPolicy.Retry_after_in_milliseconds
        self.connection_policy = connection_policy
        self.request = args[0] if args else None


    def ShouldRetry(self, exception):  # pylint: disable=unused-argument
        """Returns true if the request should retry based on the passed-in exception.

        :param exceptions.CosmosHttpResponseError exception:
        :returns: a boolean stating whether the request should be retried
        :rtype: bool
        """
        if not self.request:
            return False

        if not self.connection_policy.EnableEndpointDiscovery:
            return False

        if self.failover_retry_count >= self.Max_retry_attempt_count:
            return False

        self.failover_retry_count += 1

        # set the refresh_needed flag to ensure that endpoint list is
        # refreshed with new writable and readable locations
        self.global_endpoint_manager.refresh_needed = True

        # If per partition automatic failover is applicable, we mark the current endpoint as unavailable
        # and resolve the service endpoint for the partition range - otherwise, continue the default retry logic
        if self.global_endpoint_manager.is_per_partition_automatic_failover_applicable(self.request):
            partition_level_info = self.global_endpoint_manager.partition_range_to_failover_info[self.pk_range_wrapper]
            location = self.global_endpoint_manager.location_cache.get_location_from_endpoint(
                str(self.request.location_endpoint_to_route))
            regional_endpoint = (self.global_endpoint_manager.location_cache.
                                account_read_regional_routing_contexts_by_location.get(location))
            partition_level_info.unavailable_regional_endpoints[location] = regional_endpoint
            self.global_endpoint_manager.resolve_service_endpoint_for_partition(self.request, self.pk_range_wrapper)
            return True

        if self.request.location_endpoint_to_route:
            context = self.__class__.__name__
            if _OperationType.IsReadOnlyOperation(self.request.operation_type):
                # Mark current read endpoint as unavailable
                self.global_endpoint_manager.mark_endpoint_unavailable_for_read(
                    self.request.location_endpoint_to_route,
                    True, context)
            else:
                self.global_endpoint_manager.mark_endpoint_unavailable_for_write(
                    self.request.location_endpoint_to_route,
                    True, context)

        # clear previous location-based routing directive
        self.request.clear_route_to_location()

        # set location-based routing directive based on retry count
        # simulating single master writes by ensuring usePreferredLocations is set to false
        # reasoning being that 403.3 is only expected for write region failover in single writer account
        # and we must rely on account locations as they are the source of truth
        self.request.route_to_location_with_preferred_location_flag(self.failover_retry_count, False)

        return True
