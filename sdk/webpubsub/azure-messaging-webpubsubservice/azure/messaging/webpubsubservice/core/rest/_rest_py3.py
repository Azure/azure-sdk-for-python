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


import asyncio
import codecs
import json
from enum import Enum
import xml.etree.ElementTree as ET
from typing import (
    Any,
    AsyncIterable,
    IO,
    Iterable,
    Iterator,
    Optional,
    Union,
    Mapping,
    Sequence,
    Tuple,
    List,
)
from abc import abstractmethod

import cgi

from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import (
    HttpRequest as _PipelineTransportHttpRequest,
)

from azure.core.pipeline.transport._base import (
    _HttpResponseBase as _PipelineTransportHttpResponseBase,
)

from azure.core._pipeline_client import PipelineClient as _PipelineClient
from azure.core._pipeline_client_async import (
    AsyncPipelineClient as _AsyncPipelineClient,
)

################################### TYPES SECTION #########################

ByteStream = Union[Iterable[bytes], AsyncIterable[bytes]]
PrimitiveData = Optional[Union[str, int, float, bool]]


ParamsType = Union[
    Mapping[str, Union[PrimitiveData, Sequence[PrimitiveData]]],
    List[Tuple[str, PrimitiveData]],
]

HeadersType = Union[Mapping[str, str], Sequence[Tuple[str, str]]]

ContentType = Union[str, bytes, ByteStream]

FileContent = Union[str, bytes, IO[str], IO[bytes]]
FileType = Union[
    Tuple[Optional[str], FileContent],
]

FilesType = Union[Mapping[str, FileType], Sequence[Tuple[str, FileType]]]



class HttpVerbs(str, Enum):
    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    HEAD = "HEAD"
    PATCH = "PATCH"
    DELETE = "DELETE"
    MERGE = "MERGE"


########################### UTILS SECTION #################################


def _is_stream_or_str_bytes(content: Any) -> bool:
    return isinstance(content, (str, bytes)) or any(
        hasattr(content, attr) for attr in ["read", "__iter__", "__aiter__"]
    )


def _lookup_encoding(encoding: str) -> bool:
    # including check for whether encoding is known taken from httpx
    try:
        codecs.lookup(encoding)
        return True
    except LookupError:
        return False


def _set_content_length_header(
    header_name: str, header_value: str, internal_request: _PipelineTransportHttpRequest
) -> None:
    valid_methods = ["put", "post", "patch"]
    content_length_headers = ["Content-Length", "Transfer-Encoding"]
    if internal_request.method.lower() in valid_methods and not any(
        [c for c in content_length_headers if c in internal_request.headers]
    ):
        internal_request.headers[header_name] = header_value


def _set_content_type_header(
    header_value: str, internal_request: _PipelineTransportHttpRequest
) -> None:
    if not internal_request.headers.get("Content-Type"):
        internal_request.headers["Content-Type"] = header_value


def _set_content_body(
    content: ContentType, internal_request: _PipelineTransportHttpRequest
) -> None:
    headers = internal_request.headers
    content_type = headers.get("Content-Type")
    if _is_stream_or_str_bytes(content):
        # stream will be bytes / str, or iterator of bytes / str
        internal_request.set_streamed_data_body(content)
        if isinstance(content, str) and content:
            _set_content_length_header(
                "Content-Length", str(len(internal_request.data)), internal_request
            )
            _set_content_type_header("text/plain", internal_request)
        elif isinstance(content, bytes) and content:
            _set_content_length_header(
                "Content-Length", str(len(internal_request.data)), internal_request
            )
            _set_content_type_header("application/octet-stream", internal_request)
        elif isinstance(content, (Iterable, AsyncIterable)): # pylint: disable=isinstance-second-argument-not-valid-type
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


def _set_body(
    content: ContentType,
    data: dict,
    files: Any,
    json_body: Any,
    internal_request: _PipelineTransportHttpRequest,
) -> None:
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
        # boundary = binascii.hexlify(os.urandom(16)).decode(
        #    "ascii"
        #)  # got logic from httpx, thanks httpx!
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


