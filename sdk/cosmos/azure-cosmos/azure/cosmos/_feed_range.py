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

import base64
import json
from abc import ABC
from typing import Any, Dict

from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range

# pylint: disable=protected-access
class FeedRange(ABC):
    """Represents a single feed range in an Azure Cosmos DB SQL API container.

    """
    @staticmethod
    def from_string(json_str: str) -> 'FeedRange':
        """
        Create a feed range from previously obtained string representation.

        :param str json_str: A string representation of a feed range.
        :return: A feed range.
        :rtype: ~azure.cosmos.FeedRange
        """
        feed_range_json_str = base64.b64decode(json_str).decode('utf-8')
        feed_range_json = json.loads(feed_range_json_str)
        if feed_range_json.get(FeedRangeEpk.type_property_name):
            return FeedRangeEpk._from_json(feed_range_json)

        raise ValueError("Invalid feed range base64 encoded string [Wrong feed range type]")

class FeedRangeEpk(FeedRange):
    type_property_name = "Range"

    def __init__(self, feed_range: Range) -> None:
        if feed_range is None:
            raise ValueError("feed_range cannot be None")

        self._feed_range_internal = FeedRangeInternalEpk(feed_range)

    def __str__(self) -> str:
        """Get a json representation of the feed range.
           The returned json string can be used to create a new feed range from it.

        :return: A json representation of the feed range.
        """
        return self._feed_range_internal.__str__()

    @classmethod
    def _from_json(cls, data: Dict[str, Any]) -> 'FeedRange':
        return cls(FeedRangeInternalEpk.from_json(data)._range)
