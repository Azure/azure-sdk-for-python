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
import os
import json
from typing import cast, IO
from six.moves.http_client import HTTPResponse as _HTTPResponse
import xml.etree.ElementTree as ET

from email.message import Message
try:
    from email import message_from_bytes as message_parser
except ImportError:  # 2.7
    from email import message_from_string as message_parser  # type: ignore
from ..pipeline.transport._base import BytesIOSocket, _serialize_request
from ..pipeline import PipelineRequest, PipelineResponse, PipelineContext
from ..pipeline._tools import await_result as _await_result

try:
    binary_type = str
    from urlparse import urlparse  # type: ignore
except ImportError:
    binary_type = bytes  # type: ignore
    from urllib.parse import urlparse

def _deserialize_response(
    http_response_as_bytes, http_request, http_response_type=None
):
    if http_response_type is None:
        from ._client_transport_response import HttpClientTransportResponse
        http_response_type = HttpClientTransportResponse
    local_socket = BytesIOSocket(http_response_as_bytes)
    response = _HTTPResponse(local_socket, method=http_request.method)
    response.begin()
    return http_response_type(http_request, response)


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
        if hasattr(data, "read"):
            data = cast(IO, data)
            data_name = None
            try:
                if data.name[0] != "<" and data.name[-1] != ">":
                    data_name = os.path.basename(data.name)
            except (AttributeError, TypeError):
                pass
            return (data_name, data, "application/octet-stream")
        return (None, cast(str, data))

    def format_parameters(self, params):
        query = urlparse(self.url).query
        if query:
            self.url = self.url.partition("?")[0]
            existing_params = {
                p[0]: p[-1] for p in [p.partition("=") for p in query.split("&")]
            }
            params.update(existing_params)
        query_params = []
        for k, v in params.items():
            if isinstance(v, list):
                for w in v:
                    if w is None:
                        raise ValueError("Query parameter {} cannot be None".format(k))
                    query_params.append("{}={}".format(k, w))
            else:
                if v is None:
                    raise ValueError("Query parameter {} cannot be None".format(k))
                query_params.append("{}={}".format(k, v))
        query = "?" + "&".join(query_params)
        self.url = self.url + query

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
        if not self.multipart_mixed_info:
            return 0

        requests = self.multipart_mixed_info[0]  # type: List[HttpRequest]
        boundary = self.multipart_mixed_info[2]  # type: Optional[str]

        # Update the main request with the body
        main_message = Message()
        main_message.add_header("Content-Type", "multipart/mixed")
        if boundary:
            main_message.set_boundary(boundary)

        for req in requests:
            part_message = Message()
            if req.multipart_mixed_info:
                content_index = req.prepare_multipart_body(content_index=content_index)
                part_message.add_header("Content-Type", req.headers['Content-Type'])
                payload = req.serialize()
                # We need to remove the ~HTTP/1.1 prefix along with the added content-length
                payload = payload[payload.index(b'--'):]
            else:
                part_message.add_header("Content-Type", "application/http")
                part_message.add_header("Content-Transfer-Encoding", "binary")
                part_message.add_header("Content-ID", str(content_index))
                payload = req.serialize()
                content_index += 1
            part_message.set_payload(payload)
            main_message.attach(part_message)

        try:
            from email.policy import HTTP

            full_message = main_message.as_bytes(policy=HTTP)
            eol = b"\r\n"
        except ImportError:  # Python 2.7
            # Right now we decide to not support Python 2.7 on serialization, since
            # it doesn't serialize a valid HTTP request (and our main scenario Storage refuses it)
            raise NotImplementedError(
                "Multipart request are not supported on Python 2.7"
            )
            # full_message = main_message.as_string()
            # eol = b'\n'
        _, _, body = full_message.split(eol, 2)
        self.set_bytes_body(body)
        self.headers["Content-Type"] = (
            "multipart/mixed; boundary=" + main_message.get_boundary()
        )
        return content_index

    def serialize(self):
        # type: () -> bytes
        """Serialize this request using application/http spec.

        :rtype: bytes
        """
        return _serialize_request(self)

class _HttpResponseBackcompatMixinBase(object):

    def body(self):
        return self.content

    @property
    def internal_response(self):
        return self._internal_response

    @property
    def block_size(self):
        return self._connection_data_block_size

    def _decode_parts(self, message, http_response_type, requests):
        """Rebuild an HTTP response from pure string."""
        responses = []
        for index, raw_reponse in enumerate(message.get_payload()):
            content_type = raw_reponse.get_content_type()
            if content_type == "application/http":
                responses.append(
                    _deserialize_response(
                        raw_reponse.get_payload(decode=True),
                        requests[index],
                        http_response_type=http_response_type,
                    )
                )
            elif content_type == "multipart/mixed" and requests[index].multipart_mixed_info:
                # The message batch contains one or more change sets
                changeset_requests = requests[index].multipart_mixed_info[0]  # type: ignore
                changeset_responses = self._decode_parts(raw_reponse, http_response_type, changeset_requests)
                responses.extend(changeset_responses)
            else:
                raise ValueError(
                    "Multipart doesn't support part other than application/http for now"
                )
        return responses

    def _get_raw_parts(self, http_response_type=None):
        if http_response_type is None:
            from ._client_transport_response import HttpClientTransportResponse
            http_response_type = HttpClientTransportResponse

        body_as_bytes = self.body()
        # In order to use email.message parser, I need full HTTP bytes. Faking something to make the parser happy
        http_body = (
            b"Content-Type: "
            + self.content_type.encode("ascii")
            + b"\r\n\r\n"
            + body_as_bytes
        )
        message = message_parser(http_body)  # type: Message
        requests = self.request.multipart_mixed_info[0]  # type: List[HttpRequest]
        return self._decode_parts(message, http_response_type, requests)

    def stream_download(self, pipeline, **kwargs):
        if kwargs.get("decompress"):
            return self.iter_bytes()
        return self.iter_raw()

class HttpResponseBackcompatMixin(_HttpResponseBackcompatMixinBase):

    def parts(self):
        if not self.content_type or not self.content_type.startswith("multipart/mixed"):
            raise ValueError(
                "You can't get parts if the response is not multipart/mixed"
            )

        responses = self._get_raw_parts()
        if self.request.multipart_mixed_info:
            policies = self.request.multipart_mixed_info[1]  # type: List[SansIOHTTPPolicy]

            # Apply on_response concurrently to all requests
            import concurrent.futures

            def parse_responses(response):
                http_request = response.request
                context = PipelineContext(None)
                pipeline_request = PipelineRequest(http_request, context)
                pipeline_response = PipelineResponse(
                    http_request, response, context=context
                )

                for policy in policies:
                    _await_result(policy.on_response, pipeline_request, pipeline_response)

            with concurrent.futures.ThreadPoolExecutor() as executor:
                # List comprehension to raise exceptions if happened
                [  # pylint: disable=expression-not-assigned, unnecessary-comprehension
                    _ for _ in executor.map(parse_responses, responses)
                ]

        return responses
