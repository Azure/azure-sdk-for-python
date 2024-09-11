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

"""Internal class for feed range implementation in the Azure Cosmos
database service.
"""
from abc import ABC, abstractmethod
from typing import Union, List, Dict, Any

from azure.cosmos._routing.routing_range import Range, PartitionKeyRange
from azure.cosmos.partition_key import _Undefined, _Empty


class FeedRange(ABC):

    @abstractmethod
    def get_normalized_range(self) -> Range:
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass



    @staticmethod
    def _get_range(pk_ranges) -> Range:
        max_range = pk_ranges[0][PartitionKeyRange.MaxExclusive]
        min_range = pk_ranges[0][PartitionKeyRange.MinInclusive]
        for i in range(1, len(pk_ranges)):
            pk_ranges_min = pk_ranges[i][PartitionKeyRange.MinInclusive]
            pk_ranges_max = pk_ranges[i][PartitionKeyRange.MaxExclusive]
            if pk_ranges_min < min_range:
                min_range = pk_ranges_min
            if pk_ranges_max > max_range:
                max_range = pk_ranges_max
        return Range(min_range, max_range, True, False)

class FeedRangePartitionKey(FeedRange):
    type_property_name = "PK"

    def __init__(
            self,
            pk_value: Union[str, int, float, bool, List[Union[str, int, float, bool]], _Empty, _Undefined],
            feed_range: Range) -> None:  # pylint: disable=line-too-long

        if pk_value is None:
            raise ValueError("PartitionKey cannot be None")
        if feed_range is None:
            raise ValueError("Feed range cannot be None")

        self._pk_value = pk_value
        self._feed_range = feed_range

    def get_normalized_range(self) -> Range:
        return self._feed_range.to_normalized_range()

    def to_dict(self) -> Dict[str, Any]:
        if isinstance(self._pk_value, _Undefined):
            return { self.type_property_name: [{}] }
        if isinstance(self._pk_value, _Empty):
            return { self.type_property_name: [] }
        if isinstance(self._pk_value, list):
            return { self.type_property_name: list(self._pk_value) }

        return { self.type_property_name: self._pk_value }

    @classmethod
    def from_json(cls, data: Dict[str, Any], feed_range: Range) -> 'FeedRangePartitionKey':
        if data.get(cls.type_property_name):
            pk_value = data.get(cls.type_property_name)
            if not pk_value:
                return cls(_Empty(), feed_range)
            if pk_value == [{}]:
                return cls(_Undefined(), feed_range)
            if isinstance(pk_value, list):
                return cls(list(pk_value), feed_range)
            return cls(data[cls.type_property_name], feed_range)

        raise ValueError(f"Can not parse FeedRangePartitionKey from the json,"
                         f" there is no property {cls.type_property_name}")


class FeedRangeEpk(FeedRange):
    type_property_name = "Range"

    def __init__(self, feed_range: Range) -> None:
        if feed_range is None:
            raise ValueError("feed_range cannot be None")

        self._range = feed_range

    def get_normalized_range(self) -> Range:
        return self._range.to_normalized_range()

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.type_property_name: self._range.to_dict()
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'FeedRangeEpk':
        if data.get(cls.type_property_name):
            feed_range = Range.ParseFromDict(data.get(cls.type_property_name))
            return cls(feed_range)
        raise ValueError(f"Can not parse FeedRangeEPK from the json, there is no property {cls.type_property_name}")
