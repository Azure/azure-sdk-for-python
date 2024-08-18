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

"""Internal class for change feed state implementation in the Azure Cosmos
database service.
"""

import base64
import collections
import json
from abc import ABC, abstractmethod
from typing import Optional, Union, List, Any

from azure.cosmos import http_constants
from azure.cosmos._change_feed.aio.change_feed_start_from import ChangeFeedStartFromETagAndFeedRange, \
    ChangeFeedStartFromInternal
from azure.cosmos._change_feed.aio.composite_continuation_token import CompositeContinuationToken
from azure.cosmos._change_feed.aio.feed_range_composite_continuation_token import FeedRangeCompositeContinuation
from azure.cosmos._change_feed.feed_range import FeedRangeEpk, FeedRangePartitionKey, FeedRange
from azure.cosmos._routing.aio.routing_map_provider import SmartRoutingMapProvider
from azure.cosmos._routing.routing_range import Range
from azure.cosmos._utils import is_key_exists_and_not_none
from azure.cosmos.exceptions import CosmosFeedRangeGoneError
from azure.cosmos.partition_key import _Empty, _Undefined


class ChangeFeedState(ABC):
    version_property_name = "v"

    @abstractmethod
    def populate_feed_options(self, feed_options: dict[str, any]) -> None:
        pass

    @abstractmethod
    async def populate_request_headers(
            self,
            routing_provider: SmartRoutingMapProvider,
            request_headers: dict[str, any]) -> None:
        pass

    @abstractmethod
    def apply_server_response_continuation(self, continuation: str) -> None:
        pass

    @staticmethod
    def from_json(
            container_link: str,
            container_rid: str,
            data: dict[str, Any]):
        if is_key_exists_and_not_none(data, "partitionKeyRangeId") or is_key_exists_and_not_none(data, "continuationPkRangeId"):
            return ChangeFeedStateV1.from_json(container_link, container_rid, data)
        else:
            if is_key_exists_and_not_none(data, "continuationFeedRange"):
                # get changeFeedState from continuation
                continuation_json_str = base64.b64decode(data["continuationFeedRange"]).decode('utf-8')
                continuation_json = json.loads(continuation_json_str)
                version = continuation_json.get(ChangeFeedState.version_property_name)
                if version is None:
                    raise ValueError("Invalid base64 encoded continuation string [Missing version]")
                elif version == "V2":
                    return ChangeFeedStateV2.from_continuation(container_link, container_rid, continuation_json)
                else:
                    raise ValueError("Invalid base64 encoded continuation string [Invalid version]")
            # when there is no continuation token, by default construct ChangeFeedStateV2
            return ChangeFeedStateV2.from_initial_state(container_link, container_rid, data)

class ChangeFeedStateV1(ChangeFeedState):
    """Change feed state v1 implementation. This is used when partition key range id is used or the continuation is just simple _etag
    """

    def __init__(
            self,
            container_link: str,
            container_rid: str,
            change_feed_start_from: ChangeFeedStartFromInternal,
            partition_key_range_id: Optional[str] = None,
            partition_key: Optional[Union[str, int, float, bool, List[Union[str, int, float, bool]], _Empty, _Undefined]] = None,
            continuation: Optional[str] = None):

        self._container_link = container_link
        self._container_rid = container_rid
        self._change_feed_start_from = change_feed_start_from
        self._partition_key_range_id = partition_key_range_id
        self._partition_key = partition_key
        self._continuation = continuation

    @property
    def container_rid(self):
        return self._container_rid

    @classmethod
    def from_json(cls, container_link: str, container_rid: str, data: dict[str, Any]) -> 'ChangeFeedStateV1':
        return cls(
            container_link,
            container_rid,
            ChangeFeedStartFromInternal.from_start_time(data.get("startTime")),
            data.get("partitionKeyRangeId"),
            data.get("partitionKey"),
            data.get("continuationPkRangeId")
        )

    async def populate_request_headers(
            self,
            routing_provider: SmartRoutingMapProvider,
            headers: dict[str, Any]) -> None:
        headers[http_constants.HttpHeaders.AIM] = http_constants.HttpHeaders.IncrementalFeedHeaderValue

        # When a merge happens, the child partition will contain documents ordered by LSN but the _ts/creation time
        # of the documents may not be sequential. So when reading the changeFeed by LSN, it is possible to encounter documents with lower _ts.
        # In order to guarantee we always get the documents after customer's point start time, we will need to always pass the start time in the header.
        self._change_feed_start_from.populate_request_headers(headers)
        if self._continuation:
            headers[http_constants.HttpHeaders.IfNoneMatch] = self._continuation

    def populate_feed_options(self, feed_options: dict[str, any]) -> None:
        if self._partition_key_range_id is not None:
            feed_options["partitionKeyRangeId"] = self._partition_key_range_id
        if self._partition_key is not None:
            feed_options["partitionKey"] = self._partition_key

    def apply_server_response_continuation(self, continuation: str) -> None:
        self._continuation = continuation

