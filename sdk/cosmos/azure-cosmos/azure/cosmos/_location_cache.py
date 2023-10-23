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

"""Implements the abstraction to resolve target location for geo-replicated
DatabaseAccount with multiple writable and readable locations.
"""
import collections
import time

from . import documents
from . import http_constants

# pylint: disable=protected-access


class EndpointOperationType(object):
    NoneType = "None"
    ReadType = "Read"
    WriteType = "Write"


def get_endpoint_by_location(locations):
    endpoints_by_location = collections.OrderedDict()
    parsed_locations = []

    for location in locations:
        if not location["name"]:
            # during fail-over the location name is empty
            continue
        try:
            region_uri = location["databaseAccountEndpoint"]
            parsed_locations.append(location["name"])
            endpoints_by_location.update({location["name"]: region_uri})
        except Exception as e:
            raise e

    return endpoints_by_location, parsed_locations


class LocationCache(object):  # pylint: disable=too-many-public-methods,too-many-instance-attributes
    def current_time_millis(self):  # pylint: disable=no-self-use
        return int(round(time.time() * 1000))

    def __init__(
        self,
        preferred_locations,
        default_endpoint,
        enable_endpoint_discovery,
        use_multiple_write_locations,
        refresh_time_interval_in_ms,
    ):
        self.preferred_locations = preferred_locations
        self.default_endpoint = default_endpoint
        self.enable_endpoint_discovery = enable_endpoint_discovery
        self.use_multiple_write_locations = use_multiple_write_locations
        self.enable_multiple_writable_locations = False
        self.write_endpoints = [self.default_endpoint]
        self.read_endpoints = [self.default_endpoint]
        self.location_unavailability_info_by_endpoint = {}
        self.refresh_time_interval_in_ms = refresh_time_interval_in_ms
        self.last_cache_update_time_stamp = 0
        self.available_read_endpoint_by_locations = {}
        self.available_write_endpoint_by_locations = {}
        self.available_write_locations = []
        self.available_read_locations = []

    def check_and_update_cache(self):
        if (
            self.location_unavailability_info_by_endpoint
            and self.current_time_millis() - self.last_cache_update_time_stamp > self.refresh_time_interval_in_ms
        ):
            self.update_location_cache()

    def get_write_endpoints(self):
        self.check_and_update_cache()
        return self.write_endpoints

    def get_read_endpoints(self):
        self.check_and_update_cache()
        return self.read_endpoints

    def get_write_endpoint(self):
        return self.get_write_endpoints()[0]

    def get_read_endpoint(self):
        return self.get_read_endpoints()[0]

    def mark_endpoint_unavailable_for_read(self, endpoint):
        self.mark_endpoint_unavailable(endpoint, EndpointOperationType.ReadType)

    def mark_endpoint_unavailable_for_write(self, endpoint):
        self.mark_endpoint_unavailable(endpoint, EndpointOperationType.WriteType)

    def perform_on_database_account_read(self, database_account):
        self.update_location_cache(
            database_account._WritableLocations,
            database_account._ReadableLocations,
            database_account._EnableMultipleWritableLocations,
        )

    def get_ordered_write_endpoints(self):
        return self.available_write_locations

    def get_ordered_read_endpoints(self):
        return self.available_read_locations

    def resolve_service_endpoint(self, request):
        if request.location_endpoint_to_route:
            return request.location_endpoint_to_route

        location_index = int(request.location_index_to_route) if request.location_index_to_route else 0
        use_preferred_locations = (
            request.use_preferred_locations if request.use_preferred_locations is not None else True
        )

        if not use_preferred_locations or (
            documents._OperationType.IsWriteOperation(request.operation_type)
            and not self.can_use_multiple_write_locations_for_request(request)
        ):
            # For non-document resource types in case of client can use multiple write locations
            # or when client cannot use multiple write locations, flip-flop between the
            # first and the second writable region in DatabaseAccount (for manual failover)
            if self.enable_endpoint_discovery and self.available_write_locations:
                location_index = min(location_index % 2, len(self.available_write_locations) - 1)
                write_location = self.available_write_locations[location_index]
                return self.available_write_endpoint_by_locations[write_location]
            return self.default_endpoint

        endpoints = (
            self.get_write_endpoints()
            if documents._OperationType.IsWriteOperation(request.operation_type)
            else self.get_read_endpoints()
        )
        return endpoints[location_index % len(endpoints)]

    def should_refresh_endpoints(self):  # pylint: disable=too-many-return-statements
        most_preferred_location = self.preferred_locations[0] if self.preferred_locations else None

        # we should schedule refresh in background if we are unable to target the user's most preferredLocation.
        if self.enable_endpoint_discovery:

            should_refresh = self.use_multiple_write_locations and not self.enable_multiple_writable_locations

            if most_preferred_location:
                if self.available_read_endpoint_by_locations:
                    most_preferred_read_endpoint = self.available_read_endpoint_by_locations[most_preferred_location]
                    if most_preferred_read_endpoint and most_preferred_read_endpoint != self.read_endpoints[0]:
                        # For reads, we can always refresh in background as we can alternate to
                        # other available read endpoints
                        return True
                else:
                    return True

            if not self.can_use_multiple_write_locations():
                if self.is_endpoint_unavailable(self.write_endpoints[0], EndpointOperationType.WriteType):
                    # Since most preferred write endpoint is unavailable, we can only refresh in background if
                    # we have an alternate write endpoint
                    return True
                return should_refresh
            if most_preferred_location:
                most_preferred_write_endpoint = self.available_write_endpoint_by_locations[most_preferred_location]
                if most_preferred_write_endpoint:
                    should_refresh |= most_preferred_write_endpoint != self.write_endpoints[0]
                    return should_refresh
                return True
            return should_refresh
        return False

    def clear_stale_endpoint_unavailability_info(self):
        new_location_unavailability_info = {}
        if self.location_unavailability_info_by_endpoint:
            for unavailable_endpoint in self.location_unavailability_info_by_endpoint:
                unavailability_info = self.location_unavailability_info_by_endpoint[unavailable_endpoint]
                if not (
                    unavailability_info
                    and self.current_time_millis() - unavailability_info["lastUnavailabilityCheckTimeStamp"]
                    > self.refresh_time_interval_in_ms
                ):
                    new_location_unavailability_info[
                        unavailable_endpoint
                    ] = self.location_unavailability_info_by_endpoint[unavailable_endpoint]

        self.location_unavailability_info_by_endpoint = new_location_unavailability_info

    def is_endpoint_unavailable(self, endpoint, expected_available_operations):
        unavailability_info = (
            self.location_unavailability_info_by_endpoint[endpoint]
            if endpoint in self.location_unavailability_info_by_endpoint
            else None
        )

        if (
            expected_available_operations == EndpointOperationType.NoneType
            or not unavailability_info
            or expected_available_operations not in unavailability_info["operationType"]
        ):
            return False

        if (
            self.current_time_millis() - unavailability_info["lastUnavailabilityCheckTimeStamp"]
            > self.refresh_time_interval_in_ms
        ):
            return False
        # Unexpired entry present. Endpoint is unavailable
        return True

    def mark_endpoint_unavailable(self, unavailable_endpoint, unavailable_operation_type):
        unavailability_info = (
            self.location_unavailability_info_by_endpoint[unavailable_endpoint]
            if unavailable_endpoint in self.location_unavailability_info_by_endpoint
            else None
        )
        current_time = self.current_time_millis()
        if not unavailability_info:
            self.location_unavailability_info_by_endpoint[unavailable_endpoint] = {
                "lastUnavailabilityCheckTimeStamp": current_time,
                "operationType": set([unavailable_operation_type]),
            }
        else:
            unavailable_operations = set([unavailable_operation_type]).union(unavailability_info["operationType"])
            self.location_unavailability_info_by_endpoint[unavailable_endpoint] = {
                "lastUnavailabilityCheckTimeStamp": current_time,
                "operationType": unavailable_operations,
            }
        self.update_location_cache()

    def get_preferred_locations(self):
        return self.preferred_locations

    def update_location_cache(self, write_locations=None, read_locations=None, enable_multiple_writable_locations=None):
        if enable_multiple_writable_locations:
            self.enable_multiple_writable_locations = enable_multiple_writable_locations

        self.clear_stale_endpoint_unavailability_info()

        if self.enable_endpoint_discovery:
            if read_locations:
                self.available_read_endpoint_by_locations, self.available_read_locations = get_endpoint_by_location(  # pylint: disable=line-too-long
                    read_locations
                )

            if write_locations:
                self.available_write_endpoint_by_locations, self.available_write_locations = get_endpoint_by_location(  # pylint: disable=line-too-long
                    write_locations
                )

        self.write_endpoints = self.get_preferred_available_endpoints(
            self.available_write_endpoint_by_locations,
            self.available_write_locations,
            EndpointOperationType.WriteType,
            self.default_endpoint,
        )
        self.read_endpoints = self.get_preferred_available_endpoints(
            self.available_read_endpoint_by_locations,
            self.available_read_locations,
            EndpointOperationType.ReadType,
            self.write_endpoints[0],
        )
        self.last_cache_update_timestamp = self.current_time_millis()  # pylint: disable=attribute-defined-outside-init

    def get_preferred_available_endpoints(
        self, endpoints_by_location, orderedLocations, expected_available_operation, fallback_endpoint
    ):
        endpoints = []
        # if enableEndpointDiscovery is false, we always use the defaultEndpoint that
        # user passed in during documentClient init
        if self.enable_endpoint_discovery and endpoints_by_location:  # pylint: disable=too-many-nested-blocks
            if (
                self.can_use_multiple_write_locations()
                or expected_available_operation == EndpointOperationType.ReadType
            ):
                unavailable_endpoints = []
                if self.preferred_locations:
                    # When client can not use multiple write locations, preferred locations
                    # list should only be used determining read endpoints order. If client
                    # can use multiple write locations, preferred locations list should be
                    # used for determining both read and write endpoints order.
                    for location in self.preferred_locations:
                        endpoint = endpoints_by_location[location] if location in endpoints_by_location else None
                        if endpoint:
                            if self.is_endpoint_unavailable(endpoint, expected_available_operation):
                                unavailable_endpoints.append(endpoint)
                            else:
                                endpoints.append(endpoint)

                if not endpoints:
                    endpoints.append(fallback_endpoint)

                endpoints.extend(unavailable_endpoints)
            else:
                for location in orderedLocations:
                    if location and location in endpoints_by_location:
                        # location is empty during manual failover
                        endpoints.append(endpoints_by_location[location])

        if not endpoints:
            endpoints.append(fallback_endpoint)

        return endpoints

    def can_use_multiple_write_locations(self):
        return self.use_multiple_write_locations and self.enable_multiple_writable_locations

    def can_use_multiple_write_locations_for_request(self, request):
        return self.can_use_multiple_write_locations() and (
            request.resource_type == http_constants.ResourceType.Document
            or (
                request.resource_type == http_constants.ResourceType.StoredProcedure
                and request.operation_type == documents._OperationType.ExecuteJavaScript
            )
        )
