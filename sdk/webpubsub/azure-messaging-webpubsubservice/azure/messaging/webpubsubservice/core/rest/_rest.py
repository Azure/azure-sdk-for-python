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

# pylint currently complains about typing.Union not being subscriptable
# pylint: disable=unsubscriptable-object

import codecs
import json
from enum import Enum
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING, Iterable

import cgi
import six

from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import (
    HttpRequest as _PipelineTransportHttpRequest,
)


if TYPE_CHECKING:
    from typing import (  # pylint: disable=ungrouped-imports
        Any,
        Optional,
        Union,
        Mapping,
        Sequence,
        Tuple,
        Iterator,
    )

    ByteStream = Iterable[bytes]

    HeadersType = Union[Mapping[str, str], Sequence[Tuple[str, str]]]
    ContentType = Union[str, bytes, ByteStream]
    from azure.core.pipeline.transport._base import (
        _HttpResponseBase as _PipelineTransportHttpResponseBase,
    )
    from azure.core._pipeline_client import PipelineClient as _PipelineClient


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
    if internal_request.method.lower() in valid_methods and not any(
        [c for c in content_length_headers if c in internal_request.headers]
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
            _set_content_length_header(
                "Content-Length", str(len(internal_request.data)), internal_request
            )
            if isinstance(content, six.string_types):
                _set_content_type_header("text/plain", internal_request)
            else:
                _set_content_type_header("application/octet-stream", internal_request)
        elif isinstance( # pylint: disable=isinstance-second-argument-not-valid-type
            content, Iterable
        ):
            # _set_content_length_header("Transfer-Encoding", "chunked", internal_request)
            _set_content_type_header("application/octet-stream", internal_request)
    elif isinstance(content, ET.Element):
        # XML body
        internal_request.set_xml_body(content)
        _set_content_type_header("application/xml", internal_request)
        _set_content_length_header(
            "Content-Length", str(len(internal_request.data)), internal_request
        )
    elif content_type and content_type.startswith("text/"):
        # Text body
        internal_request.set_text_body(content)
        _set_content_length_header(
            "Content-Length", str(len(internal_request.data)), internal_request
        )
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
        # boundary = binascii.hexlify(os.urandom(16)).decode("ascii")  # got logic from httpx, thanks httpx!
        # _set_content_type_header("multipart/form-data; boundary={}".format(boundary), internal_request)
    elif data:
        _set_content_type_header("application/x-www-form-urlencoded", internal_request)
        internal_request.set_formdata_body(data)
        # need to set twice because Content-Type is being popped in set_formdata_body
        # don't want to risk changing pipeline.transport, so doing twice here
        _set_content_type_header("application/x-www-form-urlencoded", internal_request)


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
                text = text[idx + 1 :]
                break
            if curr_char == "\r" and next_char == "\n":
                # if it ends with \r\n, we only do \n
                lines.append(text[:idx] + "\n")
                text = text[idx + 2 :]
                break
            if curr_char == "\r" and next_char is not None:
                # if it's \r then a normal character, we switch \r to \n
                lines.append(text[:idx] + "\n")
                text = text[idx + 1 :]
                break
            if next_char is None:
                text = ""
                last_chunk_of_text += text
                break
    if last_chunk_of_text.endswith("\r"):
        # if ends with \r, we switch \r to \n
        lines.append(last_chunk_of_text[:-1] + "\n")
    elif last_chunk_of_text:
        lines.append(last_chunk_of_text)
    return lines


################################## CLASSES ######################################
class _StreamContextManager(object):
    def __init__(self, client, request, **kwargs):
        # type: (_PipelineClient, HttpRequest, Any) -> None
        self.client = client
        self.request = request
        self.kwargs = kwargs

    def __enter__(self):
        # type: (...) -> HttpResponse
        """Actually make the call only when we enter. For sync stream_response calls"""
        pipeline_transport_response = self.client._pipeline.run(
            self.request._internal_request, stream=True, **self.kwargs
        ).http_response
        self.response = HttpResponse(  # pylint: disable=attribute-defined-outside-init
            request=self.request, _internal_response=pipeline_transport_response
        )
        return self.response

    def __exit__(self, *args):
        """Close our stream connection. For sync calls"""
        self.response.__exit__(*args)

    def close(self):
        self.response.close()


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

        self._internal_request = kwargs.pop(
            "_internal_request",
            _PipelineTransportHttpRequest(
                method=method,
                url=url,
                headers=kwargs.pop("headers", None),
            ),
        )
        params = kwargs.pop("params", None)

        if params:
            self._internal_request.format_parameters(params)

        _set_body(
            content=content,
            data=data,
            files=files,
            json_body=json_body,
            internal_request=self._internal_request,
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
            self._internal_request.headers["Content-Length"] = str(
                len(self._internal_request.data)
            )

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
        """Gets the request content."""
        return self._internal_request.data or self._internal_request.files

    def __repr__(self):
        return self._internal_request.__repr__()

    def __deepcopy__(self, memo=None):
        return HttpRequest(
            self.method,
            self.url,
            _internal_request=self._internal_request.__deepcopy__(memo),
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
    :ivar bool is_error: Whether this response is an error.
    """

    def __init__(self, **kwargs):
        # type: (Any) -> None
        self._internal_response = kwargs.pop(
            "_internal_response"
        )  # type: _PipelineTransportHttpResponseBase
        self._request = kwargs.pop("request")
        self.is_closed = False
        self.is_stream_consumed = False
        self._num_bytes_downloaded = 0

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
        encoding = params.get("charset")  # -> utf-8
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
        _ = (
            self.content
        )  # access content to make sure we trigger if response not fully read in
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

    @property
    def num_bytes_downloaded(self):
        # type: (...) -> int
        """See how many bytes of your stream response have been downloaded"""
        return self._num_bytes_downloaded

    @property
    def is_error(self):
        # type: (...) -> bool
        """See whether your HttpResponse is an error.

        Use .raise_for_status() if you want to raise if this response is an error.
        """
        return self.status_code < 400

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
        if self.status_code >= 400:
            raise HttpResponseError(response=self)

    def __repr__(self):
        # type: (...) -> str
        content_type_str = (
            ", Content-Type: {}".format(self.content_type) if self.content_type else ""
        )
        return "<{}: {} {}{}>".format(
            type(self).__name__, self.status_code, self.reason, content_type_str
        )

    def _validate_streaming_access(self):
        # type: (...) -> None
        if self.is_closed:
            raise ResponseClosedError()
        if self.is_stream_consumed:
            raise StreamConsumedError()


class HttpResponse(_HttpResponseBase):
    @property
    def content(self):
        # type: (...) -> bytes
        try:
            return self._content
        except AttributeError:
            raise ResponseNotReadError()

    def close(self):
        # type: (...) -> None
        self.is_closed = True
        self._internal_response.internal_response.close()

    def __exit__(self, *args):
        # type: (...) -> None
        self._internal_response.internal_response.__exit__(*args)

    def read(self):
        # type: (...) -> bytes
        """
        Read the response's bytes.

        """
        try:
            return self._content
        except AttributeError:
            self._validate_streaming_access()
            self._content = (  # pylint: disable=attribute-defined-outside-init
                self._internal_response.body() or b"".join(self.iter_raw())
            )
            self._close_stream()
            return self._content

    def iter_bytes(self, chunk_size=None):
        # type: (int) -> Iterator[bytes]
        """Iterate over the bytes in the response stream"""
        try:
            chunk_size = len(self._content) if chunk_size is None else chunk_size
            for i in range(0, len(self._content), chunk_size):
                yield self._content[i : i + chunk_size]

        except AttributeError:
            for raw_bytes in self.iter_raw(chunk_size=chunk_size):
                yield raw_bytes

    def iter_text(self, chunk_size=None):
        # type: (int) -> Iterator[str]
        """Iterate over the response text"""
        for byte in self.iter_bytes(chunk_size):
            text = byte.decode(self.encoding or "utf-8")
            yield text

    def iter_lines(self, chunk_size=None):
        # type: (int) -> Iterator[str]
        for text in self.iter_text(chunk_size):
            lines = _parse_lines_from_text(text)
            for line in lines:
                yield line

    def _close_stream(self):
        # type: (...) -> None
        self.is_stream_consumed = True
        self.close()

    def iter_raw(self, **_):
        # type: (int) -> Iterator[bytes]
        """Iterate over the raw response bytes"""
        self._validate_streaming_access()
        stream_download = self._internal_response.stream_download(None)
        for raw_bytes in stream_download:
            self._num_bytes_downloaded += len(raw_bytes)
            yield raw_bytes

        self._close_stream()


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
