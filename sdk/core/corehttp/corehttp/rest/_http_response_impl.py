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
from typing import Any, Optional, Iterator, MutableMapping, Callable

from ._helpers import (
    get_charset_encoding,
    decode_to_text,
)
from ..exceptions import (
    HttpResponseError,
    ResponseNotReadError,
    StreamConsumedError,
    StreamClosedError,
)
from ._rest_py3 import (
    _HttpResponseBase,
    HttpResponse as _HttpResponse,
    HttpRequest as _HttpRequest,
)


class _HttpResponseBaseImpl(_HttpResponseBase):  # pylint: disable=too-many-instance-attributes
    """Base Implementation class for corehttp.rest.HttpRespone and corehttp.rest.AsyncHttpResponse

    Since the rest responses are abstract base classes, we need to implement them for each of our transport
    responses. This is the base implementation class shared by HttpResponseImpl and AsyncHttpResponseImpl.
    The transport responses will be built on top of HttpResponseImpl and AsyncHttpResponseImpl

    :keyword request: The request that led to the response
    :type request: ~corehttp.rest.HttpRequest
    :keyword any internal_response: The response we get directly from the transport. For example, for our requests
     transport, this will be a requests.Response.
    :keyword optional[int] block_size: The block size we are using in our transport
    :keyword int status_code: The status code of the response
    :keyword str reason: The HTTP reason
    :keyword str content_type: The content type of the response
    :keyword MutableMapping[str, str] headers: The response headers
    :keyword Callable stream_download_generator: The stream download generator that we use to stream the response.
    """

    def __init__(self, **kwargs) -> None:
        super(_HttpResponseBaseImpl, self).__init__()
        self._request = kwargs.pop("request")
        self._internal_response = kwargs.pop("internal_response")
        self._block_size: int = kwargs.pop("block_size", None) or 4096
        self._status_code: int = kwargs.pop("status_code")
        self._reason: str = kwargs.pop("reason")
        self._content_type: str = kwargs.pop("content_type")
        self._headers: MutableMapping[str, str] = kwargs.pop("headers")
        self._stream_download_generator: Callable = kwargs.pop("stream_download_generator")
        self._is_closed = False
        self._is_stream_consumed = False
        self._json = None  # this is filled in ContentDecodePolicy, when we deserialize
        self._content: Optional[bytes] = None
        self._text: Optional[str] = None

    @property
    def request(self) -> _HttpRequest:
        """The request that resulted in this response.

        :rtype: ~corehttp.rest.HttpRequest
        :return: The request that resulted in this response.
        """
        return self._request

    @property
    def url(self) -> str:
        """The URL that resulted in this response.

        :rtype: str
        :return: The URL that resulted in this response.
        """
        return self.request.url

    @property
    def is_closed(self) -> bool:
        """Whether the network connection has been closed yet.

        :rtype: bool
        :return: Whether the network connection has been closed yet.
        """
        return self._is_closed

    @property
    def is_stream_consumed(self) -> bool:
        """Whether the stream has been consumed.

        :rtype: bool
        :return: Whether the stream has been consumed.
        """
        return self._is_stream_consumed

    @property
    def status_code(self) -> int:
        """The status code of this response.

        :rtype: int
        :return: The status code of this response.
        """
        return self._status_code

    @property
    def headers(self) -> MutableMapping[str, str]:
        """The response headers.

        :rtype: MutableMapping[str, str]
        :return: The response headers.
        """
        return self._headers

    @property
    def content_type(self) -> Optional[str]:
        """The content type of the response.

        :rtype: optional[str]
        :return: The content type of the response.
        """
        return self._content_type

    @property
    def reason(self) -> str:
        """The reason phrase for this response.

        :rtype: str
        :return: The reason phrase for this response.
        """
        return self._reason

    @property
    def encoding(self) -> Optional[str]:
        """Returns the response encoding.

        :return: The response encoding. We either return the encoding set by the user,
         or try extracting the encoding from the response's content type. If all fails,
         we return `None`.
        :rtype: optional[str]
        """
        try:
            return self._encoding
        except AttributeError:
            self._encoding: Optional[str] = get_charset_encoding(self)
            return self._encoding

    @encoding.setter
    def encoding(self, value: str) -> None:
        """Sets the response encoding.

        :param str value: Sets the response encoding.
        """
        self._encoding = value
        self._text = None  # clear text cache
        self._json = None  # clear json cache as well

    def text(self, encoding: Optional[str] = None) -> str:
        """Returns the response body as a string

        :param optional[str] encoding: The encoding you want to decode the text with. Can
         also be set independently through our encoding property
        :return: The response's content decoded as a string.
        :rtype: str
        """
        if encoding:
            return decode_to_text(encoding, self.content)
        if self._text:
            return self._text
        self._text = decode_to_text(self.encoding, self.content)
        return self._text

    def json(self) -> Any:
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

    def raise_for_status(self) -> None:
        """Raises an HttpResponseError if the response has an error status code.

        If response is good, does nothing.
        """
        if self.status_code >= 400:
            raise HttpResponseError(response=self)

    @property
    def content(self) -> bytes:
        """Return the response's content in bytes.

        :return: The response's content in bytes.
        :rtype: bytes
        """
        if self._content is None:
            raise ResponseNotReadError(self)
        return self._content

    def __repr__(self) -> str:
        content_type_str = ", Content-Type: {}".format(self.content_type) if self.content_type else ""
        return "<HttpResponse: {} {}{}>".format(self.status_code, self.reason, content_type_str)


