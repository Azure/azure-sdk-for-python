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
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Callable, Tuple, cast

from azure.cosmos import _retry_utility, http_constants, exceptions
from azure.cosmos._change_feed.change_feed_start_from import ChangeFeedStartFromType
from azure.cosmos._change_feed.change_feed_state import ChangeFeedStateV1, ChangeFeedStateV2, ChangeFeedStateVersion
from azure.cosmos.exceptions import CosmosHttpResponseError

# pylint: disable=protected-access

class ChangeFeedFetcher(ABC):

    @abstractmethod
    def fetch_next_block(self):
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
            feed_options: Dict[str, Any],
            fetch_function: Callable[[Dict[str, Any]], Tuple[List[Dict[str, Any]], Dict[str, Any]]]
    ) -> None:

        self._client = client
        self._feed_options = feed_options

        self._change_feed_state: ChangeFeedStateV1 = self._feed_options.pop("changeFeedState")
        if self._change_feed_state.version != ChangeFeedStateVersion.V1:
            raise ValueError(f"ChangeFeedFetcherV1 can not handle change feed state version"
                             f" {type(self._change_feed_state)}")

        self._resource_link = resource_link
        self._fetch_function = fetch_function

    def fetch_next_block(self) -> List[Dict[str, Any]]:
        """Returns a block of results.

        :return: List of results.
        :rtype: list
        """
        def callback():
            return self.fetch_change_feed_items()

        return _retry_utility.Execute(self._client, self._client._global_endpoint_manager, callback)

    def fetch_change_feed_items(self) -> List[Dict[str, Any]]:
        self._feed_options["changeFeedState"] = self._change_feed_state

        self._change_feed_state.populate_feed_options(self._feed_options)
        is_s_time_first_fetch = self._change_feed_state._continuation is None
        while True:
            (fetched_items, response_headers) = self._fetch_function(self._feed_options)
            continuation_key = http_constants.HttpHeaders.ETag
            # In change feed queries, the continuation token is always populated. The hasNext() test is whether
            # there is any items in the response or not.
            self._change_feed_state.apply_server_response_continuation(
                cast(str, response_headers.get(continuation_key)),
                bool(fetched_items))

            if fetched_items:
                break

            # When processing from point in time, there will be no initial results being returned,
            # so we will retry with the new continuation token again
            if (self._change_feed_state._change_feed_start_from.version == ChangeFeedStartFromType.POINT_IN_TIME
                    and is_s_time_first_fetch):
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
            feed_options: Dict[str, Any],
            fetch_function: Callable[[Dict[str, Any]], Tuple[List[Dict[str, Any]], Dict[str, Any]]]):

        self._client = client
        self._feed_options = feed_options

        self._change_feed_state: ChangeFeedStateV2 = self._feed_options.pop("changeFeedState")
        if self._change_feed_state.version != ChangeFeedStateVersion.V2:
            raise ValueError(f"ChangeFeedFetcherV2 can not handle change feed state version "
                             f"{type(self._change_feed_state)}")

        self._resource_link = resource_link
        self._fetch_function = fetch_function

    def fetch_next_block(self) -> List[Dict[str, Any]]:
        """Returns a block of results.

        :return: List of results.
        :rtype: list
        """

        def callback():
            return self.fetch_change_feed_items()

        try:
            return _retry_utility.Execute(self._client, self._client._global_endpoint_manager, callback)
        except CosmosHttpResponseError as e:
            if exceptions._partition_range_is_gone(e) or exceptions._is_partition_split_or_merge(e):
                # refresh change feed state
                self._change_feed_state.handle_feed_range_gone(self._client._routing_map_provider, self._resource_link)
            else:
                raise e

        return self.fetch_next_block()

    def fetch_change_feed_items(self) -> List[Dict[str, Any]]:
        self._feed_options["changeFeedState"] = self._change_feed_state

        self._change_feed_state.populate_feed_options(self._feed_options)

        is_s_time_first_fetch = self._change_feed_state._continuation.current_token.token is None
        while True:
            (fetched_items, response_headers) = self._fetch_function(self._feed_options)

            continuation_key = http_constants.HttpHeaders.ETag
            # In change feed queries, the continuation token is always populated.
            self._change_feed_state.apply_server_response_continuation(
                cast(str, response_headers.get(continuation_key)),
                bool(fetched_items))

            if fetched_items:
                self._change_feed_state._continuation._move_to_next_token()
                response_headers[continuation_key] = self._get_base64_encoded_continuation()
                break

            # when there is no items being returned, we will decide to retry based on:
            # 1. When processing from point in time, there will be no initial results being returned,
            # so we will retry with the new continuation token
            # 2. if the feed range of the changeFeedState span multiple physical partitions
            # then we will read from the next feed range until we have looped through all physical partitions
            if (self._change_feed_state._change_feed_start_from.version == ChangeFeedStartFromType.POINT_IN_TIME
                    and is_s_time_first_fetch):
                response_headers[continuation_key] = self._get_base64_encoded_continuation()
                is_s_time_first_fetch = False
                should_retry = True
            else:
                self._change_feed_state._continuation._move_to_next_token()
                response_headers[continuation_key] = self._get_base64_encoded_continuation()
                should_retry = self._change_feed_state.should_retry_on_not_modified_response()
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
