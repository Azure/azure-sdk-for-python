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

"""Internal class for change feed start from implementation in the Azure Cosmos database service.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Union, Literal, Any, Dict

from azure.cosmos import http_constants
from azure.cosmos._routing.routing_range import Range

class ChangeFeedStartFromType(Enum):
    BEGINNING = "Beginning"
    NOW = "Now"
    LEASE = "Lease"
    POINT_IN_TIME = "PointInTime"

class ChangeFeedStartFromInternal(ABC):
    """Abstract class for change feed start from implementation in the Azure Cosmos database service.
    """

    type_property_name = "Type"

    def __init__(self, start_from_type: ChangeFeedStartFromType) -> None:
        self.version = start_from_type

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        pass

    @staticmethod
    def from_start_time(
            start_time: Optional[Union[datetime, Literal["Now", "Beginning"]]]) -> 'ChangeFeedStartFromInternal':
        if start_time is None:
            return ChangeFeedStartFromNow()
        if isinstance(start_time, datetime):
            return ChangeFeedStartFromPointInTime(start_time)
        if start_time.lower() == ChangeFeedStartFromType.NOW.value.lower():
            return ChangeFeedStartFromNow()
        if start_time.lower() == ChangeFeedStartFromType.BEGINNING.value.lower():
            return ChangeFeedStartFromBeginning()

        raise ValueError(f"Invalid start_time '{start_time}'")

    @staticmethod
    def from_json(data: Dict[str, Any]) -> 'ChangeFeedStartFromInternal':
        change_feed_start_from_type = data.get(ChangeFeedStartFromInternal.type_property_name)
        if change_feed_start_from_type is None:
            raise ValueError(f"Invalid start from json [Missing {ChangeFeedStartFromInternal.type_property_name}]")

        if change_feed_start_from_type == ChangeFeedStartFromType.BEGINNING.value:
            return ChangeFeedStartFromBeginning.from_json(data)
        if change_feed_start_from_type == ChangeFeedStartFromType.LEASE.value:
            return ChangeFeedStartFromETagAndFeedRange.from_json(data)
        if change_feed_start_from_type == ChangeFeedStartFromType.NOW.value:
            return ChangeFeedStartFromNow.from_json(data)
        if change_feed_start_from_type == ChangeFeedStartFromType.POINT_IN_TIME.value:
            return ChangeFeedStartFromPointInTime.from_json(data)

        raise ValueError(f"Can not process changeFeedStartFrom for type {change_feed_start_from_type}")

    @abstractmethod
    def populate_request_headers(self, request_headers) -> None:
        pass


class ChangeFeedStartFromBeginning(ChangeFeedStartFromInternal):
    """Class for change feed start from beginning implementation in the Azure Cosmos database service.
    """

    def __init__(self) -> None:
        super().__init__(ChangeFeedStartFromType.BEGINNING)

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.type_property_name: ChangeFeedStartFromType.BEGINNING.value
        }

    def populate_request_headers(self, request_headers) -> None:
        pass  # there is no headers need to be set for start from beginning

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ChangeFeedStartFromBeginning':
        return ChangeFeedStartFromBeginning()


class ChangeFeedStartFromETagAndFeedRange(ChangeFeedStartFromInternal):
    """Class for change feed start from etag and feed range implementation in the Azure Cosmos database service.
    """

    _etag_property_name = "Etag"
    _feed_range_property_name = "FeedRange"

    def __init__(self, etag, feed_range) -> None:
        if feed_range is None:
            raise ValueError("feed_range is missing")

        self._etag = etag
        self._feed_range = feed_range
        super().__init__(ChangeFeedStartFromType.LEASE)

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.type_property_name: ChangeFeedStartFromType.LEASE.value,
            self._etag_property_name: self._etag,
            self._feed_range_property_name: self._feed_range.to_dict()
        }

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ChangeFeedStartFromETagAndFeedRange':
        etag = data.get(cls._etag_property_name)
        if etag is None:
            raise ValueError(f"Invalid change feed start from [Missing {cls._etag_property_name}]")

        feed_range_data = data.get(cls._feed_range_property_name)
        if feed_range_data is None:
            raise ValueError(f"Invalid change feed start from [Missing {cls._feed_range_property_name}]")
        feed_range = Range.ParseFromDict(feed_range_data)
        return cls(etag, feed_range)

    def populate_request_headers(self, request_headers) -> None:
        # change feed uses etag as the continuationToken
        if self._etag:
            request_headers[http_constants.HttpHeaders.IfNoneMatch] = self._etag


class ChangeFeedStartFromNow(ChangeFeedStartFromInternal):
    """Class for change feed start from etag and feed range implementation in the Azure Cosmos database service.
    """

    def __init__(self) -> None:
        super().__init__(ChangeFeedStartFromType.NOW)

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.type_property_name: ChangeFeedStartFromType.NOW.value
        }

    def populate_request_headers(self, request_headers) -> None:
        request_headers[http_constants.HttpHeaders.IfNoneMatch] = "*"

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ChangeFeedStartFromNow':
        return ChangeFeedStartFromNow()


class ChangeFeedStartFromPointInTime(ChangeFeedStartFromInternal):
    """Class for change feed start from point in time implementation in the Azure Cosmos database service.
    """

    _point_in_time_ms_property_name = "PointInTimeMs"

    def __init__(self, start_time: datetime):
        if start_time is None:
            raise ValueError("start_time is missing")

        self._start_time = start_time
        super().__init__(ChangeFeedStartFromType.POINT_IN_TIME)

    def to_dict(self) -> Dict[str, Any]:
        return {
            self.type_property_name: ChangeFeedStartFromType.POINT_IN_TIME.value,
            self._point_in_time_ms_property_name:
                int(self._start_time.astimezone(timezone.utc).timestamp() * 1000)
        }

    def populate_request_headers(self, request_headers) -> None:
        request_headers[http_constants.HttpHeaders.IfModified_since] =\
            self._start_time.astimezone(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'ChangeFeedStartFromPointInTime':
        point_in_time_ms = data.get(cls._point_in_time_ms_property_name)
        if point_in_time_ms is None:
            raise ValueError(f"Invalid change feed start from {cls._point_in_time_ms_property_name} ")

        point_in_time = datetime.fromtimestamp(point_in_time_ms).astimezone(timezone.utc)
        return ChangeFeedStartFromPointInTime(point_in_time)
