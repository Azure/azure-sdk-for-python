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
from __future__ import annotations
import codecs
import email.message
from json import dumps
import os
from typing import (
    Optional,
    Union,
    Mapping,
    Sequence,
    Tuple,
    IO,
    Any,
    Iterable,
    MutableMapping,
    AsyncIterable,
    cast,
    Dict,
)
import xml.etree.ElementTree as ET
from ..serialization import CoreJSONEncoder
from ..utils._utils import get_file_items


################################### TYPES SECTION #########################

binary_type = str
PrimitiveData = Optional[Union[str, int, float, bool]]

ParamsType = Mapping[str, Union[PrimitiveData, Sequence[PrimitiveData]]]

FileContent = Union[str, bytes, IO[str], IO[bytes]]
FileType = Union[
    # file (or bytes)
    FileContent,
    # (filename, file (or bytes))
    Tuple[Optional[str], FileContent],
    # (filename, file (or bytes), content_type)
    Tuple[Optional[str], FileContent, Optional[str]],
]

FilesType = Union[Mapping[str, FileType], Sequence[Tuple[str, FileType]]]

ContentTypeBase = Union[str, bytes, Iterable[bytes]]
ContentType = Union[str, bytes, Iterable[bytes], AsyncIterable[bytes]]

DataType = Optional[Union[bytes, Dict[str, Union[str, int]]]]

########################### HELPER SECTION #################################


def _verify_data_object(name, value):
    if not isinstance(name, str):
        raise TypeError("Invalid type for data name. Expected str, got {}: {}".format(type(name), name))
    if value is not None and not isinstance(value, (str, bytes, int, float)):
        raise TypeError("Invalid type for data value. Expected primitive type, got {}: {}".format(type(name), name))


def _format_data_helper(data: FileType) -> Union[Tuple[Optional[str], str], Tuple[Optional[str], FileContent, str]]:
    """Helper for _format_data.

    Format field data according to whether it is a stream or
    a string for a form-data request.

    :param data: The request field data.
    :type data: str or file-like object.
    :rtype: tuple[str, IO, str] or tuple[None, str]
    :return: A tuple of (data name, data IO, "application/octet-stream") or (None, data str)
    """
    content_type: Optional[str] = None
    filename: Optional[str] = None
    if isinstance(data, tuple):
        if len(data) == 2:
            # Filename and file bytes are included
            filename, file_bytes = cast(Tuple[Optional[str], FileContent], data)
        elif len(data) == 3:
            # Filename, file object, and content_type are included
            filename, file_bytes, content_type = cast(Tuple[Optional[str], FileContent, str], data)
        else:
            raise ValueError(
                "Unexpected data format. Expected file, or tuple of (filename, file_bytes) or "
                "(filename, file_bytes, content_type)."
            )
    else:
        # here we just get the file content
        if hasattr(data, "read"):
            data = cast(IO, data)
            try:
                if data.name[0] != "<" and data.name[-1] != ">":
                    filename = os.path.basename(data.name)
            except (AttributeError, TypeError):
                pass
            content_type = "application/octet-stream"
        file_bytes = data
    if content_type:
        return (filename, file_bytes, content_type)
    return (filename, cast(str, file_bytes))


def set_urlencoded_body(data, has_files):
    body = {}
    default_headers = {}
    for f, d in data.items():
        if not d:
            continue
        if isinstance(d, list):
            for item in d:
                _verify_data_object(f, item)
        else:
            _verify_data_object(f, d)
        body[f] = d
    if not has_files:
        # little hacky, but for files we don't send a content type with
        # boundary so requests / aiohttp etc deal with it
        default_headers["Content-Type"] = "application/x-www-form-urlencoded"
    return default_headers, body


def set_multipart_body(files: FilesType):
    formatted_files = [(f, _format_data_helper(d)) for f, d in get_file_items(files) if d is not None]
    return {}, dict(formatted_files) if isinstance(files, Mapping) else formatted_files


def set_xml_body(content):
    headers = {}
    bytes_content = ET.tostring(content, encoding="utf8")
    body = bytes_content.replace(b"encoding='utf8'", b"encoding='utf-8'")
    if body:
        headers["Content-Length"] = str(len(body))
    return headers, body


def set_content_body(
    content: Any,
) -> Tuple[MutableMapping[str, str], Optional[ContentTypeBase]]:
    headers: MutableMapping[str, str] = {}

    if isinstance(content, ET.Element):
        # XML body
        return set_xml_body(content)
    if isinstance(content, (str, bytes)):
        headers = {}
        body = content
        if isinstance(content, str):
            headers["Content-Type"] = "text/plain"
        if body:
            headers["Content-Length"] = str(len(body))
        return headers, body
    if any(hasattr(content, attr) for attr in ["read", "__iter__", "__aiter__"]):
        return headers, content
    raise TypeError(
        "Unexpected type for 'content': '{}'. ".format(type(content))
        + "We expect 'content' to either be str, bytes, a open file-like object or an iterable/asynciterable."
    )


def set_json_body(json: Any) -> Tuple[Dict[str, str], Any]:
    headers = {"Content-Type": "application/json"}
    if hasattr(json, "read"):
        content_headers, body = set_content_body(json)
        headers.update(content_headers)
    else:
        body = dumps(json, cls=CoreJSONEncoder)
        headers.update({"Content-Length": str(len(body))})
    return headers, body


def lookup_encoding(encoding: str) -> bool:
    # including check for whether encoding is known taken from httpx
    try:
        codecs.lookup(encoding)
        return True
    except LookupError:
        return False


def get_charset_encoding(response) -> Optional[str]:
    content_type = response.headers.get("Content-Type")

    if not content_type:
        return None
    # https://peps.python.org/pep-0594/#cgi
    m = email.message.Message()
    m["content-type"] = content_type
    encoding = cast(str, m.get_param("charset"))  # -> utf-8
    if encoding is None or not lookup_encoding(encoding):
        return None
    return encoding


def decode_to_text(encoding: Optional[str], content: bytes) -> str:
    if not content:
        return ""
    if encoding == "utf-8":
        encoding = "utf-8-sig"
    if encoding:
        return content.decode(encoding)
    return codecs.getincrementaldecoder("utf-8-sig")(errors="replace").decode(content)
