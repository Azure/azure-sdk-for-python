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
from typing import Set, Mapping, OrderedDict
from urllib.parse import urlparse

from . import documents, _base as base
from .http_constants import ResourceType
from .documents import ConnectionPolicy
from ._request_object import RequestObject

# pylint: disable=protected-access

logger = logging.getLogger("azure.cosmos.LocationCache")

class EndpointOperationType(object):
    NoneType = "None"
    ReadType = "Read"
    WriteType = "Write"

class RegionalRoutingContext(object):
    def __init__(self, primary_endpoint: str):
        self.primary_endpoint: str = primary_endpoint

    def set_primary(self, endpoint: str):
        self.primary_endpoint = endpoint

    def get_primary(self):
        return self.primary_endpoint

    def __eq__(self, other):
        return self.primary_endpoint == other.primary_endpoint

    def __str__(self):
        return "Primary: " + self.primary_endpoint

def get_regional_routing_contexts_by_loc(new_locations: list[dict[str, str]]):
    # construct from previous object
    regional_routing_contexts_by_location: OrderedDict[str, RegionalRoutingContext] = collections.OrderedDict()
    parsed_locations = []

    for new_location in new_locations:
        # if name in new_location and same for database account endpoint
        if "name" in new_location and "databaseAccountEndpoint" in new_location:
            if not new_location["name"]:
                # during fail-over the location name is empty
                continue
            try:
                region_uri = new_location["databaseAccountEndpoint"]
                parsed_locations.append(new_location["name"])
                regional_object = RegionalRoutingContext(region_uri)
                regional_routing_contexts_by_location.update({new_location["name"]: regional_object})
            except Exception as e:
                raise e

    # Also store a hash map of endpoints for each location
    locations_by_endpoints = {value.get_primary(): key for key, value in regional_routing_contexts_by_location.items()}

    return regional_routing_contexts_by_location, locations_by_endpoints, parsed_locations

def _get_health_check_endpoints(regional_routing_contexts) -> Set[str]:
    # should use the endpoints in the order returned from gateway and only the ones specified in preferred locations
    preferred_endpoints = {context.get_primary() for context in regional_routing_contexts}
    return preferred_endpoints

def _get_applicable_regional_routing_contexts(regional_routing_contexts: list[RegionalRoutingContext],
                                              location_name_by_endpoint: Mapping[str, str],
                                              fall_back_regional_routing_context: RegionalRoutingContext,
                                              exclude_location_list: list[str],
                                              resource_type: str) -> list[RegionalRoutingContext]:
    # filter endpoints by excluded locations
    applicable_regional_routing_contexts = []
    excluded_regional_routing_contexts = []
    for regional_routing_context in regional_routing_contexts:
        if location_name_by_endpoint.get(regional_routing_context.get_primary()) not in exclude_location_list:
            applicable_regional_routing_contexts.append(regional_routing_context)
        else:
            excluded_regional_routing_contexts.append(regional_routing_context)

    # Preserves the excluded locations at the end of the list, because for the metadata API calls, excluded locations
    # are not preferred, but all endpoints must be used.
    if base.IsMasterResource(resource_type):
        applicable_regional_routing_contexts.extend(excluded_regional_routing_contexts)

    # If all preferred locations are excluded, use the fallback endpoint.
    if not applicable_regional_routing_contexts:
        applicable_regional_routing_contexts.append(fall_back_regional_routing_context)

    return applicable_regional_routing_contexts

