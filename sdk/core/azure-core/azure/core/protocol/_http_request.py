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
import copy
from typing import Any
from ._types import (
    QueryParamTypes,
    HeaderTypes,
    CookieTypes,
    Content,
    RequestFiles,
    ByteStream,
)
import xml.etree.ElementTree as ET
from ..pipeline.transport import HttpRequest as PipelineTransportHttpRequest

try:
    binary_type = str
    from urlparse import urlparse  # type: ignore
except ImportError:
    binary_type = bytes  # type: ignore
    from urllib.parse import urlparse

def _is_stream(content):
    return isinstance(content, binary_type) or any(
        hasattr(content, attr) for attr in ["read", "__iter__", "__aiter__"]
    )

class HttpRequest(object):
    """Represents a HTTP request.

    :param str method: HTTP method for your call, i.e. "GET", "HEAD"
    :param str url: URL for your request
    :keyword params: Query parameters to include in the URL, as a dictionary
    :paramtype params: dict[str, any]
    :keyword headers: Dictionary of HTTP headers to include in the
     request.
    :paramtype headers: dict[str, any]
    :keyword cookies: Dictionary of Cookie items to include in the request.
    :paramtype cookies: dict[str, str] or ~http.cookiejar.CookieJar
    :keyword content: Binary content to include in the body of the
     request, as bytes or a byte iterator.
    :paramtype content: bytes or iterator of bytes
    :keyword dict data: Form data to include in the body of the request,
     as a dictionary.
    :keyword files: A dictionary of upload files to include in the
     body of the request.
    :paramtype files: Dictionary of str to IO of string or bytes
    :keyword any json: A JSON serializable object to include in the body
     of the request.
    """

    def __init__(
        self,
        method: str,
        url: str,
        *,
        params: QueryParamTypes = None,
        headers: HeaderTypes = None,
        cookies: CookieTypes = None,
        content: Content = None,
        data: dict = None,
        files: RequestFiles = None,
        json: Any = None,
    ) -> None:
        # hacking by utilizing pipeline transport HttpRequest
        self._http_request = PipelineTransportHttpRequest(
            method=method,
            url=url,
            headers=headers,
            files=files,
            data=content
        )
        if params:
            self._http_request.format_parameters(params)
        if data:
            self._http_request.set_formdata_body(data)
        if content is not None:
            content_type = self._http_request.headers.get("Content-Type")
            if _is_stream(content):
                self._http_request.set_streamed_data_body(content)
            elif isinstance(content, ET.Element):
                self._http_request.set_xml_body(content)
            elif content_type and content_type.startswith("text/"):
                self._http_request.set_text_body(content)
            else:
                self._http_request.data = content
        if json:
            self._http_request.set_json_body(json)

        self.url = self._http_request.url
        self.method = self._http_request.method
        self.headers = self._http_request.headers
        # pipeline transport HttpRequest hacks data. It can either
        # be binary content, or the formdata dict
        self.content = self._http_request.data
        self.data = self._http_request.data
        self.files = self._http_request.files


    def __repr__(self):
        return "<HttpRequest [{}], url: '{}'>".format(
            self.method, self.url
        )

    def __deepcopy__(self, memo=None):
        try:
            return HttpRequest(self.method, self.url, self.headers, None, None)
        except (ValueError, TypeError):
            return copy.copy(self)
