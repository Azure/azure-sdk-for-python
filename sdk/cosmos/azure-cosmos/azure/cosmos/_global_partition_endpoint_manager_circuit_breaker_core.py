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
import os

from azure.cosmos import documents

from azure.cosmos._partition_health_tracker import _PartitionHealthTracker
from azure.cosmos._routing.routing_range import PartitionKeyRangeWrapper
from azure.cosmos._location_cache import EndpointOperationType, LocationCache
from azure.cosmos._request_object import RequestObject
from azure.cosmos.http_constants import ResourceType, HttpHeaders
from azure.cosmos._constants import _Constants as Constants


class _GlobalPartitionEndpointManagerForCircuitBreakerCore(object):
    """
    This internal class implements the logic for partition endpoint management for
    geo-replicated database accounts.
    """


    def __init__(self, client, location_cache: LocationCache):
        self.partition_health_tracker = _PartitionHealthTracker()
        self.location_cache = location_cache
        self.client = client

    def is_circuit_breaker_applicable(self, request: RequestObject) -> bool:
        if not request:
            return False

        circuit_breaker_enabled = os.environ.get(Constants.CIRCUIT_BREAKER_ENABLED_CONFIG,
                                                 Constants.CIRCUIT_BREAKER_ENABLED_CONFIG_DEFAULT) == "True"
        if not circuit_breaker_enabled:
            return False

        if (not self.location_cache.can_use_multiple_write_locations_for_request(request)
                and documents._OperationType.IsWriteOperation(request.operation_type)): # pylint: disable=protected-access
            return False

        if ((request.resource_type != ResourceType.Document
             and request.resource_type != ResourceType.PartitionKey)
             or request.operation_type == documents._OperationType.QueryPlan): # pylint: disable=protected-access
            return False

        # this is for certain cross partition queries and read all items where we cannot discern partition information
        if (not request.headers.get(HttpHeaders.PartitionKeyRangeID)
                and not request.headers.get(HttpHeaders.PartitionKey)):
            return False

        return True

    def record_failure(
            self,
            request: RequestObject,
            pk_range_wrapper: PartitionKeyRangeWrapper
    ) -> None:
        #convert operation_type to EndpointOperationType
        endpoint_operation_type = (EndpointOperationType.WriteType if (
            documents._OperationType.IsWriteOperation(request.operation_type)) # pylint: disable=protected-access
            else EndpointOperationType.ReadType)
        location = self.location_cache.get_location_from_endpoint(str(request.location_endpoint_to_route))
        self.partition_health_tracker.add_failure(pk_range_wrapper, endpoint_operation_type, str(location))

    def check_stale_partition_info(
            self,
            request: RequestObject,
            pk_range_wrapper: PartitionKeyRangeWrapper
    ) -> None:
        self.partition_health_tracker.check_stale_partition_info(request, pk_range_wrapper)


    def add_excluded_locations_to_request(
            self,
            request: RequestObject,
            pk_range_wrapper: PartitionKeyRangeWrapper
    ) -> RequestObject:
        request.set_excluded_locations_from_circuit_breaker(
            self.partition_health_tracker.get_excluded_locations(request, pk_range_wrapper)
        )
        return request

    def mark_partition_unavailable(self, request: RequestObject, pk_range_wrapper: PartitionKeyRangeWrapper) -> None:
        location = self.location_cache.get_location_from_endpoint(str(request.location_endpoint_to_route))
        self.partition_health_tracker.mark_partition_unavailable(pk_range_wrapper, location)

    def record_success(
            self,
            request: RequestObject,
            pk_range_wrapper: PartitionKeyRangeWrapper
    ) -> None:
        #convert operation_type to either Read or Write
        endpoint_operation_type = EndpointOperationType.WriteType if (
            documents._OperationType.IsWriteOperation(request.operation_type)) else EndpointOperationType.ReadType # pylint: disable=protected-access
        location = self.location_cache.get_location_from_endpoint(str(request.location_endpoint_to_route))
        self.partition_health_tracker.add_success(pk_range_wrapper, endpoint_operation_type, location)
