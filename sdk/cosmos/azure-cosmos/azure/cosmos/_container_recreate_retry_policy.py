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
import ast
import json

from typing import Optional, Dict, Any, List
from . import http_constants
from .partition_key import _Empty, _Undefined


# pylint: disable=protected-access


class ContainerRecreateRetryPolicy:
    def __init__(self, client: Optional[Any], container_caches: Optional[Dict[str, Dict[str, Any]]]
                 , *args: Optional[List]):
        self.retry_after_in_milliseconds = 0  # Same as in .net
        self.refresh_container_properties_cache = True
        self._intended_headers = http_constants.HttpHeaders.IntendedCollectionRID
        self.container_rid = None
        self.container_link = None
        self.link = None
        self._http_request = args[3] if len(args) >= 4 else None
        self._headers = self._http_request.headers if self._http_request else None
        if self._headers and self._intended_headers in self._headers:
            self.container_rid = self._headers[self._intended_headers]
            if container_caches:
                self.container_link = self.__find_container_link_with_rid(container_caches, self.container_rid)
        self.client = client
        self.exception = None

    def ShouldRetry(self, exception: Optional[Any]) -> bool:
        """Returns true if the request should retry based on the passed-in exception.

        :param (exceptions.CosmosHttpResponseError instance) exception:
        :returns: a boolean stating whether the request should be retried
        :rtype: bool

        """

        self.exception = exception  # needed for pylint
        if self.refresh_container_properties_cache:
            if not self.container_rid or not self.container_link:
                return False
            self.refresh_container_properties_cache = False
            return True
        return False

    def __find_container_link_with_rid(self, container_properties_caches: Optional[Dict[str, Any]], rid: str) -> \
            Optional[str]:
        if container_properties_caches:
            for key, inner_dict in container_properties_caches.items():
                is_match = next((k for k, v in inner_dict.items() if v == rid), None)
                if is_match:
                    return key
        return None

    def check_if_rid_different(self, container_link: str,
                               container_properties_caches: Optional[Dict[str, Any]], rid: str) -> bool:
        if container_properties_caches:
            return container_properties_caches[container_link]["_rid"] == rid
        return not rid

    def should_extract_partition_key(self, headers: Dict[str, Any], container_cache: Optional[Dict[str, Any]]) -> bool:
        if headers and http_constants.HttpHeaders.PartitionKey in headers:
            current_partition_key = headers[http_constants.HttpHeaders.PartitionKey]
            partition_key_definition = container_cache["partitionKey"] if container_cache else None
            if partition_key_definition and partition_key_definition["kind"] == "MultiHash":
                # A null in the multihash partition key indicates a failure in extracting partition keys
                # from the document definition
                return 'null' in current_partition_key
            else:
                # These values indicate the partition key was not successfully extracted from the document definition
                return current_partition_key == '[{}]' or current_partition_key == '[]'
        return False

    def _extract_partition_key(self, client: Optional[Any], container_cache: Optional[Dict[str, Any]], body: str)\
            -> str:
        partition_key_definition = container_cache["partitionKey"] if container_cache else None
        body_dict = self.__str_to_dict(body)
        new_partition_key = _Undefined
        if body_dict:
            options = client._AddPartitionKey(self.container_link, body_dict, {}) if client else []
            # if partitionKey value is Undefined, serialize it as [{}] to be consistent with other SDKs.
            if options and isinstance(options["partitionKey"], _Undefined):
                new_partition_key = [{}]
            # If partitionKey value is Empty, serialize it as [], which is the equivalent sent for migrated collections
            elif options and isinstance(options["partitionKey"], _Empty):
                new_partition_key = []
            # else serialize using json dumps method which apart from regular values will serialize None into null
            elif partition_key_definition and partition_key_definition["kind"] == "MultiHash":
                new_partition_key = json.dumps(options["partitionKey"], separators=(',', ':'))
            else:
                new_partition_key = json.dumps([options["partitionKey"]])
        return new_partition_key

    async def _extract_partition_key_async(self, client: Optional[Any], container_cache: Optional[Dict[str, Any]], body: str)\
            -> str:
        partition_key_definition = container_cache["partitionKey"]
        body_dict = self.__str_to_dict(body)
        new_partition_key = _Undefined
        if body_dict:
            options = await client._AddPartitionKey(self.container_link, body_dict, {})
            # if partitionKey value is Undefined, serialize it as [{}] to be consistent with other SDKs.
            if isinstance(options["partitionKey"], _Undefined):
                new_partition_key = [{}]
            # If partitionKey value is Empty, serialize it as [], which is the equivalent sent for migrated collections
            elif isinstance(options["partitionKey"], _Empty):
                new_partition_key = []
            # else serialize using json dumps method which apart from regular values will serialize None into null
            elif partition_key_definition["kind"] == "MultiHash":
                new_partition_key = json.dumps(options["partitionKey"], separators=(',', ':'))
            else:
                new_partition_key = json.dumps([options["partitionKey"]])
        return new_partition_key

    def should_update_throughput_link(self, body: Optional[str], cached_container: Optional[Dict[str, Any]]) -> bool:
        body_dict = self.__str_to_dict(body)
        if not body_dict:
            return False
        try:
            # If this is a request to get throughput properties then we will update the link
            if body_dict["query"] == "SELECT * FROM root r WHERE r.resource=@link":
                self.link = cached_container["_self"]
                return True
        except (TypeError, IndexError, KeyError):
            return False
        return False

    def _update_throughput_link(self, body: Optional[str]) -> str:
        body_dict = self.__str_to_dict(body)
        if not body_dict:
            return body
        body_dict["parameters"][0]["value"] = self.link
        return json.dumps(body_dict, separators=(',', ':'))


    def __str_to_dict(self, dict_string: str) -> Dict[str, str]:
        try:
            # Use ast.literal_eval() to convert string to dictionary
            dict_obj = ast.literal_eval(dict_string)
            return dict_obj
        except (SyntaxError, ValueError):
            return {}
