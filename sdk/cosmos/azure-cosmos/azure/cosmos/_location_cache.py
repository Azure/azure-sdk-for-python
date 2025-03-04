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
import logging
import time
from urllib.parse import urlparse

from . import documents
from . import http_constants
from .documents import _OperationType

# pylint: disable=protected-access

logger = logging.getLogger("azure.cosmos.LocationCache")

class EndpointOperationType(object):
    NoneType = "None"
    ReadType = "Read"
    WriteType = "Write"

class RegionalEndpoint(object):
    def __init__(self, c_endpoint: str, p_endpoint: str):
        self.current_endpoint = c_endpoint
        self.previous_endpoint = p_endpoint

    def set_current(self, endpoint: str):
        self.current_endpoint = endpoint

    def set_previous(self, endpoint: str):
        self.previous_endpoint = endpoint

    def get_current(self):
        return self.current_endpoint

    def get_previous(self):
        return self.previous_endpoint

    def __eq__(self, other):
        return (self.current_endpoint == other.current_endpoint
                and self.previous_endpoint == other.previous_endpoint)

    def __str__(self):
        return "Current: " + self.current_endpoint + " ,Previous: " + self.previous_endpoint

    def swap(self):
        temp = self.current_endpoint
        self.current_endpoint = self.previous_endpoint
        self.previous_endpoint = temp
        logger.warning("Swapped regional endpoint values: Current: " + self.current_endpoint +
                       " ,Previous: " + self.previous_endpoint)


def get_endpoints_by_location(new_locations,
                              old_endpoints_by_location,
                              default_regional_endpoint,
                              writes,
                              use_multiple_write_locations):
    # construct from previous object
    endpoints_by_location = collections.OrderedDict()
    parsed_locations = []


    for new_location in new_locations: # pylint: disable=too-many-nested-blocks
        # if name in new_location and same for database account endpoint
        if "name" in new_location and "databaseAccountEndpoint" in new_location:
            if not new_location["name"]:
                # during fail-over the location name is empty
                continue
            try:
                region_uri = new_location["databaseAccountEndpoint"]
                parsed_locations.append(new_location["name"])
                if new_location["name"] in old_endpoints_by_location:
                    regional_object = old_endpoints_by_location[new_location["name"]]
                    current = regional_object.get_current()
                    # swap the previous with current and current with new region_uri received from the gateway
                    if current != region_uri:
                        regional_object.set_previous(current)
                        regional_object.set_current(region_uri)
                # This is the bootstrapping condition
                else:
                    regional_object = RegionalEndpoint(region_uri, region_uri)
                    # if it is for writes, then we update the previous to default_endpoint
                    if writes and not use_multiple_write_locations:
                        # if region_uri is different than global endpoint set global endpoint
                        # as fallback
                        # else construct regional uri
                        if region_uri != default_regional_endpoint.get_current():
                            regional_object.set_previous(default_regional_endpoint.get_current())
                        else:
                            constructed_region_uri =  LocationCache.GetLocationalEndpoint(
                                default_regional_endpoint.get_current(),
                                new_location["name"])
                            regional_object.set_previous(constructed_region_uri)
                # pass in object with region uri , last known good, curr etc
                endpoints_by_location.update({new_location["name"]: regional_object})
            except Exception as e:
                raise e

    return endpoints_by_location, parsed_locations


