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
from json import loads
from typing import cast, TYPE_CHECKING
from ._helpers import (
    get_charset_encoding,
    decode_to_text,
)
from ..exceptions import HttpResponseError, ResponseNotReadError, StreamConsumedError, StreamClosedError
try:
    from ._rest_py3 import (
        _HttpResponseBase,
        HttpResponse as _HttpResponse,
        HttpRequest as _HttpRequest
    )
except (SyntaxError, ImportError):
    from ._rest import (  # type: ignore
        _HttpResponseBase,
        HttpResponse as _HttpResponse,
        HttpRequest as _HttpRequest
    )

if TYPE_CHECKING:
    from typing import Any, Optional, Iterator, MutableMapping, Callable


class _HttpResponseBaseImpl(_HttpResponseBase):  # pylint: disable=too-many-instance-attributes
    """Base Implementation class for azure.core.rest.HttpRespone and azure.core.rest.AsyncHttpResponse

    Since the rest responses are abstract base classes, we need to implement them for each of our transport
    responses. This is the base implementation class shared by HttpResponseImpl and AsyncHttpResponseImpl.
    The transport responses will be built on top of HttpResponseImpl and AsyncHttpResponseImpl

    :keyword request: The request that led to the response
    :type request: ~azure.core.rest.HttpRequest
    :keyword any internal_response: The response we get directly from the transport. For example, for our requests
     transport, this will be a requests.Response.
    :keyword optional[int] block_size: The block size we are using in our transport
    :keyword int status_code: The status code of the response
    :keyword str reason: The HTTP reason
    :keyword str content_type: The content type of the response
    :keyword MutableMapping[str, str] headers: The response headers
    :keyword Callable stream_download_generator: The stream download generator that we use to stream the response.
    """

    def __init__(self, **kwargs):
        # type: (Any) -> None
        super(_HttpResponseBaseImpl, self).__init__()
        self._request = kwargs.pop("request")
        self._internal_response = kwargs.pop("internal_response")
        self._block_size = kwargs.pop("block_size", None) or 4096  # type: int
        self._status_code = kwargs.pop("status_code")  # type: int
        self._reason = kwargs.pop("reason")  # type: str
        self._content_type = kwargs.pop("content_type")  # type: str
        self._headers = kwargs.pop("headers")  # type: MutableMapping[str, str]
        self._stream_download_generator = kwargs.pop("stream_download_generator")  # type: Callable
        self._is_closed = False
        self._is_stream_consumed = False
        self._json = None  # this is filled in ContentDecodePolicy, when we deserialize
        self._content = None  # type: Optional[bytes]
        self._text = None  # type: Optional[str]

    @property
    def request(self):
        # type: (...) -> _HttpRequest
        """The request that resulted in this response.

        :rtype: ~azure.core.rest.HttpRequest
        """
        return self._request

    @property
    def url(self):
        # type: (...) -> str
        """The URL that resulted in this response.

        :rtype: str
        """
        return self.request.url

    @property
    def is_closed(self):
        # type: (...) -> bool
        """Whether the network connection has been closed yet.

        :rtype: bool
        """
        return self._is_closed

    @property
    def is_stream_consumed(self):
        # type: (...) -> bool
        """Whether the stream has been fully consumed"""
        return self._is_stream_consumed

    @property
    def status_code(self):
        # type: (...) -> int
        """The status code of this response.

        :rtype: int
        """
        return self._status_code

    @property
    def headers(self):
        # type: (...) -> MutableMapping[str, str]
        """The response headers.

        :rtype: MutableMapping[str, str]
        """
        return self._headers

    @property
    def content_type(self):
        # type: (...) -> str
        """The content type of the response.

        :rtype: str
        """
        return self._content_type

    @property
    def reason(self):
        # type: (...) -> str
        """The reason phrase for this response.

        :rtype: str
        """
        return self._reason

    @property
    def encoding(self):
        # type: (...) -> Optional[str]
        """Returns the response encoding.

        :return: The response encoding. We either return the encoding set by the user,
         or try extracting the encoding from the response's content type. If all fails,
         we return `None`.
        :rtype: optional[str]
        """
        try:
            return self._encoding
        except AttributeError:
            self._encoding = get_charset_encoding(self)  # type: Optional[str]
            return self._encoding

    @encoding.setter
    def encoding(self, value):
        # type: (str) -> None
        """Sets the response encoding"""
        self._encoding = value
        self._text = None  # clear text cache
        self._json = None  # clear json cache as well

    def text(self, encoding=None):
        # type: (Optional[str]) -> str
        """Returns the response body as a string

        :param optional[str] encoding: The encoding you want to decode the text with. Can
         also be set independently through our encoding property
        :return: The response's content decoded as a string.
        """
        if self._text is None or encoding:
            encoding_to_pass = encoding or self.encoding
            self._text = decode_to_text(encoding_to_pass, self.content)
        return self._text

    def json(self):
        # type: (...) -> Any
        """Returns the whole body as a json object.

        :return: The JSON deserialized response body
        :rtype: any
        :raises json.decoder.JSONDecodeError or ValueError (in python 2.7) if object is not JSON decodable:
        """
        # this will trigger errors if response is not read in
        self.content  # pylint: disable=pointless-statement
        if not self._json:
            self._json = loads(self.text())
        return self._json

    def _stream_download_check(self):
        if self.is_stream_consumed:
            raise StreamConsumedError(self)
        if self.is_closed:
            raise StreamClosedError(self)

        self._is_stream_consumed = True

    def raise_for_status(self):
        # type: (...) -> None
        """Raises an HttpResponseError if the response has an error status code.

        If response is good, does nothing.
        """
        if cast(int, self.status_code) >= 400:
            raise HttpResponseError(response=self)

    @property
    def content(self):
        # type: (...) -> bytes
        """Return the response's content in bytes."""
        if self._content is None:
            raise ResponseNotReadError(self)
        return self._content

    def __repr__(self):
        # type: (...) -> str
        content_type_str = (
            ", Content-Type: {}".format(self.content_type) if self.content_type else ""
        )
        return "<HttpResponse: {} {}{}>".format(
            self.status_code, self.reason, content_type_str
        )

