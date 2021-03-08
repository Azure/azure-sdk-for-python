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
from ..pipeline.transport._base import (
    _case_insensitive_dict,
    _serialize_request
)
import copy
from email.message import Message
from typing import (
    cast,
    Any,
    Dict,
    Mapping,
    Optional,
    Tuple,
    Union,
    IO,
    Generator,
    AsyncGenerator
)

import xml.etree.ElementTree as ET
try:
    binary_type = str
    from urlparse import urlparse  # type: ignore
except ImportError:
    binary_type = bytes  # type: ignore
    from urllib.parse import urlparse

class HttpRequest(object):
    """Represents a HTTP request.

    URL can be given without query parameters, to be added later using "format_parameters".

    :param str method: HTTP method (GET, HEAD, etc.)
    :param str url: At least complete scheme/host/path
    :param dict[str,str] headers: HTTP headers
    :param any files: Files list.
    :param data: Body to be sent.
    :type data: bytes or str
    """

    def __init__(self, method, url, headers=None, files=None, data=None):
        # type: (str, str, Mapping[str, str], Any, Any) -> None
        self.method = method
        self.url = url
        self.headers = _case_insensitive_dict(headers)
        self.files = files
        self.data = data
        self.multipart_mixed_info = None  # type: Optional[Tuple]

    def __repr__(self):
        return "<HttpRequest [{}], url: '{}'>".format(
            self.method, self.url
        )

    def __deepcopy__(self, memo=None):
        try:
            data = copy.deepcopy(self.body, memo)
            files = copy.deepcopy(self.files, memo)
            return HttpRequest(self.method, self.url, self.headers, files, data)
        except (ValueError, TypeError):
            return copy.copy(self)

    @property
    def query(self):
        """The query parameters of the request as a dict.

        :rtype: dict[str, str]
        """
        query = urlparse(self.url).query
        if query:
            return {p[0]: p[-1] for p in [p.partition("=") for p in query.split("&")]}
        return {}

    @property
    def body(self):
        # type: () -> bytes
        """Alias to data.

        :rtype: bytes
        """
        return self.data

    @body.setter
    def body(self, value):
        # type: (bytes) -> None
        self.data = value

    @staticmethod
    def _format_data(data):
        # type: (Union[str, IO]) -> Union[Tuple[None, str], Tuple[Optional[str], IO, str]]
        """Format field data according to whether it is a stream or
        a string for a form-data request.

        :param data: The request field data.
        :type data: str or file-like object.
        """
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
        # type: (Dict[str, str]) -> None
        """Format parameters into a valid query string.
        It's assumed all parameters have already been quoted as
        valid URL strings.

        :param dict params: A dictionary of parameters.
        """
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
        # type: (Union[bytes, Generator, AsyncGenerator]) -> None
        """Set a streamable data body.

        :param data: The request field data.
        :type data: stream or generator or asyncgenerator
        """
        if not isinstance(data, binary_type) and not any(
            hasattr(data, attr) for attr in ["read", "__iter__", "__aiter__"]
        ):
            raise TypeError(
                "A streamable data source must be an open file-like object or iterable."
            )
        self.data = data
        self.files = None

    def set_text_body(self, data):
        # type: (str) -> None
        """Set a text as body of the request.

        :param data: A text to send as body.
        :type data: str
        """
        if data is None:
            self.data = None
        else:
            self.data = data
            self.headers["Content-Length"] = str(len(self.data))
        self.files = None

    def set_xml_body(self, data):
        # type: (Optional[ET]) -> None
        """Set an XML element tree as the body of the request.

        :param data: The request field data.
        :type data: XML node
        """
        if data is None:
            self.data = None
        else:
            bytes_data = ET.tostring(data, encoding="utf8")
            self.data = bytes_data.replace(b"encoding='utf8'", b"encoding='utf-8'")
            self.headers["Content-Length"] = str(len(self.data))
        self.files = None

    def set_json_body(self, data):
        # type: (Any) -> None
        """Set a JSON-friendly object as the body of the request.

        :param any data: A JSON serializable object
        """
        if data is None:
            self.data = None
        else:
            self.data = json.dumps(data)
            self.headers["Content-Length"] = str(len(self.data))
        self.files = None

    def set_formdata_body(self, data=None):
        # type: (Dict[str, Any]) -> None
        """Set form-encoded data as the body of the request.

        :param data: The request field data.
        :type data: dict
        """
        if data is None:
            data = {}
        content_type = self.headers.pop("Content-Type", None) if self.headers else None

        if content_type and content_type.lower() == "application/x-www-form-urlencoded":
            self.data = {f: d for f, d in data.items() if d is not None}
            self.files = None
        else:  # Assume "multipart/form-data"
            self.files = {
                f: self._format_data(d) for f, d in data.items() if d is not None
            }
            self.data = None

    def set_bytes_body(self, data):
        # type: (bytes) -> None
        """Set generic bytes as the body of the request.

        Will set content-length.

        :param data: The request field data.
        :type data: bytes
        """
        if data:
            self.headers["Content-Length"] = str(len(data))
        self.data = data
        self.files = None

    def set_multipart_mixed(self, *requests, **kwargs):
        # type: (HttpRequest, Any) -> None
        """Set the part of a multipart/mixed.

        Only supported args for now are HttpRequest objects.

        boundary is optional, and one will be generated if you don't provide one.
        Note that no verification are made on the boundary, this is considered advanced
        enough so you know how to respect RFC1341 7.2.1 and provide a correct boundary.

        Any additional kwargs will be passed into the pipeline context for per-request policy
        configuration.

        :keyword list[SansIOHTTPPolicy] policies: SansIOPolicy to apply at preparation time
        :keyword str boundary: Optional boundary
        :param requests: HttpRequests object
        :type requests: list[~azure.core.protocol.HttpRequest]
        """
        self.multipart_mixed_info = (
            requests,
            kwargs.pop("policies", []),
            kwargs.pop("boundary", None),
            kwargs
        )

    def prepare_multipart_body(self, content_index=0):
        # type: (int) -> int
        """Will prepare the body of this request according to the multipart information.

        This call assumes the on_request policies have been applied already in their
        correct context (sync/async)

        Does nothing if "set_multipart_mixed" was never called.

        :param int content_index: The current index of parts within the batch message.
        :returns: The updated index after all parts in this request have been added.
        :rtype: int
        """
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