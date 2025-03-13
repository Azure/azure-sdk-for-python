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
from typing import Set
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

class RegionalRoutingContext(object):
    def __init__(self, primary_endpoint: str, alternate_endpoint: str):
        self.primary_endpoint = primary_endpoint
        self.alternate_endpoint = alternate_endpoint

    def set_primary(self, endpoint: str):
        self.primary_endpoint = endpoint

    def set_alternate(self, endpoint: str):
        self.alternate_endpoint = endpoint

    def get_primary(self):
        return self.primary_endpoint

    def get_alternate(self):
        return self.alternate_endpoint

    def __eq__(self, other):
        return (self.primary_endpoint == other.primary_endpoint
                and self.alternate_endpoint == other.alternate_endpoint)

    def __str__(self):
        return "Primary: " + self.primary_endpoint + ", Alternate: " + self.alternate_endpoint

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
                if not writes or use_multiple_write_locations:
                    regional_object = RegionalRoutingContext(region_uri, region_uri)
                elif new_location["name"] in old_endpoints_by_location:
                    regional_object = old_endpoints_by_location[new_location["name"]]
                    current = regional_object.get_primary()
                    # swap the previous with current and current with new region_uri received from the gateway
                    if current != region_uri:
                        regional_object.set_alternate(current)
                        regional_object.set_primary(region_uri)
                # This is the bootstrapping condition
                else:
                    regional_object = RegionalRoutingContext(region_uri, region_uri)
                    # if it is for writes, then we update the previous to default_endpoint
                    if writes:
                        # if region_uri is different than global endpoint set global endpoint
                        # as fallback
                        # else construct regional uri
                        if region_uri != default_regional_endpoint.get_primary():
                            regional_object.set_alternate(default_regional_endpoint.get_primary())
                        else:
                            constructed_region_uri =  LocationCache.GetLocationalEndpoint(
                                default_regional_endpoint.get_primary(),
                                new_location["name"])
                            regional_object.set_alternate(constructed_region_uri)
                # pass in object with region uri , last known good, curr etc
                endpoints_by_location.update({new_location["name"]: regional_object})
            except Exception as e:
                raise e

    return endpoints_by_location, parsed_locations

def add_endpoint_if_preferred(endpoint: str, preferred_endpoints: Set[str], endpoints: Set[str]) -> bool:
    if endpoint in preferred_endpoints:
        endpoints.add(endpoint)
        return True
    return False

def _get_health_check_endpoints(
        account_regional_routing_contexts_by_location,
        regional_routing_contexts) -> Set[str]:
    # only check 2 read regions and 2 write regions
    region_count = 2
    # should use the endpoints in the order returned from gateway and only the ones specified in preferred locations
    endpoints: Set[str] = set()
    i = 0
    preferred_endpoints = {context.get_primary() for context in regional_routing_contexts}.union(
        {context.get_alternate() for context in regional_routing_contexts}
    )

    for regional_routing_context in account_regional_routing_contexts_by_location.values():
        region_added = add_endpoint_if_preferred(
            regional_routing_context.get_primary(),
            preferred_endpoints,
            endpoints)
        region_added |= add_endpoint_if_preferred(
            regional_routing_context.get_alternate(),
            preferred_endpoints,
            endpoints)

        if region_added:
            i += 1
        if i == region_count:
            break

    return endpoints