class HttpResponseImpl(_HttpResponseBaseImpl, _HttpResponse):
    """HttpResponseImpl built on top of our HttpResponse protocol class.

    Since ~azure.core.rest.HttpResponse is an abstract base class, we need to
    implement HttpResponse for each of our transports. This is an implementation
    that each of the sync transport responses can be built on.

    :keyword request: The request that led to the response
    :type request: ~azure.core.rest.HttpRequest
    :keyword any internal_response: The response we get directly from the transport. For example, for our requests
     transport, this will be a requests.Response.
    :keyword optional[int] block_size: The block size we are using in our transport
    :keyword int status_code: The status code of the response
    :keyword str reason: The HTTP reason
    :keyword str content_type: The content type of the response
    :keyword MutableMapping[str, str] headers: The response headers
    :keyword Callable stream_download_generator: The stream download generator that we use to stream the response.
    """

    def __enter__(self):
        # type: (...) -> HttpResponseImpl
        return self

    def close(self):
        # type: (...) -> None
        if not self.is_closed:
            self._is_closed = True
            self._internal_response.close()

    def __exit__(self, *args):
        # type: (...) -> None
        self.close()

    def _set_read_checks(self):
        self._is_stream_consumed = True
        self.close()

    def read(self):
        # type: (...) -> bytes
        """
        Read the response's bytes.

        """
        if self._content is None:
            self._content = b"".join(self.iter_bytes())
        self._set_read_checks()
        return self.content

    def iter_bytes(self):
        # type: () -> Iterator[bytes]
        """Iterates over the response's bytes. Will decompress in the process.

        :return: An iterator of bytes from the response
        :rtype: Iterator[str]
        """
        if self._content is not None:
            chunk_size = cast(int, self._block_size)
            for i in range(0, len(self.content), chunk_size):
                yield self.content[i : i + chunk_size]
        else:
            self._stream_download_check()
            for part in self._stream_download_generator(
                response=self,
                pipeline=None,
                decompress=True,
            ):
                yield part
        self.close()

    def iter_raw(self):
        # type: () -> Iterator[bytes]
        """Iterates over the response's bytes. Will not decompress in the process.

        :return: An iterator of bytes from the response
        :rtype: Iterator[str]
        """
        self._stream_download_check()
        for part in self._stream_download_generator(
            response=self, pipeline=None, decompress=False
        ):
            yield part
        self.close()
