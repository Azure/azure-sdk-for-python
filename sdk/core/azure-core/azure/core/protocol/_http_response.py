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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional
    from ._types import HeaderTypes

from ._http_request import HttpRequest
from ..pipeline.transport import HttpResponse as _PipelineTransportHttpResponse

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

    def __init__(self, status_code, **kwargs):
        # type: (int, Any) -> None
        self._internal_response = kwargs.pop("_internal_response")  # type: _PipelineTransportHttpResponse
        self.request = kwargs.pop("request")
        self._encoding = None

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
        # type: (...) -> HeaderTypes
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
        return self._encoding

    @encoding.setter
    def encoding(self, value: str) -> None:
        """Sets the response encoding"""
        self._encoding = value

    @property
    def text(self):
        # type: (...) -> str
        """Returns the response body as a string"""
        return self._internal_response.text(self.encoding)

    def json(self):
        # type: (...) -> Any
        """Returns the whole body as a json object.

        :return: The JSON deserialized response body
        :rtype: any
        :raises json.decoder.JSONDecodeError or ValueError (in python 2.7) if object is not JSON decodable:
        """
        return json.loads(self._internal_response.text(self.encoding))

    def raise_for_status(self):
        # type: (...) -> None
        """Raises an HttpResponseError if the response has an error status code.

        If response is good, does nothing.
        """
        return self._internal_response.raise_for_status()

    def __repr__(self):
        # type: (...) -> str
        return self._internal_response.__repr__

class HttpResponse(_HttpResponseBase):

    @property
    def content(self):
        # type: (...) -> bytes
        return self._internal_response.body()