class HttpResponseImpl(_HttpResponseBaseImpl, _HttpResponse):
    """HttpResponseImpl built on top of our HttpResponse protocol class.

    Since ~corehttp.rest.HttpResponse is an abstract base class, we need to
    implement HttpResponse for each of our transports. This is an implementation
    that each of the sync transport responses can be built on.

    :keyword request: The request that led to the response
    :type request: ~corehttp.rest.HttpRequest
    :keyword any internal_response: The response we get directly from the transport. For example, for our requests
     transport, this will be a requests.Response.
    :keyword optional[int] block_size: The block size we are using in our transport
    :keyword int status_code: The status code of the response
    :keyword str reason: The HTTP reason
    :keyword str content_type: The content type of the response
    :keyword MutableMapping[str, str] headers: The response headers
    :keyword Callable stream_download_generator: The stream download generator that we use to stream the response.
    """

    def __enter__(self) -> "HttpResponseImpl":
        return self

    def close(self) -> None:
        if not self.is_closed:
            self._is_closed = True
            self._internal_response.close()

    def __exit__(self, *args) -> None:
        self.close()

    def _set_read_checks(self):
        self._is_stream_consumed = True
        self.close()

    def read(self) -> bytes:
        """Read the response's bytes.

        :return: The response's bytes
        :rtype: bytes
        """
        if self._content is None:
            self._content = b"".join(self.iter_bytes())
        self._set_read_checks()
        return self.content

    def iter_bytes(self, **kwargs) -> Iterator[bytes]:
        """Iterates over the response's bytes. Will decompress in the process.

        :return: An iterator of bytes from the response
        :rtype: Iterator[str]
        """
        if self._content is not None:
            chunk_size = self._block_size
            for i in range(0, len(self.content), chunk_size):
                yield self.content[i : i + chunk_size]
        else:
            self._stream_download_check()
            yield from self._stream_download_generator(response=self, pipeline=None, decompress=True)
        self.close()

    def iter_raw(self, **kwargs) -> Iterator[bytes]:
        """Iterates over the response's bytes. Will not decompress in the process.

        :return: An iterator of bytes from the response
        :rtype: Iterator[str]
        """
        self._stream_download_check()
        yield from self._stream_download_generator(response=self, pipeline=None, decompress=False)
        self.close()
