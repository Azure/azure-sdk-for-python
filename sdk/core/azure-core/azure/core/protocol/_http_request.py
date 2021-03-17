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
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

from ..pipeline.transport import (
    HttpRequest as _PipelineTransportHttpRequest,
)

if TYPE_CHECKING:
    from typing import Any, Optional
    from ._types import QueryTypes


def _is_stream(content):
    return isinstance(content, (str, bytes)) or any(
        hasattr(content, attr) for attr in ["read", "__iter__", "__aiter__"]
    )

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
    """

    def __init__(self, method, url, **kwargs):
        # type: (str, str, Any) -> None

        data = kwargs.pop("data", None)
        content = kwargs.pop("content", None)
        json = kwargs.pop("json", None)
        files = kwargs.pop("files", None)

        self._internal_request = _PipelineTransportHttpRequest(
            method=method,
            url=url,
            headers=kwargs.pop("headers", None),
        )
        params = kwargs.pop("params", None)

        if params:
            self._internal_request.format_parameters(params)
        if data is not None:
            self._internal_request.set_formdata_body(data)
        if content is not None:
            content_type = self._internal_request.headers.get("Content-Type")
            if _is_stream(content):
                self._internal_request.set_streamed_data_body(content)
            elif isinstance(content, ET.Element):
                self._internal_request.set_xml_body(content)
            elif content_type and content_type.startswith("text/"):
                self._internal_request.set_text_body(content)
            else:
                self._internal_request.data = content
        if json is not None:
            self._internal_request.set_json_body(json)
            if not self._internal_request.headers.get("Content-Type"):
                self._internal_request.headers["Content-Type"] = "application/json"
        if files is not None:
            self._internal_request.set_formdata_body(files)

        if not self._internal_request.headers.get("Content-Length"):
            try:
                # set content length header if possible
                self._internal_request.headers["Content-Length"] = str(len(self._internal_request.data))  # type: ignore
            except TypeError:
                pass
        self.method = self._internal_request.method
        if kwargs:
            raise TypeError(
                "You have passed in kwargs '{}' that are not valid kwargs.".format(
                    "', '".join(list(kwargs.keys()))
                )
            )

    @property
    def url(self) -> str:
        return self._internal_request.url

    @url.setter
    def url(self, val: str) -> None:
        self._internal_request.url = val

    @property
    def method(self) -> str:
        return self._internal_request.method

    @method.setter
    def method(self, val: str) -> None:
        self._internal_request.method = val


    def __repr__(self):
        return "<HttpRequest [{}], url: '{}'>".format(
            self.method, self.url
        )
