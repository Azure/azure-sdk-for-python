# The MIT License (MIT)
# Copyright (c) 2021 Microsoft Corporation

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

"""Internal class for global endpoint manager for circuit breaker.
"""
import logging
import os

from azure.cosmos import documents

from azure.cosmos._partition_health_tracker import PartitionHealthTracker
from azure.cosmos._routing.routing_range import PartitionKeyRangeWrapper
from azure.cosmos._location_cache import EndpointOperationType, LocationCache
from azure.cosmos._request_object import RequestObject
from azure.cosmos.http_constants import ResourceType, HttpHeaders
from azure.cosmos._constants import _Constants as Constants


logger = logging.getLogger("azure.cosmos._GlobalEndpointManagerForCircuitBreakerCore")

class _GlobalPartitionEndpointManagerForCircuitBreakerCore(object):
    """
    This internal class implements the logic for partition endpoint management for
    geo-replicated database accounts.
    """


    def __init__(self, client, location_cache: LocationCache):
        self.partition_health_tracker = PartitionHealthTracker()
        self.location_cache = location_cache
        self.client = client

    def is_circuit_breaker_applicable(self, request: RequestObject) -> bool:
        """
        Check if circuit breaker is applicable for a request.
        """
        if not request:
            return False

        circuit_breaker_enabled = os.environ.get(Constants.CIRCUIT_BREAKER_ENABLED_CONFIG,
                                                 Constants.CIRCUIT_BREAKER_ENABLED_CONFIG_DEFAULT) == "True"
        if not circuit_breaker_enabled:
            return False

        if (not self.location_cache.can_use_multiple_write_locations_for_request(request)
                and documents._OperationType.IsWriteOperation(request.operation_type)):
            return False

        if request.resource_type != ResourceType.Document:
            return False

        if request.operation_type == documents._OperationType.QueryPlan:
            return False

        return True

    def _create_pk_range_wrapper(self, request: RequestObject) -> PartitionKeyRangeWrapper:
        """
        Create a PartitionKeyRangeWrapper object.
        """
        container_rid = request.headers[HttpHeaders.IntendedCollectionRID]
        partition_key = request.headers[HttpHeaders.PartitionKey]
        # get the partition key range for the given partition key
        target_container_link = None
        for container_link, properties in self.client._container_properties_cache.items():
            if properties["_rid"] == container_rid:
                target_container_link = container_link
        if not target_container_link:
            raise RuntimeError("Illegal state: the container cache is not properly initialized.")
        # TODO: @tvaron3 check different clients and create them in different ways
        pk_range = await self.client._routing_map_provider.get_overlapping_ranges(target_container_link, partition_key)
        return PartitionKeyRangeWrapper(pk_range, container_rid)

    def record_failure(
            self,
            request: RequestObject
    ) -> None:
        if self.is_circuit_breaker_applicable(request):
            #convert operation_type to EndpointOperationType
            endpoint_operation_type = EndpointOperationType.WriteType if (
                documents._OperationType.IsWriteOperation(request.operation_type)) else EndpointOperationType.ReadType
            location = self.location_cache.get_location_from_endpoint(str(request.location_endpoint_to_route))
            pkrange_wrapper = self._create_pk_range_wrapper(request)
            self.partition_health_tracker.add_failure(pkrange_wrapper, endpoint_operation_type, str(location))

    # TODO: @tvaron3 lower request timeout to 5.5 seconds for recovering
    # TODO: @tvaron3 exponential backoff for recovering


    def add_excluded_locations_to_request(self, request: RequestObject) -> RequestObject:
        if self.is_circuit_breaker_applicable(request):
            pkrange_wrapper = self._create_pk_range_wrapper(request)
            request.set_excluded_locations_from_circuit_breaker(
                self.partition_health_tracker.get_excluded_locations(pkrange_wrapper)
            )
        return request

    def mark_partition_unavailable(self, request: RequestObject) -> None:
        """
        Mark the partition unavailable from the given request.
        """
        location = self.location_cache.get_location_from_endpoint(str(request.location_endpoint_to_route))
        pkrange_wrapper = self._create_pk_range_wrapper(request)
        self.partition_health_tracker.mark_partition_unavailable(pkrange_wrapper, location)

    def record_success(
            self,
            request: RequestObject
    ) -> None:
        if self.is_circuit_breaker_applicable(request):
            #convert operation_type to either Read or Write
            endpoint_operation_type = EndpointOperationType.WriteType if (
                documents._OperationType.IsWriteOperation(request.operation_type)) else EndpointOperationType.ReadType
            location = self.location_cache.get_location_from_endpoint(str(request.location_endpoint_to_route))
            pkrange_wrapper = self._create_pk_range_wrapper(request)
            self.partition_health_tracker.add_success(pkrange_wrapper, endpoint_operation_type, location)

# TODO: @tvaron3 there should be no in region retries when trying on healthy tentative -----------------------
