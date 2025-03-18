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
from enum import Enum
from typing import Optional, Union, List, Any, Dict, Deque
import logging
from typing_extensions import Literal

from azure.cosmos import http_constants
from azure.cosmos._change_feed.change_feed_start_from import ChangeFeedStartFromInternal, \
    ChangeFeedStartFromETagAndFeedRange
from azure.cosmos._change_feed.composite_continuation_token import CompositeContinuationToken
from azure.cosmos._change_feed.feed_range_internal import (FeedRangeInternal, FeedRangeInternalEpk,
                                                           FeedRangeInternalPartitionKey)
from azure.cosmos._change_feed.feed_range_composite_continuation_token import FeedRangeCompositeContinuation
from azure.cosmos._routing.aio.routing_map_provider import SmartRoutingMapProvider as AsyncSmartRoutingMapProvider
from azure.cosmos._routing.routing_map_provider import SmartRoutingMapProvider
from azure.cosmos._routing.routing_range import Range
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.http_constants import StatusCodes, SubStatusCodes
from azure.cosmos.partition_key import _Empty, _Undefined

class ChangeFeedStateVersion(Enum):
    V1 = "v1"
    V2 = "v2"

class ChangeFeedState(ABC):
    version_property_name = "v"

    def __init__(self, version: ChangeFeedStateVersion) -> None:
        self.version = version

    @abstractmethod
    def populate_feed_options(self, feed_options: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def populate_request_headers(
            self,
            routing_provider: SmartRoutingMapProvider,
            request_headers: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def populate_request_headers_async(
            self,
            async_routing_provider: AsyncSmartRoutingMapProvider,
            request_headers: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def apply_server_response_continuation(self, continuation: str, has_modified_response: bool) -> None:
        pass

    @staticmethod
    def from_json(
            container_link: str,
            container_rid: str,
            change_feed_state_context: Dict[str, Any]) -> 'ChangeFeedState':

        if (change_feed_state_context.get("partitionKeyRangeId")
                or change_feed_state_context.get("continuationPkRangeId")):
            return ChangeFeedStateV1.from_json(container_link, container_rid, change_feed_state_context)

        if change_feed_state_context.get("continuationFeedRange"):
            # get changeFeedState from continuation
            continuation_json_str = base64.b64decode(change_feed_state_context["continuationFeedRange"]).decode(
                'utf-8')
            continuation_json = json.loads(continuation_json_str)
            version = continuation_json.get(ChangeFeedState.version_property_name)
            if version is None:
                raise ValueError("Invalid base64 encoded continuation string [Missing version]")

            if version == ChangeFeedStateVersion.V2.value:
                return ChangeFeedStateV2.from_continuation(container_link, container_rid, continuation_json)

            raise ValueError("Invalid base64 encoded continuation string [Invalid version]")

        # when there is no continuation token, by default construct ChangeFeedStateV2
        return ChangeFeedStateV2.from_initial_state(container_link, container_rid, change_feed_state_context)

class ChangeFeedStateV1(ChangeFeedState):
    """Change feed state v1 implementation.
     This is used when partition key range id is used or the continuation is just simple _etag
    """

    def __init__(
            self,
            container_link: str,
            container_rid: str,
            change_feed_start_from: ChangeFeedStartFromInternal,
            partition_key_range_id: Optional[str] = None,
            partition_key: Optional[Union[str, int, float, bool, List[Union[str, int, float, bool]], _Empty, _Undefined]] = None, # pylint: disable=line-too-long
            continuation: Optional[str] = None) -> None:

        self._container_link = container_link
        self._container_rid = container_rid
        self._change_feed_start_from = change_feed_start_from
        self._partition_key_range_id = partition_key_range_id
        self._partition_key = partition_key
        self._continuation = continuation
        super(ChangeFeedStateV1, self).__init__(ChangeFeedStateVersion.V1)

    @property
    def container_rid(self):
        return self._container_rid

    @classmethod
    def from_json(
            cls,
            container_link: str,
            container_rid: str,
            change_feed_state_context: Dict[str, Any]) -> 'ChangeFeedStateV1':
        return cls(
            container_link,
            container_rid,
            ChangeFeedStartFromInternal.from_start_time(change_feed_state_context.get("startTime")),
            change_feed_state_context.get("partitionKeyRangeId"),
            change_feed_state_context.get("partitionKey"),
            change_feed_state_context.get("continuationPkRangeId")
        )

    def populate_request_headers(
            self,
            routing_provider: SmartRoutingMapProvider,
            request_headers: Dict[str, Any]) -> None:
        request_headers[http_constants.HttpHeaders.AIM] = http_constants.HttpHeaders.IncrementalFeedHeaderValue

        self._change_feed_start_from.populate_request_headers(request_headers)
        if self._continuation:
            request_headers[http_constants.HttpHeaders.IfNoneMatch] = self._continuation

    async def populate_request_headers_async(
            self,
            async_routing_provider: AsyncSmartRoutingMapProvider,
            request_headers: Dict[str, Any]) -> None: # pylint: disable=unused-argument

        request_headers[http_constants.HttpHeaders.AIM] = http_constants.HttpHeaders.IncrementalFeedHeaderValue

        self._change_feed_start_from.populate_request_headers(request_headers)
        if self._continuation:
            request_headers[http_constants.HttpHeaders.IfNoneMatch] = self._continuation

    def populate_feed_options(self, feed_options: Dict[str, Any]) -> None:
        if self._partition_key_range_id is not None:
            feed_options["partitionKeyRangeId"] = self._partition_key_range_id
        if self._partition_key is not None:
            feed_options["partitionKey"] = self._partition_key

    def apply_server_response_continuation(self, continuation: str, has_modified_response) -> None:
        self._continuation = continuation

class ChangeFeedStateV2(ChangeFeedState):
    container_rid_property_name = "containerRid"
    mode_property_name = "mode"
    change_feed_start_from_property_name = "startFrom"
    continuation_property_name = "continuation"

    def __init__(
            self,
            container_link: str,
            container_rid: str,
            feed_range: FeedRangeInternal,
            change_feed_start_from: ChangeFeedStartFromInternal,
            continuation: Optional[FeedRangeCompositeContinuation],
            mode: Optional[Literal["LatestVersion", "AllVersionsAndDeletes"]]
    ) -> None:

        self._container_link = container_link
        self._container_rid = container_rid
        self._feed_range = feed_range
        self._change_feed_start_from = change_feed_start_from
        if continuation is None:
            composite_continuation_token_queue: Deque = collections.deque()
            composite_continuation_token_queue.append(
                CompositeContinuationToken(
                    self._feed_range.get_normalized_range(),
                    None))
            self._continuation =\
                FeedRangeCompositeContinuation(
                    self._container_rid,
                    self._feed_range,
                    composite_continuation_token_queue)
        else:
            self._continuation = continuation

        self._mode = "LatestVersion" if mode is None else mode

        super(ChangeFeedStateV2, self).__init__(ChangeFeedStateVersion.V2)

    @property
    def container_rid(self) -> str :
        return self._container_rid

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.version_property_name: ChangeFeedStateVersion.V2.value,
            self.container_rid_property_name: self._container_rid,
            self.mode_property_name: self._mode,
            self.change_feed_start_from_property_name: self._change_feed_start_from.to_dict(),
            self.continuation_property_name: self._continuation.to_dict() if self._continuation is not None else None
        }

    def set_start_from_request_headers(
            self,
            request_headers: Dict[str, Any]) -> None:
        # When a merge happens, the child partition will contain documents ordered by LSN but the _ts/creation time
        # of the documents may not be sequential.
        # So when reading the changeFeed by LSN, it is possible to encounter documents with lower _ts.
        # In order to guarantee we always get the documents after customer's point start time,
        # we will need to always pass the start time in the header.
        self._change_feed_start_from.populate_request_headers(request_headers)

        if self._continuation.current_token is not None and self._continuation.current_token.token is not None:
            change_feed_start_from_feed_range_and_etag =\
                ChangeFeedStartFromETagAndFeedRange(
                    self._continuation.current_token.token,
                    self._continuation.current_token.feed_range)
            change_feed_start_from_feed_range_and_etag.populate_request_headers(request_headers)

    def set_pk_range_id_request_headers(
            self,
            over_lapping_ranges,
            request_headers: Dict[str, Any]) -> None:

        if len(over_lapping_ranges) > 1:
            raise self.get_feed_range_gone_error(over_lapping_ranges)

        overlapping_feed_range = Range.PartitionKeyRangeToRange(over_lapping_ranges[0])
        if overlapping_feed_range == self._continuation.current_token.feed_range:
            # exactly mapping to one physical partition, only need to set the partitionKeyRangeId
            request_headers[http_constants.HttpHeaders.PartitionKeyRangeID] = over_lapping_ranges[0]["id"]
        else:
            # the current token feed range spans less than single physical partition
            # for this case, need to set both the partition key range id and epk filter headers
            request_headers[http_constants.HttpHeaders.PartitionKeyRangeID] = over_lapping_ranges[0]["id"]
            request_headers[http_constants.HttpHeaders.ReadFeedKeyType] = "EffectivePartitionKeyRange"
            request_headers[http_constants.HttpHeaders.StartEpkString] = self._continuation.current_token.feed_range.min
            request_headers[http_constants.HttpHeaders.EndEpkString] = self._continuation.current_token.feed_range.max

    def set_mode_request_headers(
            self,
            request_headers: Dict[str, Any]) -> None:
        if self._mode == "AllVersionsAndDeletes":
            request_headers[http_constants.HttpHeaders.AIM] = http_constants.HttpHeaders.FullFidelityFeedHeaderValue
            request_headers[http_constants.HttpHeaders.ChangeFeedWireFormatVersion] = \
                http_constants.HttpHeaders.SeparateMetaWithCrts
        else:
            request_headers[http_constants.HttpHeaders.AIM] = http_constants.HttpHeaders.IncrementalFeedHeaderValue

    def populate_request_headers(
            self,
            routing_provider: SmartRoutingMapProvider,
            request_headers: Dict[str, Any]) -> None:
        self.set_start_from_request_headers(request_headers)

        # based on the feed range to find the overlapping partition key range id
        over_lapping_ranges = \
            routing_provider.get_overlapping_ranges(
                self._container_link,
                [self._continuation.current_token.feed_range])

        self.set_pk_range_id_request_headers(over_lapping_ranges, request_headers)

        self.set_mode_request_headers(request_headers)


    async def populate_request_headers_async(
            self,
            async_routing_provider: AsyncSmartRoutingMapProvider,
            request_headers: Dict[str, Any]) -> None:
        self.set_start_from_request_headers(request_headers)

        # based on the feed range to find the overlapping partition key range id
        over_lapping_ranges = \
            await async_routing_provider.get_overlapping_ranges(
                self._container_link,
                [self._continuation.current_token.feed_range])

        self.set_pk_range_id_request_headers(over_lapping_ranges, request_headers)

        self.set_mode_request_headers(request_headers)

    def populate_feed_options(self, feed_options: Dict[str, Any]) -> None:
        pass

    def handle_feed_range_gone(
            self,
            routing_provider: SmartRoutingMapProvider,
            resource_link: str) -> None:
        self._continuation.handle_feed_range_gone(routing_provider, resource_link)

    async def handle_feed_range_gone_async(
            self,
            routing_provider: AsyncSmartRoutingMapProvider,
            resource_link: str) -> None:
        await self._continuation.handle_feed_range_gone_async(routing_provider, resource_link)

    def apply_server_response_continuation(self, continuation: str, has_modified_response: bool) -> None:
        self._continuation.apply_server_response_continuation(continuation, has_modified_response)

    def should_retry_on_not_modified_response(self) -> bool:
        return self._continuation.should_retry_on_not_modified_response()

    def apply_not_modified_response(self) -> None:
        self._continuation.apply_not_modified_response()

    def get_feed_range_gone_error(self, over_lapping_ranges: List[Dict[str, Any]]) -> CosmosHttpResponseError:
        formatted_message =\
            (f"Status code: {StatusCodes.GONE} "
             f"Sub-status: {SubStatusCodes.PARTITION_KEY_RANGE_GONE}. "
             f"Range {self._continuation.current_token.feed_range}"
             f" spans {len(over_lapping_ranges)} physical partitions:"
             f" {[child_range['id'] for child_range in over_lapping_ranges]}")

        response_error = CosmosHttpResponseError(status_code=StatusCodes.GONE, message=formatted_message)
        response_error.sub_status = SubStatusCodes.PARTITION_KEY_RANGE_GONE
        return response_error

    @classmethod
    def from_continuation(
            cls,
            container_link: str,
            container_rid: str,
            continuation_json: Dict[str, Any]) -> 'ChangeFeedStateV2':

        container_rid_from_continuation = continuation_json.get(ChangeFeedStateV2.container_rid_property_name)
        if container_rid_from_continuation is None:
            raise ValueError(f"Invalid continuation: [Missing {ChangeFeedStateV2.container_rid_property_name}]")
        if container_rid_from_continuation != container_rid:
            raise ValueError("Invalid continuation: [Mismatch collection rid]")

        change_feed_start_from_data = continuation_json.get(ChangeFeedStateV2.change_feed_start_from_property_name)
        if change_feed_start_from_data is None:
            raise ValueError(f"Invalid continuation:"
                             f" [Missing {ChangeFeedStateV2.change_feed_start_from_property_name}]")
        change_feed_start_from = ChangeFeedStartFromInternal.from_json(change_feed_start_from_data)

        continuation_data = continuation_json.get(ChangeFeedStateV2.continuation_property_name)
        if continuation_data is None:
            raise ValueError(f"Invalid continuation: [Missing {ChangeFeedStateV2.continuation_property_name}]")
        continuation = FeedRangeCompositeContinuation.from_json(continuation_data)

        mode = continuation_json.get(ChangeFeedStateV2.mode_property_name)
        # All 'continuation_json' from ChangeFeedStateV2 must contain 'mode' property. For the 'continuation_json'
        # from older ChangeFeedState versions won't even hit this point, since their version is not 'v2'.
        if mode is None:
            raise ValueError(f"Invalid continuation: [Missing {ChangeFeedStateV2.mode_property_name}]")

        return cls(
            container_link=container_link,
            container_rid=container_rid,
            feed_range=continuation.feed_range,
            change_feed_start_from=change_feed_start_from,
            continuation=continuation,
            mode=mode)

    @classmethod
    def from_initial_state(
            cls,
            container_link: str,
            collection_rid: str,
            change_feed_state_context: Dict[str, Any]) -> 'ChangeFeedStateV2':

        feed_range: Optional[FeedRangeInternal] = None
        if change_feed_state_context.get("feedRange"):
            feed_range = FeedRangeInternalEpk.from_json(change_feed_state_context["feedRange"])
        elif change_feed_state_context.get("partitionKey"):
            if change_feed_state_context.get("partitionKeyFeedRange"):
                feed_range =\
                    FeedRangeInternalPartitionKey(
                        change_feed_state_context["partitionKey"],
                        change_feed_state_context["partitionKeyFeedRange"])
            else:
                raise ValueError("partitionKey is in the changeFeedStateContext, but missing partitionKeyFeedRange")
        else:
            # default to full range
            logging.info("'feed_range' empty. Using full range by default.")
            feed_range = FeedRangeInternalEpk(
                Range(
                "",
                "FF",
                True,
                False)
            )

        change_feed_start_from = (
            ChangeFeedStartFromInternal.from_start_time(change_feed_state_context.get("startTime")))

        mode = change_feed_state_context.get("mode")

        return cls(
            container_link=container_link,
            container_rid=collection_rid,
            feed_range=feed_range,
            change_feed_start_from=change_feed_start_from,
            continuation=None,
            mode=mode)
