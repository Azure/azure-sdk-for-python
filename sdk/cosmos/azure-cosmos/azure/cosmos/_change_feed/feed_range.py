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
import json
from abc import ABC, abstractmethod
from typing import Union, List

from azure.cosmos import PartitionKey
from azure.cosmos._routing.routing_range import Range
from azure.cosmos._utils import is_key_exists_and_not_none
from azure.cosmos.partition_key import _Undefined, _Empty


class FeedRange(ABC):

    @abstractmethod
    def get_normalized_range(self, partition_key_range_definition: PartitionKey) -> Range:
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, any]:
        pass

class FeedRangePartitionKey(FeedRange):
    type_property_name = "PK"

    def __init__(
            self,
            pk_value: Union[str, int, float, bool, List[Union[str, int, float, bool]], _Empty, _Undefined]):
        if pk_value is None:
            raise ValueError("PartitionKey cannot be None")

        self._pk_value = pk_value

    def get_normalized_range(self, partition_key_definition: PartitionKey) -> Range:
        return partition_key_definition._get_epk_range_for_partition_key(self._pk_value).to_normalized_range()

    def to_dict(self) -> dict[str, any]:
        if isinstance(self._pk_value, _Undefined):
            return { self.type_property_name: [{}] }
        elif isinstance(self._pk_value, _Empty):
            return { self.type_property_name: [] }
        else:
            return { self.type_property_name: json.dumps(self._pk_value) }

    @classmethod
    def from_json(cls, data: dict[str, any]) -> 'FeedRangePartitionKey':
        if is_key_exists_and_not_none(data, cls.type_property_name):
            pk_value = data.get(cls.type_property_name)
            if isinstance(pk_value, list):
                if not pk_value:
                    return cls(_Empty())
            if pk_value == [{}]:
                return cls(_Undefined())

            return cls(json.loads(data.get(cls.type_property_name)))
        raise ValueError(f"Can not parse FeedRangePartitionKey from the json, there is no property {cls.type_property_name}")

class FeedRangeEpk(FeedRange):
    type_property_name = "Range"

    def __init__(self, feed_range: Range):
        if feed_range is None:
            raise ValueError("feed_range cannot be None")

        self._range = feed_range

    def get_normalized_range(self,  partition_key_definition: PartitionKey) -> Range:
        return self._range.to_normalized_range()

    def to_dict(self) -> dict[str, any]:
        return {
            self.type_property_name: self._range.to_dict()
        }

    @classmethod
    def from_json(cls, data: dict[str, any]) -> 'FeedRangeEpk':
        if is_key_exists_and_not_none(data, cls.type_property_name):
            feed_range = Range.ParseFromDict(data.get(cls.type_property_name))
            return cls(feed_range)
        raise ValueError(f"Can not parse FeedRangeEPK from the json, there is no property {cls.type_property_name}")