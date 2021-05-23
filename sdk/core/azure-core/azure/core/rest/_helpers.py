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
import collections
import codecs
from enum import Enum
from typing import (
    Optional,
    Union,
    Mapping,
    Sequence,
    List,
    Tuple,
    IO,
    cast,
)
import xml.etree.ElementTree as ET
import six
from azure.core.pipeline.transport import (
    HttpRequest as _PipelineTransportHttpRequest,
)

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

class HttpVerbs(str, Enum):
    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    HEAD = "HEAD"
    PATCH = "PATCH"
    DELETE = "DELETE"
    MERGE = "MERGE"

########################### UTILS SECTION #################################

def _is_stream_or_str_bytes(content):
    return isinstance(content, (str, bytes)) or any(
        hasattr(content, attr) for attr in ["read", "__iter__", "__aiter__"]
    )

def _lookup_encoding(encoding):
    # type: (str) -> bool
    # including check for whether encoding is known taken from httpx
    try:
        codecs.lookup(encoding)
        return True
    except LookupError:
        return False

def _set_content_length_header(header_name, header_value, internal_request):
    # type: (str, str, _PipelineTransportHttpRequest) -> None
    valid_methods = ["put", "post", "patch"]
    content_length_headers = ["Content-Length", "Transfer-Encoding"]
    if (
        internal_request.method.lower() in valid_methods and
        not any([c for c in content_length_headers if c in internal_request.headers])
    ):
        internal_request.headers[header_name] = header_value

def _set_content_type_header(header_value, internal_request):
    # type: (str, _PipelineTransportHttpRequest) -> None
    if not internal_request.headers.get("Content-Type"):
        internal_request.headers["Content-Type"] = header_value

def _set_content_body(content, internal_request):
    headers = internal_request.headers
    content_type = headers.get("Content-Type")
    if _is_stream_or_str_bytes(content):
        # stream will be bytes / str, or iterator of bytes / str
        internal_request.set_streamed_data_body(content)
        if isinstance(content, (str, bytes)) and content:
            _set_content_length_header(
                "Content-Length",
                str(len(cast(str, internal_request.data))),
                internal_request
            )
            if isinstance(content, six.string_types):
                _set_content_type_header("text/plain", internal_request)
            else:
                _set_content_type_header("application/octet-stream", internal_request)
        elif isinstance(content, collections.Iterable):
            _set_content_length_header("Transfer-Encoding", "chunked", internal_request)
            _set_content_type_header("application/octet-stream", internal_request)
    elif isinstance(content, ET.Element):
        # XML body
        internal_request.set_xml_body(content)
        _set_content_type_header("application/xml", internal_request)
        _set_content_length_header(
            "Content-Length",
            str(len(cast(ET.Element, internal_request.data))),
            internal_request
        )
    elif content_type and content_type.startswith("text/"):
        # Text body
        internal_request.set_text_body(content)
        _set_content_length_header(
            "Content-Length",
            str(len(cast(str, internal_request.data))),
            internal_request
        )
    else:
        # Other body
        internal_request.data = content
    internal_request.headers = headers

def _verify_and_data_object(key, value):
    if not isinstance(key, str):
        raise TypeError(
            f"Invalid type for data key. Expected str, got {type(key)}: {key!r}"
        )
    if not isinstance(value, (str, bytes)):
        raise TypeError(
            f"Invalid type for data value. Expected str or bytes, got {type(value)}: {value!r}"
    )

def _set_body(content, data, files, json, internal_request):
    if data is not None and not isinstance(data, dict):
        content = data
        data = None
    if content is not None:
        _set_content_body(content, internal_request)
    elif json is not None:
        internal_request.set_json_body(json)
        _set_content_type_header("application/json", internal_request)
    elif files or data:
        if data:
            internal_request.data = {f: d for f, d in data.items() if d is not None}
        if files:
            internal_request.files = {
                f: internal_request._format_data(d)  # pylint: disable=protected-access
                for f, d in files.items() if d is not None
            }
        if data and not files:
            _set_content_type_header("application/x-www-form-urlencoded", internal_request)
        if data and files:
            for f, d in internal_request.data.items():
                if isinstance(d, list):
                    for item in d:
                        _verify_and_data_object(f, item)
                else:
                    _verify_and_data_object(f, d)

def _parse_lines_from_text(text):
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
