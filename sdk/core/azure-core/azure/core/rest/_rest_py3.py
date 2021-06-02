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
import asyncio
import cgi
import collections
import collections.abc
from json import loads
from typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
    Iterable, Iterator,
    Optional,
    Union,
)

from azure.core.exceptions import HttpResponseError
from azure.core.pipeline.transport import (
    HttpRequest as _PipelineTransportHttpRequest,
)

from azure.core.pipeline.transport._base import (
    _HttpResponseBase as _PipelineTransportHttpResponseBase
)

from ._helpers import (
    ParamsType,
    FilesType,
    HeadersType,
    _set_body,
    _lookup_encoding,
    _parse_lines_from_text,
    _set_content_length_header,
    _set_content_type_header,
)

ContentType = Union[str, bytes, Iterable[bytes], AsyncIterable[bytes]]

class _AsyncContextManager(collections.abc.Awaitable):

    def __init__(self, wrapped: collections.abc.Awaitable):
        super().__init__()
        self.wrapped = wrapped
        self.response = None

    def __await__(self):
        return self.wrapped.__await__()

    async def __aenter__(self):
        self.response = await self
        return self.response

    async def __aexit__(self, *args):
        await self.response.__aexit__(*args)

    async def close(self):
        await self.response.close()

def _add_async_body_checks(
    content, data, internal_request
):
    if data is not None and not isinstance(data, dict):
        content = data
        data = None
    if content is not None:
        if isinstance(content, collections.AsyncIterable):
            _set_content_length_header("Transfer-Encoding", "chunked", internal_request)
            _set_content_type_header("application/octet-stream", internal_request)

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
        json: Any = None,
        content: Optional[ContentType] = None,
        data: Optional[dict] = None,
        files: Optional[FilesType] = None,
        **kwargs
    ):
        self._internal_request = kwargs.pop("_internal_request", _PipelineTransportHttpRequest(
            method=method,
            url=url,
            headers=headers,
        ))

        if params:
            self._internal_request.format_parameters(params)

        _set_body(
            content=content,
            data=data,
            files=files,
            json=json,
            internal_request=self._internal_request
        )
        _add_async_body_checks(
            content=content,
            data=data,
            internal_request=self._internal_request
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
            self._internal_request.headers["Content-Length"] = str(len(self._internal_request.data))

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
        """Gets the request content.
        """
        return self._internal_request.data or self._internal_request.files

    def __repr__(self) -> str:
        return self._internal_request.__repr__()

    def __deepcopy__(self, memo=None) -> "HttpRequest":
        return HttpRequest(
            self.method,
            self.url,
            _internal_request=self._internal_request.__deepcopy__(memo)
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

    def __init__(
        self,
        *,
        request: HttpRequest,
        **kwargs
    ):
        self._internal_response = kwargs.pop("_internal_response")  # type: _PipelineTransportHttpResponseBase
        self._request = request
        self.is_closed = False
        self.is_stream_consumed = False
        self._num_bytes_downloaded = 0
        self._content: Optional[bytes] = None

    @property
    def status_code(self) -> int:
        """Returns the status code of the response"""
        # only reason it's optional in Pipeline Transport
        # HttpResponse is because we initialize it as None

        # throwing to satisfy mypy
        if self._internal_response.status_code is not None:
            return self._internal_response.status_code
        raise ValueError("status_code can not be None")

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
        # only reason it's optional in Pipeline Transport
        # HtttpResponse is because we initialize it as None

        # throwing to satisfy mypy
        if self._internal_response.reason is not None:
            return self._internal_response.reason
        raise ValueError("status_code can not be None")

    @property
    def url(self) -> str:
        """Returns the URL that resulted in this response"""
        return self._internal_response.request.url

    def _get_charset_encoding(self) -> Optional[str]:
        content_type = self.headers.get("Content-Type")

        if not content_type:
            return None
        _, params = cgi.parse_header(content_type)
        encoding = params.get('charset') # -> utf-8
        if encoding is None or not _lookup_encoding(encoding):
            return None
        return encoding

    @property
    def encoding(self) -> Optional[str]:
        """Returns the response encoding. By default, is specified
        by the response Content-Type header.
        """
        try:
            return self._encoding
        except AttributeError:
            return self._get_charset_encoding()

    @encoding.setter
    def encoding(self, value: str) -> None:
        """Sets the response encoding"""
        self._encoding = value

    @property
    def text(self) -> str:
        """Returns the response body as a string"""
        if not self._content:
            raise ResponseNotReadError()
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
        return loads(self.text)

    def raise_for_status(self) -> None:
        """Raises an HttpResponseError if the response has an error status code.

        If response is good, does nothing.
        """
        if self.status_code >= 400:
            raise HttpResponseError(response=self)

    @property
    def content(self) -> bytes:
        """Return the response's content in bytes."""
        if not self._content:
            raise ResponseNotReadError()
        return self._content

    def __repr__(self) -> str:
        content_type_str = (
            ", Content-Type: {}".format(self.content_type) if self.content_type else ""
        )
        return "<{}: {} {}{}>".format(
            type(self).__name__, self.status_code, self.reason, content_type_str
        )

    def _validate_streaming_access(self) -> None:
        if self.is_stream_consumed:
            raise StreamConsumedError()
        if self.is_closed:
            raise ResponseClosedError()

class HttpResponse(_HttpResponseBase):

    def __enter__(self) -> "HttpResponse":
        return self

    def close(self) -> None:
        self.is_closed = True
        self._internal_response.internal_response.close()

    def __exit__(self, *args) -> None:
        self.is_closed = True
        self._internal_response.internal_response.__exit__(*args)

    def read(self) -> bytes:
        """
        Read the response's bytes.

        """
        if not self._content:
            self._validate_streaming_access()
            self._content: bytes = (
                self._internal_response.body() or
                b"".join(self.iter_raw())
            )
            self._close_stream()
            return self._content
        return self._content

    def iter_bytes(self, chunk_size: int = None) -> Iterator[bytes]:
        """Iterate over the bytes in the response stream
        """
        if self._content:
            chunk_size = len(self._content) if chunk_size is None else chunk_size
            for i in range(0, len(self._content), chunk_size):
                yield self._content[i: i + chunk_size]

        else:
            for raw_bytes in self.iter_raw(chunk_size=chunk_size):
                yield raw_bytes

    def iter_text(self, chunk_size: int = None) -> Iterator[str]:
        """Iterate over the response text
        """
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

    def iter_raw(self, chunk_size: int = None) -> Iterator[bytes]:
        """Iterate over the raw response bytes
        """
        self._validate_streaming_access()
        stream_download = self._internal_response.stream_download(  # type: ignore
            None, chunk_size=chunk_size
        )
        for raw_bytes in stream_download:
            self._num_bytes_downloaded += len(raw_bytes)
            yield raw_bytes

        self._close_stream()


class AsyncHttpResponse(_HttpResponseBase):

    async def _close_stream(self) -> None:
        self.is_stream_consumed = True
        await self.close()

    async def read(self) -> bytes:
        """
        Read the response's bytes.

        """
        if not self._content:
            self._validate_streaming_access()
            await self._internal_response.load_body()  # type: ignore
            self._content = self._internal_response.body()
            await self._close_stream()
            return self._content
        return self._content

    async def iter_bytes(self, chunk_size: int = None) -> AsyncIterator[bytes]:
        """Iterate over the bytes in the response stream
        """
        if self._content:
            chunk_size = len(self._content) if chunk_size is None else chunk_size
            for i in range(0, len(self._content), chunk_size):
                yield self._content[i: i + chunk_size]
        else:
            async for raw_bytes in self.iter_raw(chunk_size=chunk_size):
                yield raw_bytes

    async def iter_text(self, chunk_size: int = None) -> AsyncIterator[str]:
        """Iterate over the response text
        """
        async for byte in self.iter_bytes(chunk_size):
            text = byte.decode(self.encoding or "utf-8")
            yield text

    async def iter_lines(self, chunk_size: int = None) -> AsyncIterator[str]:
        async for text in self.iter_text(chunk_size):
            lines = _parse_lines_from_text(text)
            for line in lines:
                yield line

    async def iter_raw(self, chunk_size: int = None) -> AsyncIterator[bytes]:
        """Iterate over the raw response bytes
        """
        self._validate_streaming_access()
        stream_download = self._internal_response.stream_download(  # type: ignore
            None, chunk_size=chunk_size
        )
        async for raw_bytes in stream_download:
            self._num_bytes_downloaded += len(raw_bytes)
            yield raw_bytes

        await self._close_stream()

    async def close(self) -> None:
        self.is_closed = True
        self._internal_response.internal_response.close()
        await asyncio.sleep(0)

    async def __aexit__(self, *args) -> None:
        self.is_closed = True
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
