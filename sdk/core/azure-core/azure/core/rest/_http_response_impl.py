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
from typing import cast, Any, Optional, Iterator
from ._helpers import (
    get_charset_encoding,
    decode_to_text,
    parse_lines_from_text,
)
from ..exceptions import HttpResponseError, ResponseNotReadError
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


class _HttpResponseBaseImpl(_HttpResponseBase):

    def __init__(self, **kwargs):
        # type: (Any) -> None
        super(_HttpResponseBaseImpl, self).__init__()
        self._request = kwargs.pop("request")
        self._internal_response = kwargs.pop("internal_response")
        self._is_closed = False
        self._is_stream_consumed = False
        self._connection_data_block_size = None
        self._json = None  # this is filled in ContentDecodePolicy, when we deserialize
        self._content = None  # type: Optional[bytes]
        self._text = None  # type: Optional[str]

    @property
    def request(self):
        # type: (...) -> _HttpRequest
        return self._request

    @property
    def url(self):
        # type: (...) -> str
        """Returns the URL that resulted in this response"""
        return self.request.url

    @property
    def is_closed(self):
        # type: (...) -> bool
        """Whether the network connection has been closed yet"""
        return self._is_closed

    @property
    def is_stream_consumed(self):
        # type: (...) -> bool
        """Whether the stream has been fully consumed"""
        return self._is_stream_consumed

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

    Helper impl for creating our transport responses
    """

    def __enter__(self):
        # type: (...) -> HttpResponseImpl
        return self

    def close(self):
        # type: (...) -> None
        self._is_closed = True
        self._internal_response.close()

    def __exit__(self, *args):
        # type: (...) -> None
        self.close()

    def read(self):
        # type: (...) -> bytes
        """
        Read the response's bytes.

        """
        if self._content is None:
            self._content = b"".join(self.iter_bytes())
        return self.content

    def iter_text(self):
        # type: () -> Iterator[str]
        """Iterate over the response text
        """
        for byte in self.iter_bytes():
            text = byte.decode(self.encoding or "utf-8")
            yield text

    def iter_lines(self):
        # type: () -> Iterator[str]
        for text in self.iter_text():
            lines = parse_lines_from_text(text)
            for line in lines:
                yield line

    def _close_stream(self):
        # type: (...) -> None
        self._is_stream_consumed = True
        self.close()
