# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

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

"""Internal class for processing change feed implementation in the Azure Cosmos
database service.
"""
import base64
import copy
import json
from abc import ABC, abstractmethod

from azure.cosmos import http_constants, exceptions
from azure.cosmos._change_feed.aio.change_feed_state import ChangeFeedStateV1, ChangeFeedStateV2
from azure.cosmos.aio import _retry_utility_async
from azure.cosmos.exceptions import CosmosHttpResponseError


class ChangeFeedFetcher(ABC):

    @abstractmethod
    async def fetch_next_block(self):
        pass

class ChangeFeedFetcherV1(ChangeFeedFetcher):
    """Internal class for change feed fetch v1 implementation.
     This is used when partition key range id is used or when the supplied continuation token is in just simple etag.
     Please note v1 does not support split or merge.

    """
    def __init__(
            self,
            client,
            resource_link: str,
            feed_options: dict[str, any],
            fetch_function):

        self._client = client
        self._feed_options = feed_options

        self._change_feed_state = self._feed_options.pop("changeFeedState")
        if not isinstance(self._change_feed_state, ChangeFeedStateV1):
            raise ValueError(f"ChangeFeedFetcherV1 can not handle change feed state version {type(self._change_feed_state)}")
        self._change_feed_state.__class__ = ChangeFeedStateV1

        self._resource_link = resource_link
        self._fetch_function = fetch_function

    async def fetch_next_block(self):
        """Returns a block of results.

        :return: List of results.
        :rtype: list
        """
        async def callback():
            return await self.fetch_change_feed_items(self._fetch_function)

        return await _retry_utility_async.ExecuteAsync(self._client, self._client._global_endpoint_manager, callback)

    async def fetch_change_feed_items(self, fetch_function) -> list[dict[str, any]]:
        new_options = copy.deepcopy(self._feed_options)
        new_options["changeFeedState"] = self._change_feed_state

        self._change_feed_state.populate_feed_options(new_options)
        is_s_time_first_fetch = True
        while True:
            (fetched_items, response_headers) = await fetch_function(new_options)
            continuation_key = http_constants.HttpHeaders.ETag
            # In change feed queries, the continuation token is always populated. The hasNext() test is whether
            # there is any items in the response or not.
            # For start time however we get no initial results, so we need to pass continuation token? Is this true?
            self._change_feed_state.apply_server_response_continuation(
                response_headers.get(continuation_key))

            if fetched_items:
                break
            elif is_s_time_first_fetch:
                is_s_time_first_fetch = False
            else:
                break
        return fetched_items


class ChangeFeedFetcherV2(object):
    """Internal class for change feed fetch v2 implementation.
    """

    def __init__(
            self,
            client,
            resource_link: str,
            feed_options: dict[str, any],
            fetch_function):

        self._client = client
        self._feed_options = feed_options

        self._change_feed_state = self._feed_options.pop("changeFeedState")
        if not isinstance(self._change_feed_state, ChangeFeedStateV2):
            raise ValueError(f"ChangeFeedFetcherV2 can not handle change feed state version {type(self._change_feed_state)}")
        self._change_feed_state.__class__ = ChangeFeedStateV2

        self._resource_link = resource_link
        self._fetch_function = fetch_function

    async def fetch_next_block(self):
        """Returns a block of results.

        :return: List of results.
        :rtype: list
        """

        async def callback():
            return await self.fetch_change_feed_items(self._fetch_function)

        try:
            return await _retry_utility_async.ExecuteAsync(self._client, self._client._global_endpoint_manager, callback)
        except CosmosHttpResponseError as e:
            if exceptions._partition_range_is_gone(e) or exceptions._is_partition_split_or_merge(e):
                # refresh change feed state
                await self._change_feed_state.handle_feed_range_gone(self._client._routing_map_provider, self._resource_link)
            else:
                raise e

        return await self.fetch_next_block()

    async def fetch_change_feed_items(self, fetch_function) -> list[dict[str, any]]:
        new_options = copy.deepcopy(self._feed_options)
        new_options["changeFeedState"] = self._change_feed_state

        self._change_feed_state.populate_feed_options(new_options)

        is_s_time_first_fetch = True
        while True:
            (fetched_items, response_headers) = await fetch_function(new_options)

            continuation_key = http_constants.HttpHeaders.ETag
            # In change feed queries, the continuation token is always populated. The hasNext() test is whether
            # there is any items in the response or not.
            # For start time however we get no initial results, so we need to pass continuation token? Is this true?
            if fetched_items:
                self._change_feed_state.apply_server_response_continuation(
                    response_headers.get(continuation_key))
                response_headers[continuation_key] = self._get_base64_encoded_continuation()
                break
            else:
                self._change_feed_state.apply_not_modified_response()
                self._change_feed_state.apply_server_response_continuation(
                    response_headers.get(continuation_key))
                response_headers[continuation_key] = self._get_base64_encoded_continuation()
                should_retry = self._change_feed_state.should_retry_on_not_modified_response() or is_s_time_first_fetch
                is_s_time_first_fetch = False
                if not should_retry:
                    break

        return fetched_items

    def _get_base64_encoded_continuation(self) -> str:
        continuation_json = json.dumps(self._change_feed_state.to_dict())
        json_bytes = continuation_json.encode('utf-8')
        # Encode the bytes to a Base64 string
        base64_bytes = base64.b64encode(json_bytes)
        # Convert the Base64 bytes to a string
        return base64_bytes.decode('utf-8')