class ChangeFeedStateV2(ChangeFeedState):
    container_rid_property_name = "containerRid"
    change_feed_mode_property_name = "mode"
    change_feed_start_from_property_name = "startFrom"
    continuation_property_name = "continuation"

    # TODO: adding change feed mode
    def __init__(
            self,
            container_link: str,
            container_rid: str,
            feed_range: FeedRange,
            change_feed_start_from: ChangeFeedStartFromInternal,
            continuation: Optional[FeedRangeCompositeContinuation] = None):

        self._container_link = container_link
        self._container_rid = container_rid
        self._feed_range = feed_range
        self._change_feed_start_from = change_feed_start_from
        self._continuation = continuation
        if self._continuation is None:
            composite_continuation_token_queue = collections.deque()
            composite_continuation_token_queue.append(
                CompositeContinuationToken(
                    self._feed_range.get_normalized_range(),
                    None))
            self._continuation =\
                FeedRangeCompositeContinuation(self._container_rid, self._feed_range, composite_continuation_token_queue)

    @property
    def container_rid(self) -> str :
        return self._container_rid

    def to_dict(self) -> dict[str, Any]:
        return {
            self.version_property_name: "V2",
            self.container_rid_property_name: self._container_rid,
            self.change_feed_mode_property_name: "Incremental",
            self.change_feed_start_from_property_name: self._change_feed_start_from.to_dict(),
            self.continuation_property_name: self._continuation.to_dict()
        }

    async def populate_request_headers(
            self,
            routing_provider: SmartRoutingMapProvider,
            headers: dict[str, any]) -> None:
        headers[http_constants.HttpHeaders.AIM] = http_constants.HttpHeaders.IncrementalFeedHeaderValue

        # When a merge happens, the child partition will contain documents ordered by LSN but the _ts/creation time
        # of the documents may not be sequential. So when reading the changeFeed by LSN, it is possible to encounter documents with lower _ts.
        # In order to guarantee we always get the documents after customer's point start time, we will need to always pass the start time in the header.
        self._change_feed_start_from.populate_request_headers(headers)

        if self._continuation.current_token is not None and self._continuation.current_token.token is not None:
            change_feed_start_from_feed_range_and_etag =\
                ChangeFeedStartFromETagAndFeedRange(self._continuation.current_token.token, self._continuation.current_token.feed_range)
            change_feed_start_from_feed_range_and_etag.populate_request_headers(headers)

        # based on the feed range to find the overlapping partition key range id
        over_lapping_ranges =\
            await routing_provider.get_overlapping_ranges(
                self._container_link,
                [self._continuation.current_token.feed_range])

        if len(over_lapping_ranges) > 1:
            raise CosmosFeedRangeGoneError(message=
                                           f"Range {self._continuation.current_token.feed_range}"
                                           f" spans {len(over_lapping_ranges)}"
                                           f" physical partitions: {[child_range['id'] for child_range in over_lapping_ranges]}")
        else:
            overlapping_feed_range = Range.PartitionKeyRangeToRange(over_lapping_ranges[0])
            if overlapping_feed_range == self._continuation.current_token.feed_range:
                # exactly mapping to one physical partition, only need to set the partitionKeyRangeId
                headers[http_constants.HttpHeaders.PartitionKeyRangeID] = over_lapping_ranges[0]["id"]
            else:
                # the current token feed range spans less than single physical partition
                # for this case, need to set both the partition key range id and epk filter headers
                headers[http_constants.HttpHeaders.PartitionKeyRangeID] = over_lapping_ranges[0]["id"]
                headers[http_constants.HttpHeaders.StartEpkString] = self._continuation.current_token.feed_range.min
                headers[http_constants.HttpHeaders.EndEpkString] = self._continuation.current_token.feed_range.max

    def populate_feed_options(self, feed_options: dict[str, any]) -> None:
        pass

    async def handle_feed_range_gone(self, routing_provider: SmartRoutingMapProvider, resource_link: str) -> None:
        await self._continuation.handle_feed_range_gone(routing_provider, resource_link)

    def apply_server_response_continuation(self, continuation: str) -> None:
        self._continuation.apply_server_response_continuation(continuation)

    def should_retry_on_not_modified_response(self):
        self._continuation.should_retry_on_not_modified_response()

    def apply_not_modified_response(self) -> None:
        self._continuation.apply_not_modified_response()

    @classmethod
    def from_continuation(
            cls,
            container_link: str,
            container_rid: str,
            continuation_json: dict[str, Any]) -> 'ChangeFeedStateV2':

        container_rid_from_continuation = continuation_json.get(ChangeFeedStateV2.container_rid_property_name)
        if container_rid_from_continuation is None:
            raise ValueError(f"Invalid continuation: [Missing {ChangeFeedStateV2.container_rid_property_name}]")
        elif container_rid_from_continuation != container_rid:
            raise ValueError("Invalid continuation: [Mismatch collection rid]")

        change_feed_start_from_data = continuation_json.get(ChangeFeedStateV2.change_feed_start_from_property_name)
        if change_feed_start_from_data is None:
            raise ValueError(f"Invalid continuation: [Missing {ChangeFeedStateV2.change_feed_start_from_property_name}]")
        change_feed_start_from = ChangeFeedStartFromInternal.from_json(change_feed_start_from_data)

        continuation_data = continuation_json.get(ChangeFeedStateV2.continuation_property_name)
        if continuation_data is None:
            raise ValueError(f"Invalid continuation: [Missing {ChangeFeedStateV2.continuation_property_name}]")
        continuation = FeedRangeCompositeContinuation.from_json(continuation_data)
        return ChangeFeedStateV2(
            container_link=container_link,
            container_rid=container_rid,
            feed_range=continuation._feed_range,
            change_feed_start_from=change_feed_start_from,
            continuation=continuation)

    @classmethod
    def from_initial_state(
            cls,
            container_link: str,
            collection_rid: str,
            data: dict[str, Any]) -> 'ChangeFeedStateV2':

        if is_key_exists_and_not_none(data, "feedRange"):
            feed_range_str = base64.b64decode(data["feedRange"]).decode('utf-8')
            feed_range_json = json.loads(feed_range_str)
            feed_range = FeedRangeEpk(Range.ParseFromDict(feed_range_json))
        elif is_key_exists_and_not_none(data, "partitionKey"):
            if is_key_exists_and_not_none(data, "partitionKeyFeedRange"):
                feed_range = FeedRangePartitionKey(data["partitionKey"], data["partitionKeyFeedRange"])
            else:
                raise ValueError("partitionKey is in the changeFeedStateContext, but missing partitionKeyFeedRange")
        else:
            # default to full range
            feed_range = FeedRangeEpk(
                Range(
                    "",
                    "FF",
                    True,
                    False))

        change_feed_start_from = ChangeFeedStartFromInternal.from_start_time(data.get("startTime"))
        return cls(
            container_link=container_link,
            container_rid=collection_rid,
            feed_range=feed_range,
            change_feed_start_from=change_feed_start_from,
            continuation=None)

