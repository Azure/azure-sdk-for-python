# The MIT License (MIT)
# Copyright (c) 2025 Microsoft Corporation

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

"""Internal class for async connection reset retry policy implementation in the Azure
Cosmos database service.
"""

from typing import Optional
from azure.cosmos import http_constants


class PartitionKeyRangeGoneRetryPolicyAsync(object):
    """Async retry policy for handling partition key range gone errors.

    This policy handles Gone (410) errors caused by partition splits or merges
    by refreshing the routing map cache asynchronously before allowing retry.
    """

    def __init__(self, client, *args, **kwargs):
        self.retry_after_in_milliseconds = 1000
        self.refresh_partition_key_range_cache = True
        self.args = args
        self.client = client
        self.exception = None
        self.kwargs = kwargs

    async def ShouldRetry(self, exception):
        """Returns true if the request should retry based on the passed-in exception.

        :param (exceptions.CosmosHttpResponseError instance) exception:
        :returns: a boolean stating whether the request should be retried
        :rtype: bool
        """
        self.exception = exception

        # Extract collection rid and link from request
        collection_link: Optional[str] = None

        if len(self.args) > 3:
            request = self.args[3]  # request object
            if hasattr(request, 'headers'):
                collection_rid = request.headers.get(http_constants.HttpHeaders.IntendedCollectionRID)
                cached_properties = self.client._container_properties_cache.get(collection_rid)
                if cached_properties:
                    collection_link = cached_properties.get("container_link")

        if self.refresh_partition_key_range_cache:
            previous_routing_map = None
            if collection_link and hasattr(self.client, '_routing_map_provider'):
                if hasattr(self.client._routing_map_provider, '_collection_routing_map_by_item'):
                    previous_routing_map = self.client._routing_map_provider._collection_routing_map_by_item.get(
                        collection_link)

            # Only clear the cache if it's not already empty.
            if previous_routing_map is not None:
                # Asynchronous refresh for async client
                await self.client.refresh_routing_map_provider(collection_link, previous_routing_map)

            self.refresh_partition_key_range_cache = False

        # return False to raise error to multi_execution_aggregator and repair document producer context
        return False