class LocationCache(object):  # pylint: disable=too-many-public-methods,too-many-instance-attributes
    def current_time_millis(self):
        return int(round(time.time() * 1000))

    def __init__(
        self,
        preferred_locations,
        default_endpoint,
        enable_endpoint_discovery,
        use_multiple_write_locations,
    ):
        self.preferred_locations = preferred_locations
        self.default_regional_routing_context = RegionalRoutingContext(default_endpoint, default_endpoint)
        self.enable_endpoint_discovery = enable_endpoint_discovery
        self.use_multiple_write_locations = use_multiple_write_locations
        self.enable_multiple_writable_locations = False
        self.write_regional_routing_contexts = [self.default_regional_routing_context]
        self.read_regional_routing_contexts = [self.default_regional_routing_context]
        self.location_unavailability_info_by_endpoint = {}
        self.last_cache_update_time_stamp = 0
        self.account_read_regional_routing_contexts_by_location = {} # pylint: disable=name-too-long
        self.account_write_regional_routing_contexts_by_location = {} # pylint: disable=name-too-long
        self.account_write_locations = []
        self.account_read_locations = []

    def get_write_regional_routing_contexts(self):
        return self.write_regional_routing_contexts

    def get_read_regional_routing_contexts(self):
        return self.read_regional_routing_contexts

    def get_write_regional_routing_context(self):
        return self.get_write_regional_routing_contexts()[0].get_primary()

    def get_read_regional_routing_context(self):
        return self.get_read_regional_routing_contexts()[0].get_primary()

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
        return self.account_write_locations

    def get_ordered_read_locations(self):
        return self.account_read_locations

    def resolve_service_endpoint(self, request):
        if request.location_endpoint_to_route:
            return request.location_endpoint_to_route

        location_index = int(request.location_index_to_route) if request.location_index_to_route else 0
        use_preferred_locations = (
            request.use_preferred_locations if request.use_preferred_locations is not None else True
        )

        # whether to check for write or read unavailable
        endpoint_operation_type = EndpointOperationType.WriteType if (
            documents._OperationType.IsWriteOperation(request.operation_type)) else EndpointOperationType.ReadType

        if not use_preferred_locations or (
            documents._OperationType.IsWriteOperation(request.operation_type)
            and not self.can_use_multiple_write_locations_for_request(request)
        ):
            # For non-document resource types in case of client can use multiple write locations
            # or when client cannot use multiple write locations, flip-flop between the
            # first and the second writable region in DatabaseAccount (for manual failover)
            if self.enable_endpoint_discovery and self.account_write_locations:
                location_index = min(location_index % 2, len(self.account_write_locations) - 1)
                write_location = self.account_write_locations[location_index]
                if (self.account_write_regional_routing_contexts_by_location
                        and write_location in self.account_write_regional_routing_contexts_by_location):
                    write_regional_routing_context = (
                        self.account_write_regional_routing_contexts_by_location)[write_location]
                    if (
                            request.last_routed_location_endpoint_within_region is not None
                            and request.last_routed_location_endpoint_within_region
                            == write_regional_routing_context.get_primary()
                            or self.is_endpoint_unavailable_internal(write_regional_routing_context.get_primary(),
                                                             endpoint_operation_type)
                    ):
                        return write_regional_routing_context.get_alternate()
                    return write_regional_routing_context.get_primary()
            # if endpoint discovery is off for reads it should use passed in endpoint
            return self.default_regional_routing_context.get_primary()

        regional_routing_contexts = (
            self.get_write_regional_routing_contexts()
            if documents._OperationType.IsWriteOperation(request.operation_type)
            else self.get_read_regional_routing_contexts()
        )
        regional_routing_context = regional_routing_contexts[location_index % len(regional_routing_contexts)]
        if (
                request.last_routed_location_endpoint_within_region is not None
                and request.last_routed_location_endpoint_within_region
                == regional_routing_context.get_primary()
                or self.is_endpoint_unavailable_internal(regional_routing_context.get_primary(),
                                                          endpoint_operation_type)
        ):
            return regional_routing_context.get_alternate()
        return regional_routing_context.get_primary()

    def should_refresh_endpoints(self):  # pylint: disable=too-many-return-statements
        most_preferred_location = self.preferred_locations[0] if self.preferred_locations else None

        # we should schedule refresh in background if we are unable to target the user's most preferredLocation.
        if self.enable_endpoint_discovery:

            should_refresh = self.use_multiple_write_locations and not self.enable_multiple_writable_locations

            if (most_preferred_location and most_preferred_location in
                    self.account_read_regional_routing_contexts_by_location):
                if (self.account_read_regional_routing_contexts_by_location
                        and most_preferred_location in self.account_read_regional_routing_contexts_by_location):
                    most_preferred_read_endpoint = (
                        self.account_read_regional_routing_contexts_by_location)[most_preferred_location]
                    if (most_preferred_read_endpoint and
                            most_preferred_read_endpoint != self.read_regional_routing_contexts[0]):
                        # For reads, we can always refresh in background as we can alternate to
                        # other available read endpoints
                        return True
                else:
                    return True

            if not self.can_use_multiple_write_locations():
                if self.is_location_unavailable(self.write_regional_routing_contexts[0],
                                                EndpointOperationType.WriteType):
                    # same logic as other
                    # Since most preferred write endpoint is unavailable, we can only refresh in background if
                    # we have an alternate write endpoint
                    return True
                return should_refresh
            if (most_preferred_location and
                    most_preferred_location in self.account_write_regional_routing_contexts_by_location):
                most_preferred_write_regional_endpoint = (
                    self.account_write_regional_routing_contexts_by_location)[most_preferred_location]
                if most_preferred_write_regional_endpoint:
                    should_refresh |= most_preferred_write_regional_endpoint != self.write_regional_routing_contexts[0]
                    return should_refresh
                return True
            return should_refresh
        return False

    def is_location_unavailable(self, endpoint: RegionalRoutingContext, operation_type: str):
        # For writes with single write region accounts only mark it unavailable if both are down
        if not _OperationType.IsReadOnlyOperation(operation_type) and not self.can_use_multiple_write_locations():
            return (self.is_endpoint_unavailable_internal(endpoint.get_primary(), operation_type)
                    and self.is_endpoint_unavailable_internal(endpoint.get_alternate(), operation_type))

        # For reads mark the region as down if primary endpoint is unavailable
        return self.is_endpoint_unavailable_internal(endpoint.get_primary(), operation_type)

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

        # Endpoint is unavailable
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
        if not unavailability_info:
            self.location_unavailability_info_by_endpoint[unavailable_endpoint] = {
                "operationType": set([unavailable_operation_type])
            }
        else:
            unavailable_operations = set([unavailable_operation_type]).union(unavailability_info["operationType"])
            self.location_unavailability_info_by_endpoint[unavailable_endpoint] = {
                "operationType": unavailable_operations
            }

        if refresh_cache:
            self.update_location_cache()

    def mark_endpoint_available(self, available_endpoint: str):
        self.location_unavailability_info_by_endpoint.pop(available_endpoint, "")

    def update_location_cache(self, write_locations=None, read_locations=None, enable_multiple_writable_locations=None):
        if enable_multiple_writable_locations:
            self.enable_multiple_writable_locations = enable_multiple_writable_locations

        if self.enable_endpoint_discovery:
            if read_locations:
                (self.account_read_regional_routing_contexts_by_location,
                 self.account_read_locations) = get_endpoints_by_location(
                    read_locations,
                    self.account_read_regional_routing_contexts_by_location,
                    self.default_regional_routing_context,
                    False,
                    self.use_multiple_write_locations
                )

            if write_locations:
                (self.account_write_regional_routing_contexts_by_location,
                 self.account_write_locations) = get_endpoints_by_location(
                    write_locations,
                    self.account_write_regional_routing_contexts_by_location,
                    self.default_regional_routing_context,
                    True,
                    self.use_multiple_write_locations
                )

        self.write_regional_routing_contexts = self.get_preferred_regional_routing_contexts(
            self.account_write_regional_routing_contexts_by_location,
            self.account_write_locations,
            EndpointOperationType.WriteType,
            self.default_regional_routing_context
        )
        self.read_regional_routing_contexts = self.get_preferred_regional_routing_contexts(
            self.account_read_regional_routing_contexts_by_location,
            self.account_read_locations,
            EndpointOperationType.ReadType,
            self.write_regional_routing_contexts[0]
        )
        self.last_cache_update_timestamp = self.current_time_millis()  # pylint: disable=attribute-defined-outside-init

    def get_preferred_regional_routing_contexts(
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
                            if self.is_location_unavailable(regional_endpoint, expected_available_operation):
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

    def endpoints_to_health_check(self) -> Set[str]:
        # only check 2 read regions and 2 write regions
        # add read endpoints from gateway and in preferred locations
        health_check_endpoints = _get_health_check_endpoints(
            self.account_read_regional_routing_contexts_by_location,
            self.read_regional_routing_contexts
        )
        # add write endpoints from gateway and in preferred locations
        health_check_endpoints.union(_get_health_check_endpoints(
            self.account_write_regional_routing_contexts_by_location,
            self.write_regional_routing_contexts
        ))

        return health_check_endpoints

    # get at most two regional routing contexts in the order from gateway and the ones specified in preferred locations
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