class _StreamContextManagerBase:
    def __init__(
        self,
        client: Union[_PipelineClient, _AsyncPipelineClient],
        request: "HttpRequest",
        **kwargs
    ):
        """Used so we can treat stream requests and responses as a context manager.

        In Autorest, we only return a `StreamContextManager` if users pass in `stream_response` True

        Actually sends request when we enter the context manager, closes response when we exit.

        Heavily inspired from httpx, we want the same behavior for it to feel consistent for users
        """
        self.client = client
        self.request = request
        self.kwargs = kwargs

    @abstractmethod
    def close(self):
        ...


class _StreamContextManager(_StreamContextManagerBase):
    def __enter__(self) -> "HttpResponse":
        """Actually make the call only when we enter. For sync stream_response calls"""
        pipeline_transport_response = self.client._pipeline.run(
            self.request._internal_request, stream=True, **self.kwargs
        ).http_response
        self.response = HttpResponse( # pylint: disable=attribute-defined-outside-init
            request=self.request, _internal_response=pipeline_transport_response
        )
        return self.response

    def __exit__(self, *args):
        """Close our stream connection. For sync calls"""
        self.response.__exit__(*args)

    def close(self):
        self.response.close()


class _AsyncStreamContextManager(_StreamContextManagerBase):
    async def __aenter__(self) -> "AsyncHttpResponse":
        """Actually make the call only when we enter. For async stream_response calls."""
        if not isinstance(self.client, _AsyncPipelineClient):
            raise TypeError(
                "Only sync calls should enter here. If you mean to do a sync call, "
                "make sure to use 'with' instead."
            )
        pipeline_transport_response = (
            await self.client._pipeline.run(
                self.request._internal_request, stream=True, **self.kwargs
            )
        ).http_response
        self.response = AsyncHttpResponse( # pylint: disable=attribute-defined-outside-init
            request=self.request, _internal_response=pipeline_transport_response
        )
        return self.response

    async def __aexit__(self, *args):
        await self.response.__aexit__(*args)

    async def close(self): # pylint: disable=invalid-overridden-method
        await self.response.close()


################################## CLASSES ######################################