class LocationCache(object):  # pylint: disable=too-many-public-methods,too-many-instance-attributes

    def __init__(
        self,
        default_endpoint: str,
        connection_policy: ConnectionPolicy,
    ):
        self.default_regional_routing_context: RegionalRoutingContext = RegionalRoutingContext(default_endpoint)
        self.effective_preferred_locations: list[str] = []
        self.enable_multiple_writable_locations: bool = False
        self.write_regional_routing_contexts: list[RegionalRoutingContext] = [self.default_regional_routing_context]
        self.read_regional_routing_contexts: list[RegionalRoutingContext] = [self.default_regional_routing_context]
        self.location_unavailability_info_by_endpoint: dict[str, dict[str, Set[EndpointOperationType]]] = {}
        self.last_cache_update_time_stamp: int = 0
        self.account_read_regional_routing_contexts_by_location: dict[str, RegionalRoutingContext] = {} # pylint: disable=name-too-long
        self.account_write_regional_routing_contexts_by_location: dict[str, RegionalRoutingContext] = {} # pylint: disable=name-too-long
        self.account_locations_by_read_endpoints: dict[str, str] = {} # pylint: disable=name-too-long
        self.account_locations_by_write_endpoints: dict[str, str] = {} # pylint: disable=name-too-long
        self.account_write_locations: list[str] = []
        self.account_read_locations: list[str] = []
        self.connection_policy: ConnectionPolicy = connection_policy

    def get_write_regional_routing_contexts(self):
        return self.write_regional_routing_contexts

    def get_read_regional_routing_contexts(self):
        return self.read_regional_routing_contexts

    def get_location_from_endpoint(self, endpoint: str) -> str:
        if endpoint in self.account_locations_by_read_endpoints:
            return self.account_locations_by_read_endpoints[endpoint]
        return self.account_write_locations[0]

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

    def get_all_write_endpoints(self) -> Set[str]:
        return {
            context.get_primary()
            for context in self.get_write_regional_routing_contexts()
        }

    def get_ordered_write_locations(self):
        return self.account_write_locations

    def get_ordered_read_locations(self):
        return self.account_read_locations

    def _get_configured_excluded_locations(self, request: RequestObject) -> list[str]:
        # If excluded locations were configured on request, use request level excluded locations.
        excluded_locations = request.excluded_locations
        if excluded_locations is None:
            if self.connection_policy.ExcludedLocations:
                # If excluded locations were only configured on client(connection_policy), use client level
                # make copy of excluded locations to avoid modifying the original list
                excluded_locations = list(self.connection_policy.ExcludedLocations)
            else:
                excluded_locations = []
        for excluded_location in request.excluded_locations_circuit_breaker:
            if excluded_location not in excluded_locations:
                excluded_locations.append(excluded_location)
        return excluded_locations

    def _get_applicable_read_regional_routing_contexts(self, request: RequestObject) -> list[RegionalRoutingContext]:
        # Get configured excluded locations
        excluded_locations = self._get_configured_excluded_locations(request)

        # If excluded locations were configured, return filtered regional endpoints by excluded locations.
        if excluded_locations:
            return _get_applicable_regional_routing_contexts(
                self.get_read_regional_routing_contexts(),
                self.account_locations_by_read_endpoints,
                self.get_write_regional_routing_contexts()[0],
                excluded_locations,
                request.resource_type)

        # Else, return all regional endpoints
        return self.get_read_regional_routing_contexts()

    def _get_applicable_write_regional_routing_contexts(self, request: RequestObject) -> list[RegionalRoutingContext]:
        # Get configured excluded locations
        excluded_locations = self._get_configured_excluded_locations(request)

        # If excluded locations were configured, return filtered regional endpoints by excluded locations.
        if excluded_locations:
            return _get_applicable_regional_routing_contexts(
                self.get_write_regional_routing_contexts(),
                self.account_locations_by_write_endpoints,
                self.default_regional_routing_context,
                excluded_locations,
                request.resource_type)

        # Else, return all regional endpoints
        return self.get_write_regional_routing_contexts()

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
            if self.connection_policy.EnableEndpointDiscovery and self.account_write_locations:
                location_index = min(location_index % 2, len(self.account_write_locations) - 1)
                write_location = self.account_write_locations[location_index]
                if (self.account_write_regional_routing_contexts_by_location
                        and write_location in self.account_write_regional_routing_contexts_by_location):
                    write_regional_routing_context = (
                        self.account_write_regional_routing_contexts_by_location)[write_location]
                    return write_regional_routing_context.get_primary()
            # if endpoint discovery is off for reads it should use passed in endpoint
            return self.default_regional_routing_context.get_primary()

        regional_routing_contexts = (
            self._get_applicable_write_regional_routing_contexts(request)
            if documents._OperationType.IsWriteOperation(request.operation_type)
            else self._get_applicable_read_regional_routing_contexts(request)
        )
        regional_routing_context = regional_routing_contexts[location_index % len(regional_routing_contexts)]
        return regional_routing_context.get_primary()

    def should_refresh_endpoints(self):  # pylint: disable=too-many-return-statements
        most_preferred_location = self.effective_preferred_locations[0] if self.effective_preferred_locations else None

        # we should schedule refresh in background if we are unable to target the user's most preferredLocation.
        if self.connection_policy.EnableEndpointDiscovery:

            should_refresh = (self.connection_policy.UseMultipleWriteLocations
                              and not self.enable_multiple_writable_locations)

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
                if self.is_endpoint_unavailable(self.write_regional_routing_contexts[0].get_primary(),
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

    def is_endpoint_unavailable(self, endpoint: str, expected_available_operation: str):
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

    def mark_endpoint_unavailable(
            self, unavailable_endpoint: str, unavailable_operation_type: EndpointOperationType, refresh_cache: bool):
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

        if self.connection_policy.EnableEndpointDiscovery:
            if read_locations:
                (self.account_read_regional_routing_contexts_by_location,
                 self.account_locations_by_read_endpoints,
                 self.account_read_locations) = get_regional_routing_contexts_by_loc(read_locations)

            if write_locations:
                (self.account_write_regional_routing_contexts_by_location,
                 self.account_locations_by_write_endpoints,
                 self.account_write_locations) = get_regional_routing_contexts_by_loc(write_locations)

        # if preferred locations is empty and the default endpoint is a global endpoint,
        # we should use the read locations from gateway as effective preferred locations
        if self.connection_policy.PreferredLocations:
            self.effective_preferred_locations = self.connection_policy.PreferredLocations
        elif self.is_default_endpoint_regional():
            self.effective_preferred_locations = []
        elif not self.effective_preferred_locations:
            self.effective_preferred_locations = self.account_read_locations

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

    def get_preferred_regional_routing_contexts(
        self, endpoints_by_location, ordered_locations, expected_available_operation, fallback_endpoint
    ):
        regional_endpoints = []
        # if enableEndpointDiscovery is false, we always use the defaultEndpoint that
        # user passed in during documentClient init
        if self.connection_policy.EnableEndpointDiscovery and endpoints_by_location:  # pylint: disable=too-many-nested-blocks
            if (
                self.can_use_multiple_write_locations()
                or expected_available_operation == EndpointOperationType.ReadType
            ):
                unavailable_endpoints = []
                if self.effective_preferred_locations:
                    # When client can not use multiple write locations, preferred locations
                    # list should only be used determining read endpoints order. If client
                    # can use multiple write locations, preferred locations list should be
                    # used for determining both read and write endpoints order.
                    for location in self.effective_preferred_locations:
                        regional_endpoint = endpoints_by_location.get(location)
                        if regional_endpoint:
                            if self.is_endpoint_unavailable(regional_endpoint.get_primary(),
                                                            expected_available_operation):
                                unavailable_endpoints.append(regional_endpoint)
                            else:
                                regional_endpoints.append(regional_endpoint)

                # If all preferred locations are unavailable, honor the preferred list by trying them anyway.
                if not regional_endpoints and unavailable_endpoints:
                    regional_endpoints.extend(unavailable_endpoints)

                # If there are no preferred locations or none of the preferred locations are in the account,
                # add the fallback endpoint.
                if not regional_endpoints:
                    regional_endpoints.append(fallback_endpoint)
            else:
                for location in ordered_locations:
                    if location and location in endpoints_by_location:
                        # location is empty during manual failover
                        regional_endpoint = endpoints_by_location[location]
                        regional_endpoints.append(regional_endpoint)

        if not regional_endpoints:
            regional_endpoints.append(fallback_endpoint)

        return regional_endpoints

    # if the endpoint is returned from the gateway in the account topology, it is a regional endpoint
    def is_default_endpoint_regional(self) -> bool:
        return any(
            context.get_primary() == self.default_regional_routing_context.get_primary()
            for context in self.account_read_regional_routing_contexts_by_location.values()
        )

    def can_use_multiple_write_locations(self):
        return self.connection_policy.UseMultipleWriteLocations and self.enable_multiple_writable_locations

    def can_use_multiple_write_locations_for_request(self, request):  # pylint: disable=name-too-long
        return self.can_use_multiple_write_locations() and (
            request.resource_type == ResourceType.Document
            or request.resource_type == ResourceType.PartitionKey
            or (
                request.resource_type == ResourceType.StoredProcedure
                and request.operation_type == documents._OperationType.ExecuteJavaScript
            )
        )

    def endpoints_to_health_check(self) -> Set[str]:
        # add read endpoints from gateway and in preferred locations
        health_check_endpoints = _get_health_check_endpoints(self.read_regional_routing_contexts)
        # add first write endpoint in case that the write region is not in preferred locations
        health_check_endpoints = health_check_endpoints.union(
            _get_health_check_endpoints(self.write_regional_routing_contexts[:1]
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
