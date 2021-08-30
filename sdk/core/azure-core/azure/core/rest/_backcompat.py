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
from typing import Any, Optional
import xml.etree.ElementTree as ET
from ..utils._pipeline_transport_rest_shared import (
    _decode_parts_helper,
    _get_raw_parts_helper,
    _prepare_multipart_body_helper,
    _format_parameters_helper,
    _parts_helper,
)

try:
    binary_type = str
    from urlparse import urlparse  # type: ignore
except ImportError:
    binary_type = bytes  # type: ignore
    from urllib.parse import urlparse

def _pad_attr_name(attr, backcompat_attrs):
    return "_{}".format(attr) if attr in backcompat_attrs else attr

class HttpRequestBackcompatMixin(object):

    def __getattr__(self, attr):
        backcompat_attrs = [
            "files",
            "data",
            "multipart_mixed_info",
            "query",
            "body",
            "format_parameters",
            "set_streamed_data_body",
            "set_text_body",
            "set_xml_body",
            "set_json_body",
            "set_formdata_body",
            "set_bytes_body",
            "set_multipart_mixed",
            "prepare_multipart_body",
            "serialize",
        ]
        attr = _pad_attr_name(attr, backcompat_attrs)
        return self.__getattribute__(attr)

    def __setattr__(self, attr, value):
        backcompat_attrs = [
            "multipart_mixed_info",
            "files",
            "data",
            "body",
        ]
        attr = _pad_attr_name(attr, backcompat_attrs)
        super(HttpRequestBackcompatMixin, self).__setattr__(attr, value)

    @property
    def _multipart_mixed_info(self):
        """DEPRECATED: Information used to make multipart mixed requests.

        This is deprecated and will be removed in a later release.
        """
        try:
            return self.__multipart_mixed_info
        except AttributeError:
            return None

    @_multipart_mixed_info.setter
    def _multipart_mixed_info(self, val):
        """DEPRECATED: Set information to make multipart mixed requests.

        This is deprecated and will be removed in a later release.
        """
        self.__multipart_mixed_info = val

    @property
    def _query(self):
        """DEPRECATED: Query parameters passed in by user

        This is deprecated and will be removed in a later release.
        """
        query = urlparse(self.url).query
        if query:
            return {p[0]: p[-1] for p in [p.partition("=") for p in query.split("&")]}
        return {}

    @property
    def _body(self):
        """DEPRECATED: Body of the request. You should use the `content` property instead

        This is deprecated and will be removed in a later release.
        """
        return self._data

    @_body.setter
    def _body(self, val):
        """DEPRECATED: Set the body of the request

        This is deprecated and will be removed in a later release.
        """
        self._data = val

    @staticmethod
    def _format_data(data):
        from ..pipeline.transport._base import HttpRequest as PipelineTransportHttpRequest
        return PipelineTransportHttpRequest._format_data(data)  # pylint: disable=protected-access

    def _format_parameters(self, params):
        """DEPRECATED: Format the query parameters

        This is deprecated and will be removed in a later release.
        You should pass the query parameters through the kwarg `params`
        instead.
        """
        return _format_parameters_helper(self, params)

    def _set_streamed_data_body(self, data):
        """DEPRECATED: Set the streamed request body.

        This is deprecated and will be removed in a later release.
        You should pass your stream content through the `content` kwarg instead
        """
        if not isinstance(data, binary_type) and not any(
            hasattr(data, attr) for attr in ["read", "__iter__", "__aiter__"]
        ):
            raise TypeError(
                "A streamable data source must be an open file-like object or iterable."
            )
        self._data = data
        self._files = None

    def _set_text_body(self, data):
        """DEPRECATED: Set the text body

        This is deprecated and will be removed in a later release.
        You should pass your text content through the `content` kwarg instead
        """
        if data is None:
            self._data = None
        else:
            self._data = data
            self.headers["Content-Length"] = str(len(self._data))
        self._files = None

    def _set_xml_body(self, data):
        """DEPRECATED: Set the xml body.

        This is deprecated and will be removed in a later release.
        You should pass your xml content through the `content` kwarg instead
        """
        if data is None:
            self._data = None
        else:
            bytes_data = ET.tostring(data, encoding="utf8")
            self._data = bytes_data.replace(b"encoding='utf8'", b"encoding='utf-8'")
            self.headers["Content-Length"] = str(len(self._data))
        self._files = None

    def _set_json_body(self, data):
        """DEPRECATED: Set the json request body.

        This is deprecated and will be removed in a later release.
        You should pass your json content through the `json` kwarg instead
        """
        if data is None:
            self._data = None
        else:
            self._data = json.dumps(data)
            self.headers["Content-Length"] = str(len(self._data))
        self._files = None

    def _set_formdata_body(self, data=None):
        """DEPRECATED: Set the formrequest body.

        This is deprecated and will be removed in a later release.
        You should pass your stream content through the `files` kwarg instead
        """
        if data is None:
            data = {}
        content_type = self.headers.pop("Content-Type", None) if self.headers else None

        if content_type and content_type.lower() == "application/x-www-form-urlencoded":
            self._data = {f: d for f, d in data.items() if d is not None}
            self._files = None
        else:  # Assume "multipart/form-data"
            self._files = {
                f: self._format_data(d) for f, d in data.items() if d is not None
            }
            self._data = None

    def _set_bytes_body(self, data):
        """DEPRECATED: Set the bytes request body.

        This is deprecated and will be removed in a later release.
        You should pass your bytes content through the `content` kwarg instead
        """
        if data:
            self.headers["Content-Length"] = str(len(data))
        self._data = data
        self._files = None

    def _set_multipart_mixed(self, *requests, **kwargs):
        """DEPRECATED: Set the multipart mixed info.

        This is deprecated and will be removed in a later release.
        """
        self.multipart_mixed_info = (
            requests,
            kwargs.pop("policies", []),
            kwargs.pop("boundary", None),
            kwargs
        )

    def _prepare_multipart_body(self, content_index=0):
        """DEPRECATED: Prepare your request body for multipart requests.

        This is deprecated and will be removed in a later release.
        """
        return _prepare_multipart_body_helper(self, content_index)

    def _serialize(self):
        """DEPRECATED: Serialize this request using application/http spec.

        This is deprecated and will be removed in a later release.

        :rtype: bytes
        """
        from ..pipeline.transport._base import _serialize_request
        return _serialize_request(self)

