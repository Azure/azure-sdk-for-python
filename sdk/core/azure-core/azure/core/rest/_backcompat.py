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

class HttpRequestBackcompatMixin(object):

    @property
    def files(self):
        return self._files

    @property
    def data(self):
        return self._data

    @property
    def multipart_mixed_info(self):
        try:
            return self._multipart_mixed_info
        except AttributeError:
            return None

    @multipart_mixed_info.setter
    def multipart_mixed_info(self, val):
        self._multipart_mixed_info = val

    @property
    def query(self):
        query = urlparse(self.url).query
        if query:
            return {p[0]: p[-1] for p in [p.partition("=") for p in query.split("&")]}
        return {}

    @property
    def body(self):
        return self._data

    @body.setter
    def body(self, val):
        self._data = val

    @staticmethod
    def _format_data(data):
        from ..pipeline.transport._base import HttpRequest as PipelineTransportHttpRequest
        return PipelineTransportHttpRequest._format_data(data)  # pylint: disable=protected-access

    def format_parameters(self, params):
        return _format_parameters_helper(self, params)

    def set_streamed_data_body(self, data):
        if not isinstance(data, binary_type) and not any(
            hasattr(data, attr) for attr in ["read", "__iter__", "__aiter__"]
        ):
            raise TypeError(
                "A streamable data source must be an open file-like object or iterable."
            )
        self._data = data
        self._files = None

    def set_text_body(self, data):
        if data is None:
            self._data = None
        else:
            self._data = data
            self.headers["Content-Length"] = str(len(self._data))
        self._files = None

    def set_xml_body(self, data):
        if data is None:
            self._data = None
        else:
            bytes_data = ET.tostring(data, encoding="utf8")
            self._data = bytes_data.replace(b"encoding='utf8'", b"encoding='utf-8'")
            self.headers["Content-Length"] = str(len(self._data))
        self._files = None

    def set_json_body(self, data):
        if data is None:
            self._data = None
        else:
            self._data = json.dumps(data)
            self.headers["Content-Length"] = str(len(self._data))
        self._files = None

    def set_formdata_body(self, data=None):
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

    def set_bytes_body(self, data):
        if data:
            self.headers["Content-Length"] = str(len(data))
        self._data = data
        self._files = None

    def set_multipart_mixed(self, *requests, **kwargs):
        self.multipart_mixed_info = (
            requests,
            kwargs.pop("policies", []),
            kwargs.pop("boundary", None),
            kwargs
        )

    def prepare_multipart_body(self, content_index=0):
        return _prepare_multipart_body_helper(self, content_index)

    def serialize(self):
        """Serialize this request using application/http spec.

        :rtype: bytes
        """
        from ..pipeline.transport._base import _serialize_request
        return _serialize_request(self)

class _HttpResponseBackcompatMixinBase(object):

    def body(self):
        return self.content  # pylint: disable=no-member

    @property
    def internal_response(self):
        return self._internal_response

    @internal_response.setter
    def internal_response(self, val):
        self._internal_response = val  # type: Any

    @property
    def block_size(self):
        return self._connection_data_block_size

    @block_size.setter
    def block_size(self, val):
        self._connection_data_block_size = val  # type: Optional[int]

    def _decode_parts(self, message, http_response_type, requests):
        """Rebuild an HTTP response from pure string."""
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

    def stream_download(self, pipeline, **kwargs):  # pylint: disable=unused-argument
        if kwargs.get("decompress"):
            return self.iter_bytes()  # pylint: disable=no-member
        return self.iter_raw()  # pylint: disable=no-member

class HttpResponseBackcompatMixin(_HttpResponseBackcompatMixinBase):

    def parts(self):
        return _parts_helper(self)
