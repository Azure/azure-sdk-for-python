# The MIT License (MIT)
# Copyright (c) 2018 Microsoft Corporation

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

"""Internal class for session read/write unavailable retry policy implementation
in the Azure Cosmos database service.
"""

import logging
from azure.cosmos.documents import _OperationType

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_formatter = logging.Formatter("%(levelname)s:%(message)s")
log_handler = logging.StreamHandler()
log_handler.setFormatter(log_formatter)
logger.addHandler(log_handler)


class _SessionRetryPolicy(object):
    """The session retry policy used to handle read/write session unavailability.
    """

    Max_retry_attempt_count = 1
    Retry_after_in_milliseconds = 0

    def __init__(self, endpoint_discovery_enable, global_endpoint_manager, *args):
        self.global_endpoint_manager = global_endpoint_manager
        self._max_retry_attempt_count = _SessionRetryPolicy.Max_retry_attempt_count
        self.session_token_retry_count = 0
        self.retry_after_in_milliseconds = _SessionRetryPolicy.Retry_after_in_milliseconds
        self.endpoint_discovery_enable = endpoint_discovery_enable
        self.request = args[0] if args else None
        if self.request:
            self.can_use_multiple_write_locations = self.global_endpoint_manager.can_use_multiple_write_locations(
                self.request
            )
            # clear previous location-based routing directive
            self.request.clear_route_to_location()

            # Resolve the endpoint for the request and pin the resolution to the resolved endpoint
            # This enables marking the endpoint unavailability on endpoint failover/unreachability
            self.location_endpoint = self.global_endpoint_manager.resolve_service_endpoint(self.request)
            self.request.route_to_location(self.location_endpoint)

    def ShouldRetry(self, _exception):
        """Returns true if the request should retry based on the passed-in exception.

        :param exceptions.CosmosHttpResponseError _exception:
        :returns: a boolean stating whether the request should be retried
        :rtype: bool
        """
        self.session_token_retry_count += 1
        # clear previous location-based routing directive
        self.request.clear_route_to_location()

        if not self.endpoint_discovery_enable:
            # if endpoint discovery is disabled, the request cannot be retried anywhere else
            return False

        if self.can_use_multiple_write_locations:
            if _OperationType.IsReadOnlyOperation(self.request.operation_type):
                endpoints = self.global_endpoint_manager.get_ordered_read_endpoints()
            else:
                endpoints = self.global_endpoint_manager.get_ordered_write_endpoints()

            if self.session_token_retry_count > len(endpoints):
                # When use multiple write locations is true and the request has been tried
                # on all locations, then don't retry the request
                return False

            # set location-based routing directive based on request retry context
            self.request.route_to_location_with_preferred_location_flag(
                self.session_token_retry_count - 1, self.session_token_retry_count > self._max_retry_attempt_count
            )
            self.request.should_clear_session_token_on_session_read_failure = self.session_token_retry_count == len(
                endpoints
            )  # clear on last attempt

            # Resolve the endpoint for the request and pin the resolution to the resolved endpoint
            # This enables marking the endpoint unavailability on endpoint failover/unreachability
            self.location_endpoint = self.global_endpoint_manager.resolve_service_endpoint(self.request)
            self.request.route_to_location(self.location_endpoint)
            return True

        if self.session_token_retry_count > self._max_retry_attempt_count:
            # When cannot use multiple write locations, then don't retry the request if
            # we have already tried this request on the write location
            return False

        # set location-based routing directive based on request retry context
        self.request.route_to_location_with_preferred_location_flag(self.session_token_retry_count - 1, False)
        self.request.should_clear_session_token_on_session_read_failure = True

        # Resolve the endpoint for the request and pin the resolution to the resolved endpoint
        # This enables marking the endpoint unavailability on endpoint failover/unreachability
        self.location_endpoint = self.global_endpoint_manager.resolve_service_endpoint(self.request)
        self.request.route_to_location(self.location_endpoint)
        return True
