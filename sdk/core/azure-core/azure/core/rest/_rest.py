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
import collections
from json import loads

from typing import TYPE_CHECKING

from azure.core.exceptions import HttpResponseError

from .._utils import _case_insensitive_dict

from ._helpers import (
    RequestNotReadError,
    ResponseClosedError,
    ResponseNotReadError,
    StreamConsumedError,
    lookup_encoding,
    SyncByteStream,
    RequestHelper,
    parse_lines_from_text,
)

if TYPE_CHECKING:
    from typing import (
        Iterable,
        Optional,
        Any,
        Iterator,
        Union,
        Dict,
    )
    from ._helpers import HeadersType
    ByteStream = Iterable[bytes]
    ContentType = Union[str, bytes, ByteStream]
    from azure.core.pipeline.transport._base import (
        HttpResponse as _PipelineTransportHttpResponse
    )



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

        self.url = url
        self.method = method
        self.headers = _case_insensitive_dict(kwargs.pop("headers", None))
        helper = RequestHelper()
        params = kwargs.pop("params", None)
        if params:
            self.url = helper.format_parameters(self.url, params)

        headers, self._content = helper.set_body(
            content=kwargs.pop("content", None),
            data=kwargs.pop("data", None),
            files=kwargs.pop("files", None),
            json=kwargs.pop("json", None),
        )
        self._read_content = False
        self._update_headers(_case_insensitive_dict(headers))

        # we just return content in the case of 'data' or 'files'
        if not isinstance(self._content, SyncByteStream):
            self._read_content = True
        if isinstance(self._content, helper.byte_stream):
            self.read()

        if kwargs:
            raise TypeError(
                "You have passed in kwargs '{}' that are not valid kwargs.".format(
                    "', '".join(list(kwargs.keys()))
                )
            )

    def _update_headers(self, default_headers):
        # type: (Dict[str, str]) -> None
        for name, value in default_headers.items():
            if name == "Transfer-Encoding" and "Content-Length" in self.headers:
                continue
            self.headers.setdefault(name, value)

    @property
    def content(self):
        # type: (...) -> Any
        """Gets the request content.
        """
        if not self._read_content:
            raise RequestNotReadError()
        return self._content

    def read(self):
        # type: (...) -> bytes
        if not self._read_content:
            if not isinstance(self._content, collections.Iterable):
                raise TypeError("read() should only be called on sync streams.")
            self._content = b"".join(self._content)
            self._read_content = True
        return self._content

    def __repr__(self):
        # type: (...) -> str
        return "<HttpRequest [{}], url: '{}'>".format(
            self.method, self.url
        )

    @property
    def _data(self):
        try:
            return self._content._data  # pylint: disable=protected-access
        except AttributeError:
            return self._content

    @property
    def _files(self):
        try:
            return self._content._files  # pylint: disable=protected-access
        except AttributeError:
            return None

    # def __deepcopy__(self, memo=None):
    #     return HttpRequest(
    #         self.method,
    #         self.url,
    #         _internal_request=self._internal_request.__deepcopy__(memo)
    #     )

class HttpResponse(object):  # pylint: disable=too-many-instance-attributes
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
        self.request = kwargs.pop("request")
        self.internal_response = kwargs.pop("internal_response")
        self.status_code = None
        self.headers = {}
        self.reason = None
        self.is_closed = False
        self.is_stream_consumed = False
        self._num_bytes_downloaded = 0
        self._content = None  # type: Optional[bytes]
        self._read_content = False
        self.content_type = None

    @property
    def url(self):
        # type: (...) -> str
        """Returns the URL that resulted in this response"""
        return self.request.url

    def _get_charset_encoding(self):
        content_type = self.headers.get("Content-Type")

        if not content_type:
            return None
        _, params = cgi.parse_header(content_type)
        encoding = params.get('charset') # -> utf-8
        if encoding is None or not lookup_encoding(encoding):
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
        return self.internal_response.text

    @property
    def num_bytes_downloaded(self):
        # type: (...) -> int
        """See how many bytes of your stream response have been downloaded"""
        return self._num_bytes_downloaded

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

    @property
    def content(self):
        # type: (...) -> bytes
        """Return the response's content in bytes."""
        if not self._read_content:
            raise ResponseNotReadError()
        return self._content


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
        if self.is_stream_consumed:
            raise StreamConsumedError()
        if self.is_closed:
            raise ResponseClosedError()

    def __enter__(self):
        # type: (...) -> HttpResponse
        return self

    def close(self):
        # type: (...) -> None
        self.is_closed = True
        self.internal_response.close()

    def __exit__(self, *args):
        # type: (...) -> None
        self.close()

    def read(self):
        # type: (...) -> bytes
        """
        Read the response's bytes.

        """
        if not self._read_content:
            self._content = b"".join(self.iter_bytes())
            self._read_content = True
        return self._content

    def iter_bytes(self, chunk_size=None):
        # type: (int) -> Iterator[bytes]
        """Iterate over the bytes in the response stream
        """

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
            lines = parse_lines_from_text(text)
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
