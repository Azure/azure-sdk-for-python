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
from abc import ABC, abstractmethod
from typing import Any, Dict

from azure.cosmos._change_feed.feed_range_internal import FeedRangeInternal, FeedRangeInternalEpk
from azure.cosmos._routing.routing_range import Range

# pylint: disable=protected-access
class FeedRange(ABC):
    """Represents a single feed range in an Azure Cosmos DB SQL API container.

    """

    def to_string(self) -> str:
        """
        Get a json representation of the feed range.
        The returned json string can be used to create a new feed range from it.

        :return: A json representation of the feed range.
        :rtype: str
        """

        return self._to_base64_encoded_string()

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

    @abstractmethod
    def _to_dict(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def _to_feed_range_internal(self) -> 'FeedRangeInternal':
        pass

    def _to_base64_encoded_string(self) -> str:
        data_json = json.dumps(self._to_dict())
        json_bytes = data_json.encode('utf-8')
        # Encode the bytes to a Base64 string
        base64_bytes = base64.b64encode(json_bytes)
        # Convert the Base64 bytes to a string
        return base64_bytes.decode('utf-8')

class FeedRangeEpk (FeedRange):
    type_property_name = "Range"

    def __init__(self, feed_range: Range) -> None:
        if feed_range is None:
            raise ValueError("feed_range cannot be None")

        self._feed_range = feed_range

    def _to_dict(self) -> Dict[str, Any]:
        return {
            self.type_property_name: self._feed_range.to_dict()
        }

    def _to_feed_range_internal(self) -> 'FeedRangeInternal':
        return FeedRangeInternalEpk(self._feed_range)

    @classmethod
    def _from_json(cls, data: Dict[str, Any]) -> 'FeedRange':
        if data.get(cls.type_property_name):
            feed_range = Range.ParseFromDict(data.get(cls.type_property_name))
            return cls(feed_range)
        raise ValueError(f"Can not parse FeedRangeEPK from the json, there is no property {cls.type_property_name}")
