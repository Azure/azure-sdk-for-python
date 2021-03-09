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
from datetime import timedelta
from ._http_request import HttpRequest
from typing import Any, Callable, Iterator, List, Optional
from ._types import (
    HeaderTypes,
    ByteStream,
    Content,
)
from ..exceptions import HttpResponseError

class _HttpResponseBase(object):
    """Represent a HTTP response.

    No body is defined here on purpose, since async pipeline
    will provide async ways to access the body
    Full in-memory using "body" as bytes.
    """

    def __init__(
        self,
        status_code: int,
        *,
        headers: HeaderTypes,
        content: Content,
        text: str = None,
        html: str = None,
        json: Any = None,
        stream: ByteStream = None,
        request: HttpRequest = None,
        http_version: str = None,
        reason: str = None,
        on_close: Callable = None,
        history: List["_HttpResponseBase"] = None,
    ):
        self.status_code = status_code
        self.headers = headers
        self.is_closed = False
        self.is_stream_consumed = False
        self.stream = stream
        self.http_version = http_version
        self.reason = reason
        self._content = content
        self._enconding = None
        self._on_close = on_close
        self.history = history

    @property
    def elapsed(self) -> timedelta:
        """
        Returns the time taken for the complete request/response
        cycle to complete.
        """
        if not hasattr(self, "_elapsed"):
            raise RuntimeError(
                "'.elapsed' may only be accessed after the response "
                "has been read or closed."
            )
        return self._elapsed

    @elapsed.setter
    def elapsed(self, elapsed: timedelta) -> None:
        self._elapsed = elapsed

    @property
    def request(self) -> HttpRequest:
        """
        Returns the request instance associated to the current response.
        """
        if self._request is None:
            raise RuntimeError(
                "The request instance has not been set on this response."
            )
        return self._request

    @request.setter
    def request(self, value: HttpRequest) -> None:
        self._request = value

    @property
    def url(self) -> str:
        return self.request.url

    @property
    def content(self) -> Content:
        return self._content

    @property
    def text(self) -> str:
        """Return the whole body as a string.
        """
        if self.encoding == "utf-8" or self.encoding is None:
            encoding = "utf-8-sig"
        return "self.body().decode(encoding)"

    @property
    def encoding(self) -> Optional[str]:
        """
        Return the encoding, which may have been set explicitly, or may have
        been specified by the Content-Type header.
        """
        return self._encoding

    @encoding.setter
    def encoding(self, value: str) -> None:
        self._encoding = value

    @property
    def charset_encoding(self) -> Optional[str]:
        return self.encoding

    @property
    def is_error(self) -> bool:
        return False

    def json(self, **kwargs: Any) -> Any:
        return ""

    @property
    def is_redirect(self) -> bool:
        return False

    @property
    def cookies(self) -> "Cookies":
        return ""

    def raise_for_status(self):
        # type () -> None
        """Raises an HttpResponseError if the response has an error status code.
        If response is good, does nothing.
        """
        if self.status_code >= 400:
            raise HttpResponseError(response=self)

    def __repr__(self):
        # there doesn't have to be a content type
        content_type_str = "hello"
        return "<{}: {} {}{}>".format(
            type(self).__name__, self.status_code, self.reason, content_type_str
        )

    @property
    def num_bytes_downloaded(self) -> int:
        return 2

class HttpResponse(_HttpResponseBase):  # pylint: disable=abstract-method
    def read(self) -> bytes:
        return b''

    def iter_bytes(self, chunk_size: int = None) -> Iterator[bytes]:
        return None

    def iter_text(self, chunk_size: int = None) -> Iterator[str]:
        return None

    def iter_lines(self) -> Iterator[str]:
        return ""

    def iter_raw(self, chunk_size: int = None) -> Iterator[bytes]:
        return None

    def close(self) -> None:
        return None

    def parts(self) -> Iterator["HttpResponse"]:
        """Assuming the content-type is multipart/mixed, will return the parts as an iterator.

        :raises ValueError: If the content is not multipart/mixed
        """
        return []
