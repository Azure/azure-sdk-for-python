# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from __future__ import absolute_import
import os
from typing import cast, IO
from email.message import Message
from six.moves.http_client import HTTPConnection
try:
    binary_type = str
    from urlparse import urlparse  # type: ignore
except ImportError:
    binary_type = bytes  # type: ignore
    from urllib.parse import urlparse


def _format_parameters_helper(http_request, params):
    query = urlparse(http_request.url).query
    if query:
        http_request.url = http_request.url.partition("?")[0]
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
    http_request.url = http_request.url + query

def _pad_attr_name(attr, backcompat_attrs):
    return "_{}".format(attr) if attr in backcompat_attrs else attr

def _prepare_multipart_body_helper(http_response, content_index=0):
    if not http_response.multipart_mixed_info:
        return 0

    requests = http_response.multipart_mixed_info[0]  # type: List[HttpRequest]
    boundary = http_response.multipart_mixed_info[2]  # type: Optional[str]

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
    http_response.set_bytes_body(body)
    http_response.headers["Content-Type"] = (
        "multipart/mixed; boundary=" + main_message.get_boundary()
    )
    return content_index

class _HTTPSerializer(HTTPConnection, object):
    """Hacking the stdlib HTTPConnection to serialize HTTP request as strings.
    """

    def __init__(self, *args, **kwargs):
        self.buffer = b""
        kwargs.setdefault("host", "fakehost")
        super(_HTTPSerializer, self).__init__(*args, **kwargs)

    def putheader(self, header, *values):
        if header in ["Host", "Accept-Encoding"]:
            return
        super(_HTTPSerializer, self).putheader(header, *values)

    def send(self, data):
        self.buffer += data

def _serialize_request(http_request):
    serializer = _HTTPSerializer()
    serializer.request(
        method=http_request.method,
        url=http_request.url,
        body=http_request.body,
        headers=http_request.headers,
    )
    return serializer.buffer

def _format_data_helper(data):
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