class LocationCache(object):  # pylint: disable=too-many-public-methods,too-many-instance-attributes
    def current_time_millis(self):
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
        self.default_regional_endpoint = RegionalEndpoint(default_endpoint, default_endpoint)
        self.enable_endpoint_discovery = enable_endpoint_discovery
        self.use_multiple_write_locations = use_multiple_write_locations
        self.enable_multiple_writable_locations = False
        self.write_regional_endpoints = [self.default_regional_endpoint]
        self.read_regional_endpoints = [self.default_regional_endpoint]
        self.location_unavailability_info_by_endpoint = {}
        self.refresh_time_interval_in_ms = refresh_time_interval_in_ms
        self.last_cache_update_time_stamp = 0
        self.available_read_regional_endpoints_by_location = {} # pylint: disable=name-too-long
        self.available_write_regional_endpoints_by_location = {} # pylint: disable=name-too-long
        self.available_write_locations = []
        self.available_read_locations = []

    def check_and_update_cache(self):
        if (
            self.location_unavailability_info_by_endpoint
            and self.current_time_millis() - self.last_cache_update_time_stamp > self.refresh_time_interval_in_ms
        ):
            self.update_location_cache()

    def get_write_regional_endpoints(self):
        self.check_and_update_cache()
        return self.write_regional_endpoints

    def get_read_regional_endpoints(self):
        self.check_and_update_cache()
        return self.read_regional_endpoints

    def get_write_regional_endpoint(self):
        return self.get_write_regional_endpoints()[0].get_current()

    def get_read_regional_endpoint(self):
        return self.get_read_regional_endpoints()[0].get_current()

    def mark_endpoint_unavailable_for_read(self, endpoint, refresh_cache):
        self.mark_endpoint_unavailable(endpoint, EndpointOperationType.ReadType, refresh_cache)

    def mark_endpoint_unavailable_for_write(self, endpoint, refresh_cache):
        self.mark_endpoint_unavailable(endpoint, EndpointOperationType.WriteType, refresh_cache)

    def perform_on_database_account_read(self, database_account):
        self.update_location_cache(
            database_account._WritableLocations,
            database_account._ReadableLocations,
            database_account._EnableMultipleWritableLocations,
        )

    def get_ordered_write_locations(self):
        return self.available_write_locations

    def get_ordered_read_locations(self):
        return self.available_read_locations

    # This updates the current and previous of the regional endpoint
    # to keep it up to date with the success and failure cases
    # This is only called on write operation failures as of now.
    def swap_regional_endpoint_values(self, request):
        location_index = int(request.location_index_to_route) if request.location_index_to_route else 0
        regional_endpoints = (
            self.get_write_regional_endpoints()
            if documents._OperationType.IsWriteOperation(request.operation_type)
            else self.get_read_regional_endpoints()
        )
        regional_endpoint = regional_endpoints[location_index % len(regional_endpoints)]
        if request.location_endpoint_to_route == regional_endpoint.get_current():
            logger.warning("Swapping regional endpoint values: %s",
                           str(regional_endpoint))
            regional_endpoint.swap()

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
                if (self.available_write_locations
                        and write_location in self.available_write_regional_endpoints_by_location):
                    write_regional_endpoint = self.available_write_regional_endpoints_by_location[write_location]
                    if (request.last_routed_location_endpoint_within_region is not None
                            and request.last_routed_location_endpoint_within_region
                            == write_regional_endpoint.get_current()):
                        return write_regional_endpoint.get_previous()
                    return write_regional_endpoint.get_current()
                return self.default_regional_endpoint.get_current()

        regional_endpoints = (
            self.get_write_regional_endpoints()
            if documents._OperationType.IsWriteOperation(request.operation_type)
            else self.get_read_regional_endpoints()
        )
        regional_endpoint = regional_endpoints[location_index % len(regional_endpoints)]
        if (request.last_routed_location_endpoint_within_region is not None
                and request.last_routed_location_endpoint_within_region == regional_endpoint.get_current()):
            return regional_endpoint.get_previous()
        return regional_endpoint.get_current()

    def should_refresh_endpoints(self):  # pylint: disable=too-many-return-statements
        most_preferred_location = self.preferred_locations[0] if self.preferred_locations else None

        # we should schedule refresh in background if we are unable to target the user's most preferredLocation.
        if self.enable_endpoint_discovery:

            should_refresh = self.use_multiple_write_locations and not self.enable_multiple_writable_locations

            if (most_preferred_location and most_preferred_location in
                    self.available_read_regional_endpoints_by_location):
                if (self.available_read_regional_endpoints_by_location
                        and most_preferred_location in self.available_read_regional_endpoints_by_location):
                    most_preferred_read_endpoint = (
                        self.available_read_regional_endpoints_by_location)[most_preferred_location]
                    if most_preferred_read_endpoint and most_preferred_read_endpoint != self.read_regional_endpoints[0]:
                        # For reads, we can always refresh in background as we can alternate to
                        # other available read endpoints
                        return True
                else:
                    return True

            if not self.can_use_multiple_write_locations():
                if self.is_regional_endpoint_unavailable(self.write_regional_endpoints[0],
                                                         EndpointOperationType.WriteType):
                    # same logic as other
                    # Since most preferred write endpoint is unavailable, we can only refresh in background if
                    # we have an alternate write endpoint
                    return True
                return should_refresh
            if (most_preferred_location and
                    most_preferred_location in self.available_write_regional_endpoints_by_location):
                most_preferred_write_regional_endpoint = (
                    self.available_write_regional_endpoints_by_location)[most_preferred_location]
                if most_preferred_write_regional_endpoint:
                    should_refresh |= most_preferred_write_regional_endpoint != self.write_regional_endpoints[0]
                    return should_refresh
                return True
            return should_refresh
        return False

    def clear_stale_endpoint_unavailability_info(self):
        new_location_unavailability_info = {}
        if self.location_unavailability_info_by_endpoint:
            for unavailable_endpoint in self.location_unavailability_info_by_endpoint:  #pylint: disable=consider-using-dict-items
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

    def is_regional_endpoint_unavailable(self, endpoint: RegionalEndpoint, operation_type: str):
        # For writes only mark it unavailable if both are down
        if not _OperationType.IsReadOnlyOperation(operation_type):
            return (self.is_endpoint_unavailable_internal(endpoint.get_current(), operation_type)
                    and self.is_endpoint_unavailable_internal(endpoint.get_previous(), operation_type))

        # For reads mark the region as down if either of the endpoints are unavailable
        return (self.is_endpoint_unavailable_internal(endpoint.get_current(), operation_type)
                or self.is_endpoint_unavailable_internal(endpoint.get_previous(), operation_type))

    def is_endpoint_unavailable_internal(self, endpoint: str, expected_available_operation: str):
        unavailability_info = (
            self.location_unavailability_info_by_endpoint[endpoint]
            if endpoint in self.location_unavailability_info_by_endpoint
            else None
        )

        if (
            expected_available_operation == EndpointOperationType.NoneType
            or not unavailability_info
            or expected_available_operation not in unavailability_info["operationType"]
        ):
            return False

        if (
            self.current_time_millis() - unavailability_info["lastUnavailabilityCheckTimeStamp"]
            > self.refresh_time_interval_in_ms
        ):
            return False
        # Unexpired entry present. Endpoint is unavailable
        return True

    def mark_endpoint_unavailable(self, unavailable_endpoint: str, unavailable_operation_type, refresh_cache: bool):
        logger.warning("Marking %s unavailable for %s ",
                       unavailable_endpoint,
                       unavailable_operation_type)
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

        if refresh_cache:
            self.update_location_cache()

    def get_preferred_locations(self):
        return self.preferred_locations

    def update_location_cache(self, write_locations=None, read_locations=None, enable_multiple_writable_locations=None):
        if enable_multiple_writable_locations:
            self.enable_multiple_writable_locations = enable_multiple_writable_locations

        self.clear_stale_endpoint_unavailability_info()

        if self.enable_endpoint_discovery:
            if read_locations:
                (self.available_read_regional_endpoints_by_location,
                 self.available_read_locations) = get_endpoints_by_location(
                    read_locations,
                    self.available_read_regional_endpoints_by_location,
                    self.default_regional_endpoint,
                    False,
                    self.use_multiple_write_locations
                )

            if write_locations:
                (self.available_write_regional_endpoints_by_location,
                 self.available_write_locations) = get_endpoints_by_location(
                    write_locations,
                    self.available_write_regional_endpoints_by_location,
                    self.default_regional_endpoint,
                    True,
                    self.use_multiple_write_locations,
                )

        self.write_regional_endpoints = self.get_preferred_available_regional_endpoints(
            self.available_write_regional_endpoints_by_location,
            self.available_write_locations,
            EndpointOperationType.WriteType,
            self.default_regional_endpoint,
        )
        self.read_regional_endpoints = self.get_preferred_available_regional_endpoints(
            self.available_read_regional_endpoints_by_location,
            self.available_read_locations,
            EndpointOperationType.ReadType,
            self.write_regional_endpoints[0],
        )
        self.last_cache_update_timestamp = self.current_time_millis()  # pylint: disable=attribute-defined-outside-init

    def get_preferred_available_regional_endpoints( # pylint: disable=name-too-long
        self, endpoints_by_location, orderedLocations, expected_available_operation, fallback_endpoint
    ):
        regional_endpoints = []
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
                        regional_endpoint = endpoints_by_location[location] if location in endpoints_by_location \
                            else None
                        if regional_endpoint:
                            if self.is_regional_endpoint_unavailable(regional_endpoint, expected_available_operation):
                                unavailable_endpoints.append(regional_endpoint)
                            else:
                                regional_endpoints.append(regional_endpoint)

                if not regional_endpoints:
                    regional_endpoints.append(fallback_endpoint)

                regional_endpoints.extend(unavailable_endpoints)
            else:
                for location in orderedLocations:
                    if location and location in endpoints_by_location:
                        # location is empty during manual failover
                        regional_endpoint = endpoints_by_location[location]
                        regional_endpoints.append(regional_endpoint)

        if not regional_endpoints:
            regional_endpoints.append(fallback_endpoint)

        return regional_endpoints

    def can_use_multiple_write_locations(self):
        return self.use_multiple_write_locations and self.enable_multiple_writable_locations

    def can_use_multiple_write_locations_for_request(self, request):  # pylint: disable=name-too-long
        return self.can_use_multiple_write_locations() and (
            request.resource_type == http_constants.ResourceType.Document
            or (
                request.resource_type == http_constants.ResourceType.StoredProcedure
                and request.operation_type == documents._OperationType.ExecuteJavaScript
            )
        )

    @staticmethod
    def GetLocationalEndpoint(default_endpoint, location_name):
        # For default_endpoint like 'https://contoso.documents.azure.com:443/' parse it to
        # generate URL format. This default_endpoint should be global endpoint(and cannot
        # be a locational endpoint) and we agreed to document that
        endpoint_url = urlparse(default_endpoint)

        # hostname attribute in endpoint_url will return 'contoso.documents.azure.com'
        if endpoint_url.hostname is not None:
            hostname_parts = str(endpoint_url.hostname).lower().split(".")
            if hostname_parts is not None:
                # global_database_account_name will return 'contoso'
                global_database_account_name = hostname_parts[0]

                # Prepare the locational_database_account_name as contoso-eastus for location_name 'east us'
                locational_database_account_name = global_database_account_name + "-" + location_name.replace(" ", "")
                locational_database_account_name = locational_database_account_name.lower()

                # Replace 'contoso' with 'contoso-eastus' and return locational_endpoint
                # as https://contoso-eastus.documents.azure.com:443/
                locational_endpoint = default_endpoint.lower().replace(
                    global_database_account_name, locational_database_account_name, 1
                )
                return locational_endpoint

        return None