class HttpRequest:
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
    :keyword any json: A JSON serializable object. We handle JSON-serialization for your
     object, so use this for more complicated data structures than `data`.
    :keyword content: Content you want in your request body. Think of it as the kwarg you should input
     if your data doesn't fit into `json`, `data`, or `files`. Accepts a bytes type, or a generator
     that yields bytes.
    :paramtype content: str or bytes or iterable[bytes] or asynciterable[bytes]
    :keyword dict data: Form data you want in your request body. Use for form-encoded data, i.e.
     HTML forms.
    :keyword files: Files you want to in your request body. Use for uploading files with
     multipart encoding. Your input should be a mapping or sequence of file name to file content.
     Use the `data` kwarg in addition if you want to include non-file data files as part of your request.
    :paramtype files: mapping or sequence
    :ivar str url: The URL this request is against.
    :ivar str method: The method type of this request.
    :ivar headers: The HTTP headers you passed in to your request
    :vartype headers: mapping or sequence
    :ivar bytes content: The content passed in for the request
    """

    def __init__(
        self,
        method: str,
        url: str,
        *,
        params: Optional[ParamsType] = None,
        headers: Optional[HeadersType] = None,
        json: Any = None, # pylint: disable=redefined-outer-name
        content: Optional[ContentType] = None,
        data: Optional[dict] = None,
        files: Optional[FilesType] = None,
        **kwargs
    ):
        # type: (str, str, Any) -> None

        self._internal_request = kwargs.pop(
            "_internal_request",
            _PipelineTransportHttpRequest(
                method=method,
                url=url,
                headers=headers,
            ),
        )

        if params:
            self._internal_request.format_parameters(params)

        _set_body(
            content=content,
            data=data,
            files=files,
            json_body=json,
            internal_request=self._internal_request,
        )

        if kwargs:
            raise TypeError(
                "You have passed in kwargs '{}' that are not valid kwargs.".format(
                    "', '".join(list(kwargs.keys()))
                )
            )

    def _set_content_length_header(self) -> None:
        method_check = self._internal_request.method.lower() in ["put", "post", "patch"]
        content_length_unset = "Content-Length" not in self._internal_request.headers
        if method_check and content_length_unset:
            self._internal_request.headers["Content-Length"] = str(
                len(self._internal_request.data)
            )

    @property
    def url(self) -> str:
        return self._internal_request.url

    @url.setter
    def url(self, val: str) -> None:
        self._internal_request.url = val

    @property
    def method(self) -> str:
        return self._internal_request.method

    @property
    def headers(self) -> HeadersType:
        return self._internal_request.headers

    @property
    def content(self) -> Any:
        """Gets the request content."""
        return self._internal_request.data or self._internal_request.files

    def __repr__(self) -> str:
        return self._internal_request.__repr__()

    def __deepcopy__(self, memo=None) -> "HttpRequest":
        return HttpRequest(
            self.method,
            self.url,
            _internal_request=self._internal_request.__deepcopy__(memo),
        )


class _HttpResponseBase:
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
    :ivar bool is_closed: Whether the network connection has been closed yet
    :ivar bool is_stream_consumed: When getting a stream response, checks
     whether the stream has been fully consumed
    :ivar int num_bytes_downloaded: The number of bytes in your stream that
     have been downloaded
    """

    def __init__(self, *, request: HttpRequest, **kwargs):
        self._internal_response = kwargs.pop(
            "_internal_response"
        )  # type: _PipelineTransportHttpResponseBase
        self._request = request
        self.is_closed = False
        self.is_stream_consumed = False
        self._num_bytes_downloaded = 0

    @property
    def status_code(self) -> int:
        """Returns the status code of the response"""
        return self._internal_response.status_code

    @status_code.setter
    def status_code(self, val: int) -> None:
        """Set the status code of the response"""
        self._internal_response.status_code = val

    @property
    def headers(self) -> HeadersType:
        """Returns the response headers"""
        return self._internal_response.headers

    @property
    def reason(self) -> str:
        """Returns the reason phrase for the response"""
        return self._internal_response.reason

    @property
    def content(self) -> bytes:
        """Returns the response content in bytes"""
        raise NotImplementedError()

    @property
    def url(self) -> str:
        """Returns the URL that resulted in this response"""
        return self._internal_response.request.url

    @property
    def encoding(self) -> str:
        """Returns the response encoding. By default, is specified
        by the response Content-Type header.
        """

        try:
            return self._encoding
        except AttributeError:
            return self._get_charset_encoding()

    def _get_charset_encoding(self) -> str:
        content_type = self.headers.get("Content-Type")

        if not content_type:
            return None
        _, params = cgi.parse_header(content_type)
        encoding = params.get("charset")  # -> utf-8
        if encoding is None or not _lookup_encoding(encoding):
            return None
        return encoding

    @encoding.setter
    def encoding(self, value: str) -> None:
        # type: (str) -> None
        """Sets the response encoding"""
        self._encoding = value

    @property
    def text(self) -> str:
        """Returns the response body as a string"""
        _ = self.content  # access content to make sure we trigger if response not fully read in
        return self._internal_response.text(encoding=self.encoding)

    @property
    def request(self) -> HttpRequest:
        if self._request:
            return self._request
        raise RuntimeError(
            "You are trying to access the 'request', but there is no request associated with this HttpResponse"
        )

    @request.setter
    def request(self, val: HttpRequest) -> None:
        self._request = val

    @property
    def content_type(self) -> Optional[str]:
        """Content Type of the response"""
        return self._internal_response.content_type or self.headers.get("Content-Type")

    @property
    def num_bytes_downloaded(self) -> int:
        """See how many bytes of your stream response have been downloaded"""
        return self._num_bytes_downloaded

    def json(self) -> Any:
        """Returns the whole body as a json object.

        :return: The JSON deserialized response body
        :rtype: any
        :raises json.decoder.JSONDecodeError or ValueError (in python 2.7) if object is not JSON decodable:
        """
        return json.loads(self.text)

    def raise_for_status(self) -> None:
        """Raises an HttpResponseError if the response has an error status code.

        If response is good, does nothing.
        """
        if self.status_code >= 400:
            raise HttpResponseError(response=self)

    def __repr__(self) -> str:
        content_type_str = (
            ", Content-Type: {}".format(self.content_type) if self.content_type else ""
        )
        return "<{}: {} {}{}>".format(
            type(self).__name__, self.status_code, self.reason, content_type_str
        )

    def _validate_streaming_access(self) -> None:
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

    def close(self) -> None:
        self.is_closed = True
        self._internal_response.internal_response.close()

    def __exit__(self, *args) -> None:
        self._internal_response.internal_response.__exit__(*args)

    def read(self) -> bytes:
        """
        Read the response's bytes.

        """
        try:
            return self._content
        except AttributeError:
            self._validate_streaming_access()
            self._content = (self._internal_response.body() or # pylint: disable=attribute-defined-outside-init
                             b"".join(self.iter_raw()))
            self._close_stream()
            return self._content

    def iter_bytes(self, chunk_size: int = None) -> Iterator[bytes]:
        """Iterate over the bytes in the response stream"""
        try:
            chunk_size = len(self._content) if chunk_size is None else chunk_size
            for i in range(0, len(self._content), chunk_size):
                yield self._content[i : i + chunk_size]

        except AttributeError:
            for raw_bytes in self.iter_raw(chunk_size=chunk_size):
                yield raw_bytes

    def iter_text(self, chunk_size: int = None) -> Iterator[str]:
        """Iterate over the response text"""
        for byte in self.iter_bytes(chunk_size):
            text = byte.decode(self.encoding or "utf-8")
            yield text

    def iter_lines(self, chunk_size: int = None) -> Iterator[str]:
        for text in self.iter_text(chunk_size):
            lines = _parse_lines_from_text(text)
            for line in lines:
                yield line

    def _close_stream(self) -> None:
        self.is_stream_consumed = True
        self.close()

    def iter_raw(self, **_) -> Iterator[bytes]:
        """Iterate over the raw response bytes"""
        self._validate_streaming_access()
        stream_download = self._internal_response.stream_download(None)
        for raw_bytes in stream_download:
            self._num_bytes_downloaded += len(raw_bytes)
            yield raw_bytes

        self._close_stream()


