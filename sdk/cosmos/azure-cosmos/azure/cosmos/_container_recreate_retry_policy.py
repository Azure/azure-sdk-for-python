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

"""Internal class for container recreate retry policy implementation in the Azure
Cosmos database service.
"""

from typing import Optional, Dict, Any
from . import http_constants

# pylint: disable=protected-access


class ContainerRecreateRetryPolicy(object):
    def __init__(self, client, *args):
        self.retry_after_in_milliseconds = 0  # Same as in .net
        self.refresh_container_properties_cache = True
        self.args = args
        self.intendedHeaders = http_constants.HttpHeaders.IntendedCollectionRID
        if args and len(args) >= 4 and self.intendedHeaders in args[3].headers:
            self.container_rid = args[3].headers[self.intendedHeaders]
        self.client = client
        self.exception = None

    def ShouldRetry(self, exception):
        """Returns true if the request should retry based on the passed-in exception.

        :param (exceptions.CosmosHttpResponseError instance) exception:
        :returns: a boolean stating whether the request should be retried
        :rtype: bool

        """

        self.exception = exception  # needed for pylint
        if self.refresh_container_properties_cache:
            # refresh routing_map_provider to refresh partition key range cache
            # make refresh_partition_key_range_cache False to skip this check on subsequent Gone exceptions
            if not hasattr(self, 'container_rid'):
                return False
            container_caches = self.client._container_properties_cache
            container_link: Optional[str] = self.__find_container_link_with_RID(container_caches, self.container_rid)
            if not container_link:
                return False
            self.client._refresh_container_properties_cache(container_link)
            if self.container_rid == self.client._container_properties_cache[container_link]["_rid"]:
                return False
            self.container_rid = self.client._container_properties_cache[container_link]["_rid"]
            self.refresh_container_properties_cache = False
            return True
        # return False to raise error to multi_execution_aggregator and repair document producer context
        return False

    async def ShouldRetryAsync(self, exception):
        """Returns true if the request should retry based on the passed-in exception.

        :param (exceptions.CosmosHttpResponseError instance) exception:
        :returns: a boolean stating whether the request should be retried
        :rtype: bool

        """

        self.exception = exception  # needed for pylint
        if self.refresh_container_properties_cache:
            # refresh routing_map_provider to refresh partition key range cache
            # make refresh_partition_key_range_cache False to skip this check on subsequent Gone exceptions
            if not hasattr(self, 'container_rid'):
                return False
            container_caches = self.client._container_properties_cache
            container_link: Optional[str] = self.__find_container_link_with_RID(container_caches, self.container_rid)
            if not container_link:
                return False
            # async client needs to await to refresh cache
            await self.client._refresh_container_properties_cache(container_link)
            if self.container_rid == self.client._container_properties_cache[container_link]["_rid"]:
                return False
            self.container_rid = self.client._container_properties_cache[container_link]["_rid"]
            self.refresh_container_properties_cache = False
            return True
        # return False to raise error to multi_execution_aggregator and repair document producer context
        return False

    def __find_container_link_with_RID(self, container_properties_caches: Optional[Dict[str, Any]], rid: str) -> Optional[str]:  # pylint: disable=line-too-long
        if container_properties_caches:
            for key, inner_dict in container_properties_caches.items():
                is_match = next((k for k, v in inner_dict.items() if v == rid), None)
                if is_match:
                    return key
        return None

    def __check_if_rid_different(self, container_link: str, container_properties_caches: Optional[Dict[str, Any]], rid: str):
        return container_properties_caches[container_link]["_rid"] == rid