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
from typing import TYPE_CHECKING, Optional

from azure.cosmos import PartitionKey
from azure.cosmos._global_partition_endpoint_manager_circuit_breaker_core import \
    _GlobalPartitionEndpointManagerForCircuitBreakerCore
from azure.cosmos._routing.routing_range import PartitionKeyRangeWrapper, Range

from azure.cosmos.aio._global_endpoint_manager_async import _GlobalEndpointManager
from azure.cosmos._request_object import RequestObject
from azure.cosmos.http_constants import HttpHeaders

if TYPE_CHECKING:
    from azure.cosmos.aio._cosmos_client_connection_async import CosmosClientConnection


# pylint: disable=protected-access
class _GlobalPartitionEndpointManagerForCircuitBreakerAsync(_GlobalEndpointManager):
    """
    This internal class implements the logic for partition endpoint management for
    geo-replicated database accounts.
    """

    def __init__(self, client: "CosmosClientConnection"):
        super(_GlobalPartitionEndpointManagerForCircuitBreakerAsync, self).__init__(client)
        self.global_partition_endpoint_manager_core = (
            _GlobalPartitionEndpointManagerForCircuitBreakerCore(client, self.location_cache))

    async def create_pk_range_wrapper(self, request: RequestObject) -> Optional[PartitionKeyRangeWrapper]:
        if HttpHeaders.IntendedCollectionRID in request.headers:
            container_rid = request.headers[HttpHeaders.IntendedCollectionRID]
        else:
            self.global_partition_endpoint_manager_core.log_warn_or_debug(
                "Illegal state: the request does not contain container information. "
                "Circuit breaker cannot be performed.")
            return None
        properties = self.client._container_properties_cache[container_rid]
        # get relevant information from container cache to get the overlapping ranges
        container_link = properties["container_link"]
        partition_key_definition = properties["partitionKey"]
        partition_key = PartitionKey(path=partition_key_definition["paths"],
                                     kind=partition_key_definition["kind"],
                                     version=partition_key_definition["version"])

        if HttpHeaders.PartitionKey in request.headers:
            partition_key_value = request.headers[HttpHeaders.PartitionKey]
            # get the partition key range for the given partition key
            epk_range = [partition_key._get_epk_range_for_partition_key(partition_key_value)]
            partition_ranges = await (self.client._routing_map_provider
                                      .get_overlapping_ranges(container_link, epk_range))
            partition_range = Range.PartitionKeyRangeToRange(partition_ranges[0])
        elif HttpHeaders.PartitionKeyRangeID in request.headers:
            pk_range_id = request.headers[HttpHeaders.PartitionKeyRangeID]
            epk_range = await (self.client._routing_map_provider
                           .get_range_by_partition_key_range_id(container_link, pk_range_id))
            if not epk_range:
                self.global_partition_endpoint_manager_core.log_warn_or_debug(
                    "Illegal state: partition key range cache not initialized correctly. "
                    "Circuit breaker cannot be performed.")
                return None
            partition_range = Range.PartitionKeyRangeToRange(epk_range)
        else:
            self.global_partition_endpoint_manager_core.log_warn_or_debug(
                "Illegal state: the request does not contain partition information. "
                "Circuit breaker cannot be performed.")
            return None

        return PartitionKeyRangeWrapper(partition_range, container_rid)

    def is_circuit_breaker_applicable(self, request: RequestObject) -> bool:
        return self.global_partition_endpoint_manager_core.is_circuit_breaker_applicable(request)

    async def record_failure(
            self,
            request: RequestObject
    ) -> None:
        if self.is_circuit_breaker_applicable(request):
            pk_range_wrapper = await self.create_pk_range_wrapper(request)
            if pk_range_wrapper:
                self.global_partition_endpoint_manager_core.record_failure(request, pk_range_wrapper)

    def resolve_service_endpoint_for_partition(
            self,
            request: RequestObject,
            pk_range_wrapper: Optional[PartitionKeyRangeWrapper]
    ):
        if self.is_circuit_breaker_applicable(request) and pk_range_wrapper:
            self.global_partition_endpoint_manager_core.check_stale_partition_info(request, pk_range_wrapper)
            request = self.global_partition_endpoint_manager_core.add_excluded_locations_to_request(request,
                                                                                                    pk_range_wrapper)
        return self._resolve_service_endpoint(request)

    async def record_success(
            self,
            request: RequestObject
    ) -> None:
        if self.is_circuit_breaker_applicable(request):
            pk_range_wrapper = await self.create_pk_range_wrapper(request)
            if pk_range_wrapper:
                self.global_partition_endpoint_manager_core.record_success(request, pk_range_wrapper)
