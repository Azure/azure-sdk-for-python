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
import cgi
from json import loads

from typing import TYPE_CHECKING

from azure.core.pipeline.transport import (
    HttpRequest as _PipelineTransportHttpRequest,
)
from azure.core.exceptions import HttpResponseError

from ._helpers import (
    _set_body,
    _lookup_encoding,
    _parse_lines_from_text,
)

if TYPE_CHECKING:
    from typing import (
        Iterable,
        Optional,
        Any,
        Iterator,
        Union,
    )
    from ._helpers import HeadersType
    ByteStream = Iterable[bytes]
    ContentType = Union[str, bytes, ByteStream]
    from azure.core.pipeline.transport._base import (
        HttpResponse as _PipelineTransportHttpResponse
    )
    from azure.core.pipeline import Pipeline



################################## CLASSES ######################################
class _StreamContextManager(object):
    def __init__(self, pipeline, request, **kwargs):
        # type: (Pipeline, HttpRequest, Any) -> None
        """Used so we can treat stream requests and responses as a context manager.
        In Autorest, we only return a `StreamContextManager` if users pass in `stream_response` True
        Actually sends request when we enter the context manager, closes response when we exit.
        Heavily inspired from httpx, we want the same behavior for it to feel consistent for users
        """
        self.pipeline = pipeline
        self.request = request
        self.kwargs = kwargs
        self.response = None  # type: Optional[HttpResponse]

    def __enter__(self):
        # type: (...) -> HttpResponse
        """Actually make the call only when we enter. For sync stream_response calls"""
        pipeline_transport_response = self.pipeline.run(
            self.request._internal_request,
            stream=True,
            **self.kwargs
        ).http_response
        self.response = HttpResponse(
            request=self.request,
            _internal_response=pipeline_transport_response
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
        json = kwargs.pop("json", None)
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
            json=json,
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

class HttpResponse(object):
    """Class for HttpResponse.

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
        self._internal_response = kwargs.pop("_internal_response")  # type: _PipelineTransportHttpResponse
        self._request = kwargs.pop("request")
        self.is_closed = False
        self.is_stream_consumed = False
        self._num_bytes_downloaded = 0
        self._content = None  # type: Optional[bytes]

    @property
    def status_code(self):
        # type: (...) -> int
        """Returns the status code of the response"""
        if self._internal_response.status_code is not None:
            return self._internal_response.status_code
        raise ValueError("status code can not be None")

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
        if self._internal_response.reason is not None:
            return self._internal_response.reason
        raise ValueError("reason can not be None")


    @property
    def content(self):
        # type: (...) -> bytes
        """Returns the response content in bytes"""
        if not self._content:
            raise ResponseNotReadError()
        return self._content


    @property
    def url(self):
        # type: (...) -> str
        """Returns the URL that resulted in this response"""
        return self._internal_response.request.url

    def _get_charset_encoding(self):
        content_type = self.headers.get("Content-Type")

        if not content_type:
            return None
        _, params = cgi.parse_header(content_type)
        encoding = params.get('charset') # -> utf-8
        if encoding is None or not _lookup_encoding(encoding):
            return None
        return encoding

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

    @encoding.setter
    def encoding(self, value):
        # type: (str) -> None
        """Sets the response encoding"""
        self._encoding = value

    @property
    def text(self):
        # type: (...) -> str
        """Returns the response body as a string"""
        if not self._content:
            raise ResponseNotReadError()
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
        return loads(self.text)

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

    def close(self):
        # type: (...) -> None
        self.is_closed = True
        self._internal_response.internal_response.close()

    def __exit__(self, *args):
        # type: (...) -> None
        self.close()

    def read(self):
        # type: (...) -> bytes
        """
        Read the response's bytes.

        """
        if not self._content:
            self._validate_streaming_access()
            self._content = (
                self._internal_response.body() or
                b"".join(self.iter_raw())
            )
            self._close_stream()
            return self._content
        return self._content

    def iter_bytes(self, chunk_size=None):
        # type: (int) -> Iterator[bytes]
        """Iterate over the bytes in the response stream
        """
        if self._content:
            chunk_size = len(self._content) if chunk_size is None else chunk_size
            for i in range(0, len(self._content), chunk_size):
                yield self._content[i: i + chunk_size]
        else:
            for raw_bytes in self.iter_raw(chunk_size=chunk_size):
                yield raw_bytes

    def iter_text(self, chunk_size=None):
        # type: (int) -> Iterator[str]
        """Iterate over the response text
        """
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

    def iter_raw(self, chunk_size=None):
        # type: (int) -> Iterator[bytes]
        """Iterate over the raw response bytes
        """
        self._validate_streaming_access()
        stream_download = self._internal_response.stream_download(None, chunk_size=chunk_size)
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
