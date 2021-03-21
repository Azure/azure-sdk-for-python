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

__all__ = ["HttpRequest", "HttpResponse"]

import json
from enum import Enum
import xml.etree.ElementTree as ET
from typing import TYPE_CHECKING

from azure.core.pipeline.transport import (
    HttpRequest as _PipelineTransportHttpRequest,
    HttpResponse as _PipelineTransportHttpResponse,
)

if TYPE_CHECKING:
    from typing import Any, Optional, Union, Mapping, Sequence, Tuple

    HeaderTypes = Union[Mapping[str, str], Sequence[Tuple[str, str]]]


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

    @method.setter
    def method(self, val):
        # type: (str) -> None
        self._internal_request.method = val

    @property
    def headers(self):
        return self._internal_request.headers

    @property
    def content(self):
        return self._internal_request.data

    def __repr__(self):
        return "<HttpRequest [{}], url: '{}'>".format(self.method, self.url)

    def __deepcopy__(self, memo=None):
        return self._internal_request.__deepcopy__(memo)


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
        self._internal_response = kwargs.pop(
            "_internal_response"
        )  # type: _PipelineTransportHttpResponse
        self.request = kwargs.pop("request")
        self._encoding = ""

    @property
    def status_code(self):
        # type: (...) -> int
        """Returns the status code of the response"""
        return self._internal_response.status_code or -1

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
        return self._internal_response.reason or ""

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
    def encoding(self, value):
        # type: (str) -> None
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
        # type: () -> None
        """Raises an HttpResponseError if the response has an error status code.

        If response is good, does nothing.
        """
        self._internal_response.raise_for_status()

    def __repr__(self):
        # type: (...) -> str
        return repr(self._internal_response)


class HttpResponse(_HttpResponseBase):
    @property
    def content(self):
        # type: (...) -> bytes
        return self._internal_response.body()


class AsyncHttpResponse(_HttpResponseBase):
    @property
    def content(self):
        # type: (...) -> bytes
        return self._internal_response.body()
