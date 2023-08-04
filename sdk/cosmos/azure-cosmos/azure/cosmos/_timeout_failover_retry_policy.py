# The MIT License (MIT)
# Copyright (c) 2017 Microsoft Corporation

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

"""Internal class for timeout failover retry policy implementation in the Azure
Cosmos database service.
"""
from . import http_constants


class _TimeoutFailoverRetryPolicy(object):

    def __init__(self, connection_policy, global_endpoint_manager, *args):
        self._max_retry_attempt_count = 120
        self._max_service_unavailable_retry_count = 1
        self.retry_after_in_milliseconds = 0
        self.args = args

        self.global_endpoint_manager = global_endpoint_manager
        self.failover_retry_count = 0
        self.connection_policy = connection_policy
        self.request = args[0] if args else None
        if self.request:
            self.location_endpoint = self.global_endpoint_manager.resolve_service_endpoint(self.request)

    def needsRetry(self):
        if self.args:
            if (self.args[3].method == "GET") \
                    or http_constants.HttpHeaders.IsQueryPlanRequest in self.args[3].headers\
                    or http_constants.HttpHeaders.IsQuery in self.args[3].headers:
                return True
        return False

    def ShouldRetry(self, _exception):
        """Returns true if should retry based on the passed-in exception.

        :param (exceptions.CosmosHttpResponseError instance) _exception:
        :rtype: boolean

        """
        if not self.needsRetry():
            return False

        if not self.connection_policy.EnableEndpointDiscovery:
            return False

        if _exception.status_code == http_constants.StatusCodes.SERVICE_UNAVAILABLE and \
                self.failover_retry_count >= self._max_service_unavailable_retry_count:
            return False
        if self.failover_retry_count >= self._max_retry_attempt_count:
            return False

        self.failover_retry_count += 1

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
