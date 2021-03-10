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
import json
from datetime import timedelta
from ._http_request import HttpRequest
from typing import Any, Callable, Iterator, List, Optional
from ._types import (
    HeaderTypes,
    ByteStream,
    Content,
)
from ..exceptions import HttpResponseError
from ..pipeline.transport._base import _HttpResponseBase as _PipelineTransportHttpResponseBase

class _HttpResponseBase(object):
    """Base class for HttpResponse and AsyncHttpResponse.

    :param int status_code: Status code of the response.
    :keyword headers: Response headers
    :paramtype headers: dict[str, any]
    :keyword str text: The response content as a string
    :keyword any json: JSON content
    :keyword stream: Streamed response
    :paramtype stream: bytes or iterator of bytes
    :keyword callable on_close: Any callable you want to cal
     when closing your HttpResponse
    :keyword history: If redirection, history of all redirection
     that resulted in this response.
    :paramtype history: list[~azure.core.protocol.HttpResponse]
    """

    def __init__(
        self,
        status_code: int,
        *,
        headers: HeaderTypes = None,
        content: Content = None,
        request: HttpRequest = None,
        http_version: str = None,
        reason: str = None,
        text: str = None,
        json: Any = None,
        stream: ByteStream = None,
        on_close: Callable = None,
        history: List["_HttpResponseBase"] = None,
        _internal_response = None,
        _block_size = None
    ):
        self._http_response = _PipelineTransportHttpResponseBase(
            request=request,
            internal_response=_internal_response,
            block_size=_block_size,
        )
        self.status_code = status_code
        self.headers = self._http_response.headers
        self.is_closed = False
        self.is_stream_consumed = False
        self.http_version = http_version
        self.reason = self._http_response.reason
        self._content = self._http_response.body
        self._encoding = None
        self._on_close = on_close
        self.history = history
        self._request = HttpRequest._from_pipeline_transport(
            self._http_response.request
        )

    @property
    def request(self) -> HttpRequest:
        """Returns the request instance associated to the current response.
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
        """Returns the URL that resulted in this response.
        """
        return self.request.url

    @property
    def content(self) -> Content:
        """Returns the actual content of the response body.
        """
        raise NotImplementedError()

    @property
    def text(self) -> str:
        """Returns the response body as a string.
        """
        if self.encoding == "utf-8" or self.encoding is None:
            encoding = "utf-8-sig"
        return self._http_response.body().decode(encoding)

    @property
    def encoding(self) -> Optional[str]:
        """Returns the response encoding. By default, is specified
        by the response Content-Type header.
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
        """Returns whether this response is an error response.
        """
        return self.status_code < 400

    def json(self, **kwargs) -> Any:
        """Return the whole body as a json object.

        :return: The JSON deserialized response body
        :rtype: any
        :raises json.decoder.JSONDecodeError or ValueError (in python 2.7) if object is not JSON decodable:
        """
        return json.loads(self.text)

    @property
    def is_redirect(self) -> bool:
        """Returns whether this response is a redirected response"""
        return False

    def raise_for_status(self) -> None:
        """Raises an HttpResponseError if the response has an error status code.
        If response is good, does nothing.
        """
        if self.status_code >= 400:
            raise HttpResponseError(response=self)

    def __repr__(self):
        return self._http_response.__repr__

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
