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
import base64
import json
from abc import ABC, abstractmethod
from typing import Union, List, Dict, Any, Optional

from azure.cosmos._routing.routing_range import Range
from azure.cosmos.partition_key import _Undefined, _Empty


class FeedRangeInternal(ABC):

    @abstractmethod
    def get_normalized_range(self) -> Range:
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass

    def _to_base64_encoded_string(self) -> str:
        data_json = json.dumps(self.to_dict())
        json_bytes = data_json.encode('utf-8')
        # Encode the bytes to a Base64 string
        base64_bytes = base64.b64encode(json_bytes)
        # Convert the Base64 bytes to a string
        return base64_bytes.decode('utf-8')

class FeedRangeInternalPartitionKey(FeedRangeInternal):
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
    def from_json(cls, data: Dict[str, Any], feed_range: Range) -> 'FeedRangeInternalPartitionKey':
        if data.get(cls.type_property_name):
            pk_value = data.get(cls.type_property_name)
            if not pk_value:
                return cls(_Empty(), feed_range)
            if pk_value == [{}]:
                return cls(_Undefined(), feed_range)
            if isinstance(pk_value, list):
                return cls(list(pk_value), feed_range)
            return cls(data[cls.type_property_name], feed_range)

        raise ValueError(f"Can not parse FeedRangeInternalPartitionKey from the json,"
                         f" there is no property {cls.type_property_name}")


class FeedRangeInternalEpk(FeedRangeInternal):
    type_property_name = "Range"

    def __init__(self, feed_range: Range) -> None:
        if feed_range is None:
            raise ValueError("feed_range cannot be None")

        self._range = feed_range
        self._base64_encoded_string: Optional[str] = None

    def get_normalized_range(self) -> Range:
        return self._range.to_normalized_range()

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.type_property_name: self._range.to_dict()
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'FeedRangeInternalEpk':
        if data.get(cls.type_property_name):
            feed_range = Range.ParseFromDict(data.get(cls.type_property_name))
            return cls(feed_range)
        raise ValueError(f"Can not parse FeedRangeInternalEPK from the json,"
                         f" there is no property {cls.type_property_name}")

    def __str__(self) -> str:
        """Get a json representation of the feed range.
           The returned json string can be used to create a new feed range from it.

        :return: A json representation of the feed range.
        """
        if self._base64_encoded_string is None:
            self._base64_encoded_string = self._to_base64_encoded_string()

        return self._base64_encoded_string