class AsyncHttpResponse(_HttpResponseBase):
    @property
    def content(self) -> bytes:
        try:
            return self._content
        except AttributeError:
            raise ResponseNotReadError()

    async def _close_stream(self) -> None:
        self.is_stream_consumed = True
        await self.close()

    async def read(self) -> bytes:
        """
        Read the response's bytes.

        """
        try:
            return self._content
        except AttributeError:
            self._validate_streaming_access()
            await self._internal_response.load_body()
            self._content = self._internal_response._body # pylint: disable=protected-access,attribute-defined-outside-init
            await self._close_stream()
            return self._content

    async def iter_bytes(self, chunk_size: int = None) -> Iterator[bytes]:
        """Iterate over the bytes in the response stream"""
        try:
            chunk_size = len(self._content) if chunk_size is None else chunk_size
            for i in range(0, len(self._content), chunk_size):
                yield self._content[i : i + chunk_size]

        except AttributeError:
            async for raw_bytes in self.iter_raw(chunk_size=chunk_size):
                yield raw_bytes

    async def iter_text(self, chunk_size: int = None) -> Iterator[str]:
        """Iterate over the response text"""
        async for byte in self.iter_bytes(chunk_size):
            text = byte.decode(self.encoding or "utf-8")
            yield text

    async def iter_lines(self, chunk_size: int = None) -> Iterator[str]:
        async for text in self.iter_text(chunk_size):
            lines = _parse_lines_from_text(text)
            for line in lines:
                yield line

    async def iter_raw(self, **_) -> Iterator[bytes]:
        """Iterate over the raw response bytes"""
        self._validate_streaming_access()
        stream_download = self._internal_response.stream_download(None)
        async for raw_bytes in stream_download:
            self._num_bytes_downloaded += len(raw_bytes)
            yield raw_bytes

        await self._close_stream()

    async def close(self) -> None:
        self.is_closed = True
        self._internal_response.internal_response.close()
        await asyncio.sleep(0)

    async def __aexit__(self, *args) -> None:
        await self._internal_response.internal_response.__aexit__(*args)


########################### ERRORS SECTION #################################


class StreamConsumedError(Exception):
    def __init__(self) -> None:
        message = (
            "You are attempting to read or stream content that has already been streamed. "
            "You have likely already consumed this stream, so it can not be accessed anymore."
        )
        super().__init__(message)


class ResponseClosedError(Exception):
    def __init__(self) -> None:
        message = (
            "You can not try to read or stream this response's content, since the "
            "response has been closed."
        )
        super().__init__(message)


class ResponseNotReadError(Exception):
    def __init__(self) -> None:
        message = (
            "You have not read in the response's bytes yet. Call response.read() first."
        )
        super().__init__(message)
