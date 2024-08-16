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

"""Internal class for change feed continuation token by feed range in the Azure Cosmos
database service.
"""
import collections
from collections import deque
from typing import Any

from azure.cosmos._change_feed.aio.composite_continuation_token import CompositeContinuationToken
from azure.cosmos._routing.aio.routing_map_provider import SmartRoutingMapProvider
from azure.cosmos._routing.routing_range import Range


class FeedRangeCompositeContinuation(object):
    _version_property_name = "V"
    _container_rid_property_name = "Rid"
    _continuation_property_name = "Continuation"
    _feed_range_property_name = "Range"

    def __init__(
            self,
            container_rid: str,
            feed_range: Range,
            continuation: collections.deque[CompositeContinuationToken]):
        if container_rid is None:
            raise ValueError("container_rid is missing")

        self._container_rid = container_rid
        self._feed_range = feed_range
        self._continuation = continuation
        self._current_token = self._continuation[0]
        self._initial_no_result_range = None

    @property
    def current_token(self):
        return self._current_token

    def to_dict(self) -> dict[str, Any]:
        return {
            self._version_property_name: "v1", #TODO: should this start from v2
            self._container_rid_property_name: self._container_rid,
            self._continuation_property_name: [childToken.to_dict() for childToken in self._continuation],
            self._feed_range_property_name: self._feed_range.to_dict()
        }

    @classmethod
    def from_json(cls, data) -> 'FeedRangeCompositeContinuation':
        version = data.get(cls._version_property_name)
        if version is None:
            raise ValueError(f"Invalid feed range composite continuation token [Missing {cls._version_property_name}]")
        if version != "v1":
            raise ValueError("Invalid feed range composite continuation token [Invalid version]")

        container_rid = data.get(cls._container_rid_property_name)
        if container_rid is None:
            raise ValueError(f"Invalid feed range composite continuation token [Missing {cls._container_rid_property_name}]")

        feed_range_data = data.get(cls._feed_range_property_name)
        if feed_range_data is None:
            raise ValueError(f"Invalid feed range composite continuation token [Missing {cls._feed_range_property_name}]")
        feed_range = Range.ParseFromDict(feed_range_data)

        continuation_data = data.get(cls._continuation_property_name)
        if continuation_data is None:
            raise ValueError(f"Invalid feed range composite continuation token [Missing {cls._continuation_property_name}]")
        if not isinstance(continuation_data, list) or len(continuation_data) == 0:
            raise ValueError(f"Invalid feed range composite continuation token [The {cls._continuation_property_name} must be non-empty array]")
        continuation = [CompositeContinuationToken.from_json(child_range_continuation_token) for child_range_continuation_token in continuation_data]

        return cls(container_rid=container_rid, feed_range=feed_range, continuation=deque(continuation))

    async def handle_feed_range_gone(self, routing_provider: SmartRoutingMapProvider, collection_link: str) -> None:
        overlapping_ranges = await routing_provider.get_overlapping_ranges(collection_link, self._current_token.feed_range)

        if len(overlapping_ranges) == 1:
            # merge,reusing the existing the feedRange and continuationToken
            pass
        else:
            # split, remove the parent range and then add new child ranges.
            # For each new child range, using the continuation token from the parent
            self._continuation.popleft()
            for child_range in overlapping_ranges:
                self._continuation.append(CompositeContinuationToken(Range.PartitionKeyRangeToRange(child_range), self._current_token.token))

            self._current_token = self._continuation[0]

    def should_retry_on_not_modified_response(self) -> bool:
        # when getting 304(Not Modified) response from one sub feed range, we will try to fetch for the next sub feed range
        # we will repeat the above logic until we have looped through all sub feed ranges

        # TODO: validate the response headers, can we get the status code
        if len(self._continuation) > 1:
            return self._current_token.feed_range != self._initial_no_result_range

        else:
            return False

    def _move_to_next_token(self) -> None:
        first_composition_token = self._continuation.popleft()
        # add the composition token to the end of the list
        self._continuation.append(first_composition_token)
        self._current_token = self._continuation[0]

    def apply_server_response_continuation(self, etag) -> None:
        self._current_token.update_token(etag)
        self._move_to_next_token()

    def apply_not_modified_response(self) -> None:
        if self._initial_no_result_range is None:
            self._initial_no_result_range = self._current_token.feed_range

    @property
    def feed_range(self) -> Range:
        return self._feed_range
