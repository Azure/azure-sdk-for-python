# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from collections.abc import Iterator
from io import SEEK_END, SEEK_SET, RawIOBase, UnsupportedOperation
from types import TracebackType
import logging
import email
from itertools import islice
from datetime import datetime, timezone, timedelta
from typing import IO, Literal, Any, Callable, Dict, Generator, Generic, Optional, Tuple, TypeVar, Union, NoReturn
from typing_extensions import Self
from urllib.parse import quote

from azure.core import MatchConditions
from azure.core.rest import HttpResponse

PageType = TypeVar('PageType')

class Pages(Generic[PageType]):
    continuation: Optional[str] = None
    n_pages: Optional[int] = None

    def __init__(
            self,
            page_gen: Callable[[Optional[str]], Generator[PageType, None, Optional[str]]],
            *,
            n_pages: Optional[int] = None,
            continuation: Optional[str] = None,
    ):
        self._page_gen = page_gen
        self.n_pages = n_pages
        self.continuation = continuation

    def __iter__(self) -> Generator[PageType, None, Optional[str]]:
        self.continuation = yield from self._request_n_pages()
        return self.continuation

    def _request_n_pages(self) -> Generator[PageType, None, Optional[str]]:
        continuation = yield from self._page_gen(self.continuation)
        if self.n_pages:
            pages = self.n_pages - 1
            while pages and continuation:
                continuation = yield from self._page_gen(continuation)
                pages -= 1
        else:
            while continuation:
                continuation = yield from self._page_gen(continuation)
        return continuation


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


_METADATA = "x-ms-meta-"
_METADATA_PREFIX_LEN = len(_METADATA)

def deserialize_metadata_header(headers: Dict[str, Any]) -> Dict[str, str]:
    return {k[_METADATA_PREFIX_LEN:]: v for k, v in headers.items() if k.startswith(_METADATA)}


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


class Stream(RawIOBase):
    content_length: int
    content_range: str

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
        self._data: bytes = b""
        self.content_length = content_length
        self.content_range = content_range

    def __len__(self) -> int:
        return self.content_length

    def __enter__(self) -> Self:
        if self._closed:
            raise ValueError("I/O operation on closed stream.")
        return super().__enter__()

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None) -> None:
        self.close()
        return super().__exit__(exc_type, exc_val, exc_tb)

    def _get_next_chunk(self) -> bytes:
        if self._current_chunk:
            try:
                return next(self._current_chunk)
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

    def _get_line(self, size: Optional[int]) -> Optional[bytes]:
        line_split = self._data.find(b'\n')
        if line_split >= 0:
            line_split += 1
            if size is not None and size < line_split:
                new_line = self._data[0: size]
                self._data = self._data[size:]
                return new_line
            new_line = self._data[0: line_split]
            self._data = self._data[line_split:]
            return new_line
        elif size is not None and size < len(self._data):
            new_line = self._data[0: size]
            self._data = self._data[size:]
            return new_line
        return None

    def __next__(self) -> bytes:
        next_line = self.readline()
        if next_line == b"":
            self.close()
            raise StopIteration()

    def __iter__(self) -> Iterator[bytes]:
        return self

    @property
    def closed(self) -> bool:
        return self._closed

    def close(self) -> None:
        self._current_chunk.close()
        self._closed = True
        # TODO: Close down additional iteration.

    def readable(self) -> Literal[True]:
        if self._closed:
            raise ValueError("I/O operation on closed stream.")
        return True

    def writable(self) -> Literal[False]:
        if self._closed:
            raise ValueError("I/O operation on closed stream.")
        return False

    def fileno(self) -> NoReturn:
        if self._closed:
            raise ValueError("I/O operation on closed stream.")
        raise UnsupportedOperation()

    def flush(self) -> None:
        if self._closed:
            raise ValueError("I/O operation on closed stream.")
        return None

    def isatty(self) -> Literal[False]:
        if self._closed:
            raise ValueError("I/O operation on closed stream.")
        return False

    def readline(self, size: int | None = -1) -> bytes:
        if self._closed:
            raise ValueError("I/O operation on closed stream.")
        if size < 0:
            size = None
        while True:
            line = self._get_line(size)
            if line:
                return line
            try:
                self._data += self._get_next_chunk()
            except StopIteration:
                line = self._data
                self._data = b""
                return line

    def readlines(self, hint: int = -1) -> list[bytes]:
        if self._closed:
            raise ValueError("I/O operation on closed stream.")
        lines = []
        if hint == 0:
            return lines
        line = self.readline()
        if hint < 0:
            while line:
                lines.append(line)
                line = self.readline()
        else:
            while line and len(lines) < hint:
                lines.append(line)
                line = self.readline()
        return lines

    def read(self, size: int = -1) -> bytes:
        if self._closed:
            raise ValueError("I/O operation on closed stream.")
        if size >= 0:
            while len(self._data) < size:
                try:
                    self._data += self._get_next_chunk()
                except StopIteration:
                    break
            data = self._data[0: size]
            self._data = self._data[size:]
            return data
        data = b"".join(self.readlines())
        return data

    def seekable(self) -> Literal[False]:
        if self._closed:
            raise ValueError("I/O operation on closed stream.")
        return False



class PartialStream:
    validation: Optional[bytes]
    content_length: int
    content_range: str

    def __init__(self, *, start: int, end: int, response: HttpResponse) -> None:
        self._response = response
        self._func: Iterable[bytes] = self._response.iter_raw()
        self._data: Optional[bytes] = None
        self._start = start
        self._end = end
        self.validation = response.headers.get('x-ms-content-crc64')
        self.content_length = response.headers['Content-Length']
        self.content_range = response.headers['Content-Range']

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
        # TODO: perform crc64 validation
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
