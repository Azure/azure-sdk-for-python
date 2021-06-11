# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
import os
import codecs
from enum import Enum
from inspect import isgenerator
from json import dumps
import collections
from typing import (
    Optional,
    Union,
    Mapping,
    Sequence,
    List,
    Tuple,
    IO,
    Any,
    Dict,
    Iterable,
    Iterator,
    cast,
)
import xml.etree.ElementTree as ET
import six
try:
    from urlparse import urlparse  # type: ignore
except ImportError:
    from urllib.parse import urlparse

################################### TYPES SECTION #########################

PrimitiveData = Optional[Union[str, int, float, bool]]


ParamsType = Union[
    Mapping[str, Union[PrimitiveData, Sequence[PrimitiveData]]],
    List[Tuple[str, PrimitiveData]]
]

HeadersType = Mapping[str, str]

FileContent = Union[str, bytes, IO[str], IO[bytes]]
FileType = Union[
    Tuple[Optional[str], FileContent],
]

FilesType = Union[
    Mapping[str, FileType],
    Sequence[Tuple[str, FileType]]
]

ContentTypeBase = Union[str, bytes, Iterable[bytes]]

class HttpVerbs(str, Enum):
    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    HEAD = "HEAD"
    PATCH = "PATCH"
    DELETE = "DELETE"
    MERGE = "MERGE"

########################### ERRORS SECTION #################################

class StreamConsumedError(Exception):
    def __init__(self):
        message = (
            "You are attempting to read or stream content that has already been streamed. "
            "You have likely already consumed this stream, so it can not be accessed anymore."
        )
        super(StreamConsumedError, self).__init__(message)

class ResponseClosedError(Exception):
    def __init__(self):
        message = (
            "You can not try to read or stream this response's content, since the "
            "response has been closed."
        )
        super(ResponseClosedError, self).__init__(message)

class ResponseNotReadError(Exception):

    def __init__(self):
        message = (
            "You have not read in the response's bytes yet. Call response.read() first."
        )
        super(ResponseNotReadError, self).__init__(message)

class RequestNotReadError(Exception):

    def __init__(self):
        message = (
            "You have not read in the request's bytes yet. Call request.read() first."
        )
        super(RequestNotReadError, self).__init__(message)

########################### STREAM SECTION #################################

class SyncByteStream(object):
    def __init__(self, stream):
        self._data = stream  # naming it data bc this is what requests / aiohttp are interested in

    def __iter__(self):
        raise NotImplementedError()

    def close(self):
        """Close the stream"""

    def read(self):
        # type: () -> bytes
        """Read the stream"""

class ByteStream(SyncByteStream):
    def __init__(self, stream):
        # type: (bytes) -> None
        super(ByteStream, self).__init__(stream)
        self._stream = stream

    def __iter__(self):
        # type: () -> Iterator[bytes]
        yield self._stream

class IteratorByteStream(SyncByteStream):
    def __init__(self, stream):
        # type: (Iterable[bytes]) -> None
        super(IteratorByteStream, self).__init__(stream)
        self._stream = stream
        self._is_stream_consumed = False
        self._is_generator = isgenerator(stream)

    def __iter__(self):
        # type: () -> Iterator[bytes]
        if self._is_stream_consumed and self._is_generator:
            raise StreamConsumedError()

        self._is_stream_consumed = True
        for part in self._stream:
            yield part

def to_bytes(value):
    # type: (Union[str, bytes]) -> bytes
    return value.encode("utf-8") if isinstance(value, six.string_types) else value

class MultipartDataField(object):
    def __init__(self, name, value):
        if not isinstance(name, str):
            raise TypeError(
                "Invalid type for data name. Expected str, got {}: {}".format(
                    type(name), name
                )
            )
        if not isinstance(value, (str, bytes)):
            raise TypeError(
                "Invalid type for data value. Expected str or bytes, got {}: {}".format(
                    type(value), value
                )
        )
        self.name = name
        self.value = value
        self._headers = None
        self._data = None

    def render_data(self):
        # type: () -> bytes
        if self._data is None:
            self._data = to_bytes(self.value)
        return self._data

    def render(self):
        # type: () -> Iterator[bytes]
        yield self.render_data()


