# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from io import SEEK_END, SEEK_SET
import logging
import email
from datetime import datetime, timezone, timedelta
from typing import IO, Dict, Generator, Literal, Optional, Self, Tuple, Union
from urllib.parse import quote

from azure.core import MatchConditions
from azure.core.rest import HttpResponse


_LOGGER = logging.getLogger(__name__)
_DAYS = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
_MONTHS = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}


def serialize_rfc(data: datetime):
    """Serialize Datetime object into RFC-1123 formatted string.

    :param Datetime attr: Object to be serialized.
    :rtype: str
    :raises: TypeError if format invalid.
    """
    try:
        if not data.tzinfo:
            _LOGGER.warning("Datetime with no tzinfo will be considered UTC.")
        utc = data.utctimetuple()
    except AttributeError:
        raise TypeError("RFC1123 object must be valid Datetime object.")

    return "{}, {:02} {} {:04} {:02}:{:02}:{:02} GMT".format(
        _DAYS[utc.tm_wday],
        utc.tm_mday,
        _MONTHS[utc.tm_mon],
        utc.tm_year,
        utc.tm_hour,
        utc.tm_min,
        utc.tm_sec,
    )


def deserialize_rfc(value: str) -> datetime:
    """Deserialize RFC-1123 formatted string into Datetime object.

    :param str value: response string to be deserialized.
    :rtype: ~datetime.datetime
    """
    parsed_date = email.utils.parsedate_tz(value)  # type: ignore
    date_obj = datetime(
        *parsed_date[:6], tzinfo=timezone(timedelta(minutes=(parsed_date[9] or 0) / 60))
    )
    if not date_obj.tzinfo:
        date_obj = date_obj.astimezone(tz=timezone.utc)
    return date_obj


def quote_etag(etag: Optional[str]) -> Optional[str]:
    if not etag or etag == "*":
        return etag
    if etag.startswith("W/"):
        return etag
    if etag.startswith('"') and etag.endswith('"'):
        return etag
    if etag.startswith("'") and etag.endswith("'"):
        return etag
    return '"' + etag + '"'


def prep_if_match(etag: Optional[str], match_condition: Optional[MatchConditions]) -> Optional[str]:
    if match_condition == MatchConditions.IfNotModified:
        if_match = quote_etag(etag) if etag else None
        return if_match
    if match_condition == MatchConditions.IfPresent:
        return "*"
    return None


def prep_if_none_match(etag: Optional[str], match_condition: Optional[MatchConditions]) -> Optional[str]:
    if match_condition == MatchConditions.IfModified:
        if_none_match = quote_etag(etag) if etag else None
        return if_none_match
    if match_condition == MatchConditions.IfMissing:
        return "*"
    return None


def parse_content_range(content_range: str) -> Tuple[int, int, int]:
    """Parses the blob length from the content range header: bytes 1-3/65537"""
    # First, split in space and take the second half: '1-3/65537'
    # Next, split on slash and take the second half: '65537'
    # Finally, convert to an int: 65537
    byterange, total = content_range.split(' ')[1].split('/')
    start, end = byterange.split('-')
    return int(start), int(end), int(total)


def serialize_tags_header(tags: Optional[Dict[str, str]] = None) -> Optional[str]:
    if not tags:
        return None
    components = [f"{quote(k, safe='.-')}={quote(v, safe='.-')}" for k, v in tags.items()]
    return '&'.join(components)


def get_length(data: Union[bytes, IO[bytes]]) -> int:
    # Check if object implements the __len__ method, covers most input cases such as bytearray.
    try:
        return len(data)
    except:  # pylint: disable=bare-except
        # If the stream is seekable and tell() is implemented, calculate the stream size.
        try:
            current_position = data.tell()
            data.seek(0, SEEK_END)
            length = data.tell() - current_position
            data.seek(current_position, SEEK_SET)
            return length
        except (AttributeError, OSError):
            pass
    raise ValueError("Unable to determine length of data. Please provide 'content_length'.")


class Stream:
    content_length: int
    content_type: str
    content_encoding: str
    content_language: str
    content_disposition: str
    content_range: str
    cache_control: str

    def __init__(
            self, 
            *, 
            content_length: int,
            content_range: str,
            first_chunk: 'PartialStream',
            next_chunks: Optional[Generator[Tuple[HttpResponse, int, int, int], None, None]] = None,
    ) -> None:
        self._chunk_generator = next_chunks
        self._current_chunk = first_chunk
        self._closed = False
        self.content_length = content_length
        self.content_range = content_range
        self.content_type = self._current_chunk.content_type
        self.content_encoding = self._current_chunk.content_encoding
        self.content_language = self._current_chunk.content_language
        self.content_disposition = self._current_chunk.content_disposition
        self.cache_control = self._current_chunk.cache_control

    def __next__(self) -> bytes:
        if self._current_response:
            try:
                return next(self._current_response)
            except StopIteration:
                pass
        if self._chunk_generator:
            next_response, start, end, _ = next(self._chunk_generator)
            self._current_chunk = PartialStream(
                start=start,
                end=end,
                response=next_response
            )
            return next(self._current_chunk)
        raise StopIteration

    def __iter_(self) -> Self:
        return self

    def close(self) -> None:
        self._current_chunk.close()
        # TODO: Close down additional iteration.


class PartialStream:
    validation: Optional[bytes]
    content_type: str
    content_encoding: str
    content_language: str
    content_disposition: str
    cache_control: str

    def __init__(self, *, start: int, end: int, response: HttpResponse) -> None:
        self._response = response
        self._func = self._response.iter_raw()
        self._data: Optional[bytes] = None
        self._start = start
        self._end = end
        self.validation = response.headers.get('x-ms-content-crc64')
        self.content_type = response.headers['Content-Type']
        self.content_encoding = response.headers['Content-Encoding']
        self.content_language = response.headers['Content-Language']
        self.content_disposition = response.headers['Content-Disposition']
        self.cache_control = response.headers['Cache-Control']

    def __next__(self) -> bytes:
        if self.validation:
            if self._data:
                raise StopIteration
            self._data = b''.join(self._func)
            self._validate()
            return self._data
        return next(self._func)

    def __iter_(self) -> Self:
        return self

    def _validate(self) -> None:
        # perform crc64 validation
        raise NotImplementedError()

    def write(self, stream: IO[bytes]) -> int:
        stream.seek(self._start)
        if self._data:
            stream.write(self._data)
        else:
            for data in self:
                stream.write(data)

    def close(self) -> None:
        self._response.close()
