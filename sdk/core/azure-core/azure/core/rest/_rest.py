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

__all__ = [
    "HttpRequest",
    "HttpResponse",
]
import sys
import six
import os
import binascii
import codecs
import cgi
import json
from enum import Enum
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING, Iterable

from azure.core.pipeline.transport import (
    HttpRequest as _PipelineTransportHttpRequest,
)

if TYPE_CHECKING:
    from typing import (
        Any, Optional, Union, Mapping, Sequence, Tuple,
    )
    ByteStream = Iterable[bytes]

    HeadersType = Union[
        Mapping[str, str],
        Sequence[Tuple[str, str]]
    ]
    ContentType = Union[str, bytes, ByteStream]
    from azure.core.pipeline.transport._base import (
        _HttpResponseBase as _PipelineTransportHttpResponseBase
    )

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
    # type: (ContentType, _PipelineTransportHttpRequest) -> None
    headers = internal_request.headers
    content_type = headers.get("Content-Type")
    if _is_stream_or_str_bytes(content):
        # stream will be bytes / str, or iterator of bytes / str
        internal_request.set_streamed_data_body(content)
        if isinstance(content, (str, bytes)) and content:
            _set_content_length_header("Content-Length", str(len(internal_request.data)), internal_request)
            if isinstance(content, six.string_types):
                _set_content_type_header("text/plain", internal_request)
            else:
                _set_content_type_header("application/octet-stream", internal_request)
        elif isinstance(content, Iterable):
            _set_content_length_header("Transfer-Encoding", "chunked", internal_request)
            _set_content_type_header("application/octet-stream", internal_request)
    elif isinstance(content, ET.Element):
        # XML body
        internal_request.set_xml_body(content)
        _set_content_type_header("application/xml", internal_request)
        _set_content_length_header("Content-Length", str(len(internal_request.data)), internal_request)
    elif content_type and content_type.startswith("text/"):
        # Text body
        internal_request.set_text_body(content)
        _set_content_length_header("Content-Length", str(len(internal_request.data)), internal_request)
    else:
        # Other body
        internal_request.data = content
    internal_request.headers = headers

def _set_body(content, data, files, json_body, internal_request):
    # type: (ContentType, dict, Any, Any, _PipelineTransportHttpRequest) -> None
    if data is not None and not isinstance(data, dict):
        content = data
        data = None
    if content is not None:
        _set_content_body(content, internal_request)
    elif json_body is not None:
        internal_request.set_json_body(json_body)
        _set_content_type_header("application/json", internal_request)
    elif files is not None:
        internal_request.set_formdata_body(files)
        # if you don't supply your content type, we'll create a boundary for you with multipart/form-data
        boundary = binascii.hexlify(os.urandom(16)).decode("ascii")  # got logic from httpx, thanks httpx!
        # _set_content_type_header("multipart/form-data; boundary={}".format(boundary), internal_request)
    elif data:
        _set_content_type_header("application/x-www-form-urlencoded", internal_request)
        internal_request.set_formdata_body(data)
        # need to set twice because Content-Type is being popped in set_formdata_body
        # don't want to risk changing pipeline.transport, so doing twice here
        _set_content_type_header("application/x-www-form-urlencoded", internal_request)


################################## CLASSES ######################################

class HttpRequest(object):
    """Represents an HTTP request.

    :param method: HTTP method (GET, HEAD, etc.)
    :type method: str or ~azure.core.protocol.HttpVerbs
    :param str url: The url for your request
    :keyword params: Query parameters to be mapped into your URL. Your input
     should be a mapping or sequence of query name to query value(s).
    :paramtype params: mapping or sequence
    :keyword headers: HTTP headers you want in your request. Your input should
     be a mapping or sequence of header name to header value.
    :paramtype headers: mapping or sequence
    :keyword dict data: Form data you want in your request body. Use for form-encoded data, i.e.
     HTML forms.
    :keyword any json: A JSON serializable object. We handle JSON-serialization for your
     object, so use this for more complicated data structures than `data`.
    :keyword files: Files you want to in your request body. Use for uploading files with
     multipart encoding. Your input should be a mapping or sequence of file name to file content.
     Use the `data` kwarg in addition if you want to include non-file data files as part of your request.
    :paramtype files: mapping or sequence
    :keyword content: Content you want in your request body. Think of it as the kwarg you should input
     if your data doesn't fit into `json`, `data`, or `files`. Accepts a bytes type, or a generator
     that yields bytes.
    :paramtype content: str or bytes or iterable[bytes] or asynciterable[bytes]
    :ivar str url: The URL this request is against.
    :ivar str method: The method type of this request.
    :ivar headers: The HTTP headers you passed in to your request
    :vartype headers: mapping or sequence
    :ivar bytes content: The content passed in for the request
    """

    def __init__(self, method, url, **kwargs):
        # type: (str, str, Any) -> None

        data = kwargs.pop("data", None)
        content = kwargs.pop("content", None)
        json_body = kwargs.pop("json", None)
        files = kwargs.pop("files", None)

        self._internal_request = kwargs.pop("_internal_request", _PipelineTransportHttpRequest(
            method=method,
            url=url,
            headers=kwargs.pop("headers", None),
        ))
        params = kwargs.pop("params", None)

        if params:
            self._internal_request.format_parameters(params)

        _set_body(
            content=content,
            data=data,
            files=files,
            json_body=json_body,
            internal_request=self._internal_request
        )

        if kwargs:
            raise TypeError(
                "You have passed in kwargs '{}' that are not valid kwargs.".format(
                    "', '".join(list(kwargs.keys()))
                )
            )

    def _set_content_length_header(self):
        method_check = self._internal_request.method.lower() in ["put", "post", "patch"]
        content_length_unset = "Content-Length" not in self._internal_request.headers
        if method_check and content_length_unset:
            self._internal_request.headers["Content-Length"] = str(len(self._internal_request.data))

    @property
    def url(self):
        # type: (...) -> str
        return self._internal_request.url

    @url.setter
    def url(self, val):
        # type: (str) -> None
        self._internal_request.url = val

    @property
    def method(self):
        # type: (...) -> str
        return self._internal_request.method

    @property
    def headers(self):
        # type: (...) -> HeadersType
        return self._internal_request.headers

    @property
    def content(self):
        # type: (...) -> Any
        """Gets the request content.
        """
        return self._internal_request.data or self._internal_request.files

    def __repr__(self):
        return self._internal_request.__repr__()

    def __deepcopy__(self, memo=None):
        return HttpRequest(
            self.method,
            self.url,
            _internal_request=self._internal_request.__deepcopy__(memo)
        )