class MultipartFileField(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

def _validate_single(name, value):
    if not isinstance(name, str):
        raise TypeError(
            "Invalid type for data name. Expected str, got {}: {}".format(
                type(name), name
            )
        )
    if not isinstance(value, (str, bytes)):
        raise TypeError(
            "Invalid type for data value. Expected str or bytes, got {}: {}".format(
                type(value), value
            )
    )

def _validate(data):
    for name, value in data.items():
        if isinstance(value, list):
            for item in value:
                _validate_single(name=name, value=item)
        else:
            _validate_single(name, value)

class MultipartHolder():
    def __init__(self, data, files):
        # type: (dict, FileType) -> None
        _validate(data)
        self._data = data
        self._files = files

########################### HELPER SECTION #################################

def _verify_data_object(name, value):
    if not isinstance(name, str):
        raise TypeError(
            "Invalid type for data name. Expected str, got {}: {}".format(
                type(name), name
            )
        )
    if value is not None and not isinstance(value, (str, bytes, int, float)):
        raise TypeError(
            "Invalid type for value. Expected primitive type, got {}: {}".format(
                type(name), name
            )
        )

def _format_data(data):
    # type: (Union[str, IO]) -> Union[Tuple[None, str], Tuple[Optional[str], IO, str]]
    """Format field data according to whether it is a stream or
    a string for a form-data request.

    :param data: The request field data.
    :type data: str or file-like object.
    """
    if hasattr(data, "read"):
        data = cast(IO, data)
        data_name = None
        try:
            if data.name[0] != "<" and data.name[-1] != ">":
                data_name = os.path.basename(data.name)
        except (AttributeError, TypeError):
            pass
        return (data_name, data, "application/octet-stream")
    return (None, cast(str, data))

def set_multipart_body(data, files):
    formatted_files = {
        f: _format_data(d) for f, d in files.items() if d is not None
    }
    return {}, MultipartHolder(data=data, files=formatted_files)

def set_urlencoded_body(data):
    body = {}
    for f, d in data.items():
        if not d:
            continue
        if isinstance(d, list):
            for item in d:
                _verify_data_object(f, item)
        else:
            _verify_data_object(f, d)
        body[f] = d
    return {
        "Content-Type": "application/x-www-form-urlencoded"
    }, body

class RequestHelper(object):

    @property
    def byte_stream(self):
        return ByteStream

    @property
    def iterator_byte_stream(self):
        return IteratorByteStream

    def set_xml_body(self, content):
        headers = {}
        bytes_content = ET.tostring(content, encoding="utf-8")
        body = bytes_content.replace(b"encoding='utf8'", b"encoding='utf-8'")
        if body:
            headers["Content-Length"] = str(len(body))
        return headers, self.byte_stream(body)

    def _shared_set_content_body(self, content):
        # type: (Any) -> Tuple[Dict[str, str], Optional[SyncByteStream]]
        headers = {}

        if isinstance(content, ET.Element):
            # XML body
            return self.set_xml_body(content)
        if isinstance(content, (str, bytes)):
            headers = {}
            if isinstance(content, six.string_types):
                body = content.encode("utf-8")
                headers["Content-Type"] = "text/plain"
            else:
                body = content
            if body:
                headers["Content-Length"] = str(len(body))
            return headers, self.byte_stream(body)
        if isinstance(content, collections.Iterable):
            return {"Transfer-Encoding": "chunked"}, self.iterator_byte_stream(content)
        return headers, None

    def set_content_body(self, content):
        headers, body = self._shared_set_content_body(content)
        if body:
            return headers, body
        raise TypeError(
            "Unexpected type for 'content': '{}'. ".format(type(content)) +
            "We expect 'content' to either be str, bytes, or an Iterable"
        )

    def set_json_body(self, json):
        # type: (Any) -> Tuple[Dict[str, str], ByteStream]
        body = dumps(json).encode("utf-8")
        return {
            "Content-Type": "application/json",
            "Content-Length": str(len(body))
        }, self.byte_stream(body)



    def set_body(self, content, data, files, json):
        # type: (ContentTypeBase, dict, FilesType, Any) -> Tuple[Dict[str, str], SyncByteStream]
        if data is not None and not isinstance(data, dict):
            # should we warn?
            return self.set_content_body(data)
        if content is not None:
            return self.set_content_body(content)
        if json is not None:
            return self.set_json_body(json)
        if files:
            return set_multipart_body(data or {}, files)
        if data:
            return set_urlencoded_body(data)
        return {}, self.byte_stream(b"")

    @staticmethod
    def format_parameters(url, params):
        """Format parameters into a valid query string.
        It's assumed all parameters have already been quoted as
        valid URL strings.

        :param dict params: A dictionary of parameters.
        """
        query = urlparse(url).query
        if query:
            url = url.partition("?")[0]
            existing_params = {
                p[0]: p[-1] for p in [p.partition("=") for p in query.split("&")]
            }
            params.update(existing_params)
        query_params = []
        for k, v in params.items():
            if isinstance(v, list):
                for w in v:
                    if w is None:
                        raise ValueError("Query parameter {} cannot be None".format(k))
                    query_params.append("{}={}".format(k, w))
            else:
                if v is None:
                    raise ValueError("Query parameter {} cannot be None".format(k))
                query_params.append("{}={}".format(k, v))
        query = "?" + "&".join(query_params)
        url += query
        return url

def lookup_encoding(encoding):
    # type: (str) -> bool
    # including check for whether encoding is known taken from httpx
    try:
        codecs.lookup(encoding)
        return True
    except LookupError:
        return False

def parse_lines_from_text(text):
    # largely taken from httpx's LineDecoder code
    lines = []
    last_chunk_of_text = ""
    while text:
        text_length = len(text)
        for idx in range(text_length):
            curr_char = text[idx]
            next_char = None if idx == len(text) - 1 else text[idx + 1]
            if curr_char == "\n":
                lines.append(text[: idx + 1])
                text = text[idx + 1: ]
                break
            if curr_char == "\r" and next_char == "\n":
                # if it ends with \r\n, we only do \n
                lines.append(text[:idx] + "\n")
                text = text[idx + 2:]
                break
            if curr_char == "\r" and next_char is not None:
                # if it's \r then a normal character, we switch \r to \n
                lines.append(text[:idx] + "\n")
                text = text[idx + 1:]
                break
            if next_char is None:
                last_chunk_of_text += text
                text = ""
                break
    if last_chunk_of_text.endswith("\r"):
        # if ends with \r, we switch \r to \n
        lines.append(last_chunk_of_text[:-1] + "\n")
    elif last_chunk_of_text:
        lines.append(last_chunk_of_text)
    return lines