class _HttpResponseBackcompatMixinBase(object):

    def __getattr__(self, attr):
        backcompat_attrs = [
            "body",
            "internal_response",
            "block_size",
            "stream_download",
        ]
        attr = _pad_attr_name(attr, backcompat_attrs)
        return self.__getattribute__(attr)

    def __setattr__(self, attr, value):
        backcompat_attrs = [
            "block_size",
            "internal_response",
            "request",
            "status_code",
            "headers",
            "reason",
            "content_type",
            "stream_download",
        ]
        attr = _pad_attr_name(attr, backcompat_attrs)
        super(_HttpResponseBackcompatMixinBase, self).__setattr__(attr, value)

    def _body(self):
        """DEPRECATED: Get the response body.

        This is deprecated and will be removed in a later release.
        You should get it through the `content` property instead
        """
        return self.content  # pylint: disable=no-member

    def _decode_parts(self, message, http_response_type, requests):
        from ..pipeline.transport._base import BytesIOSocket, _HTTPResponse
        def _deserialize_response(
            http_response_as_bytes, http_request, http_response_type
        ):
            local_socket = BytesIOSocket(http_response_as_bytes)
            response = _HTTPResponse(local_socket, method=http_request.method)
            response.begin()
            return http_response_type(request=http_request, internal_response=response)
        return _decode_parts_helper(
            self, message, http_response_type, requests, _deserialize_response
        )

    def _get_raw_parts(self, http_response_type=None):
        from ..pipeline.transport._base import RestHttpClientTransportResponse
        return _get_raw_parts_helper(
            self, http_response_type, RestHttpClientTransportResponse
        )

    def _stream_download(self, pipeline, **kwargs):
        """DEPRECATED: Generator for streaming request body data.

        This is deprecated and will be removed in a later release.
        You should use `iter_bytes` or `iter_raw` instead.

        :rtype: iterator[bytes]
        """
        return self._stream_download_generator(pipeline, self, **kwargs)

class HttpResponseBackcompatMixin(_HttpResponseBackcompatMixinBase):

    def __getattr__(self, attr):
        backcompat_attrs = ["parts"]
        attr = _pad_attr_name(attr, backcompat_attrs)
        return super(HttpResponseBackcompatMixin, self).__getattr__(attr)

    def parts(self):
        """DEPRECATED: Assuming the content-type is multipart/mixed, will return the parts as an async iterator.

        This is deprecated and will be removed in a later release.

        :rtype: Iterator
        :raises ValueError: If the content is not multipart/mixed
        """
        return _parts_helper(self)