class _HttpResponseBase(object):
    """Base class for HttpResponse and AsyncHttpResponse.

    :keyword request: The request that resulted in this response.
    :paramtype request: ~azure.core.rest.HttpRequest
    :ivar int status_code: The status code of this response
    :ivar headers: The response headers
    :vartype headers: dict[str, any]
    :ivar str reason: The reason phrase for this response
    :ivar bytes content: The response content in bytes
    :ivar str url: The URL that resulted in this response
    :ivar str encoding: The response encoding. Is settable, by default
     is the response Content-Type header
    :ivar str text: The response body as a string.
    :ivar request: The request that resulted in this response.
    :vartype request: ~azure.core.rest.HttpRequest
    :ivar str content_type: The content type of the response
    """

    def __init__(self, **kwargs):
        # type: (int, Any) -> None
        self._internal_response = kwargs.pop("_internal_response")  # type: _PipelineTransportHttpResponseBase
        self._request = kwargs.pop("request")

    @property
    def status_code(self):
        # type: (...) -> int
        """Returns the status code of the response"""
        return self._internal_response.status_code

    @status_code.setter
    def status_code(self, val):
        # type: (int) -> None
        """Set the status code of the response"""
        self._internal_response.status_code = val

    @property
    def headers(self):
        # type: (...) -> HeadersType
        """Returns the response headers"""
        return self._internal_response.headers

    @property
    def reason(self):
        # type: (...) -> str
        """Returns the reason phrase for the response"""
        return self._internal_response.reason

    @property
    def content(self):
        # type: (...) -> bytes
        """Returns the response content in bytes"""
        raise NotImplementedError()

    @property
    def url(self):
        # type: (...) -> str
        """Returns the URL that resulted in this response"""
        return self._internal_response.request.url

    @property
    def encoding(self):
        # type: (...) -> Optional[str]
        """Returns the response encoding. By default, is specified
        by the response Content-Type header.
        """

        try:
            return self._encoding
        except AttributeError:
            return self._get_charset_encoding()

    def _get_charset_encoding(self):
        content_type = self.headers.get("Content-Type")

        if not content_type:
            return None
        _, params = cgi.parse_header(content_type)
        encoding = params.get('charset') # -> utf-8
        if encoding is None or not _lookup_encoding(encoding):
            return None
        return encoding

    @encoding.setter
    def encoding(self, value):
        # type: (str) -> None
        """Sets the response encoding"""
        self._encoding = value

    @property
    def text(self):
        # type: (...) -> str
        """Returns the response body as a string"""
        return self._internal_response.text(encoding=self.encoding)

    @property
    def request(self):
        # type: (...) -> HttpRequest
        if self._request:
            return self._request
        raise RuntimeError(
            "You are trying to access the 'request', but there is no request associated with this HttpResponse"
        )

    @request.setter
    def request(self, val):
        # type: (HttpRequest) -> None
        self._request = val

    @property
    def content_type(self):
        # type: (...) -> Optional[str]
        """Content Type of the response"""
        return self._internal_response.content_type or self.headers.get("Content-Type")

    def json(self):
        # type: (...) -> Any
        """Returns the whole body as a json object.

        :return: The JSON deserialized response body
        :rtype: any
        :raises json.decoder.JSONDecodeError or ValueError (in python 2.7) if object is not JSON decodable:
        """
        return json.loads(self.text)

    def raise_for_status(self):
        # type: (...) -> None
        """Raises an HttpResponseError if the response has an error status code.

        If response is good, does nothing.
        """
        return self._internal_response.raise_for_status()

    def __repr__(self):
        # type: (...) -> str
        content_type_str = (
            ", Content-Type: {}".format(self.content_type) if self.content_type else ""
        )
        return "<{}: {} {}{}>".format(
            type(self).__name__, self.status_code, self.reason, content_type_str
        )

    def stream_download(self, pipeline=None):
        """Generator for streaming request body data.

        :rtype: iterator[bytes]
        """

class HttpResponse(_HttpResponseBase):

    @property
    def content(self):
        # type: (...) -> bytes
        return self._internal_response.body()

    def stream_download(self, pipeline=None):
        """Generator for streaming request body data.

        Will remove once we have stream handling worked out.

        :rtype: iterator[bytes]
        """
        return self._internal_response.stream_download(pipeline=pipeline)
