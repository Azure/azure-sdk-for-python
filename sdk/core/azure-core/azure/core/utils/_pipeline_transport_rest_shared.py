# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from __future__ import absolute_import
from typing import TYPE_CHECKING
from email.message import Message

from azure.core.pipeline import (
    PipelineRequest,
    PipelineResponse,
    PipelineContext,
)
from ..pipeline._tools import await_result as _await_result

try:
    from email import message_from_bytes as message_parser
except ImportError:  # 2.7
    from email import message_from_string as message_parser  # type: ignore

try:
    binary_type = str
    from urlparse import urlparse  # type: ignore
except ImportError:
    binary_type = bytes  # type: ignore
    from urllib.parse import urlparse

if TYPE_CHECKING:
    from typing import List, Optional  # pylint: disable=ungrouped-imports
    from ..pipeline.policies import SansIOHTTPPolicy

def _decode_parts_helper(
    http_response, message, http_response_type, requests, deserialize_response_callable
):
    responses = []
    for index, raw_reponse in enumerate(message.get_payload()):
        content_type = raw_reponse.get_content_type()
        if content_type == "application/http":
            responses.append(
                deserialize_response_callable(
                    raw_reponse.get_payload(decode=True),
                    requests[index],
                    http_response_type=http_response_type,
                )
            )
        elif content_type == "multipart/mixed" and requests[index].multipart_mixed_info:
            # The message batch contains one or more change sets
            changeset_requests = requests[index].multipart_mixed_info[0]  # type: ignore
            changeset_responses = http_response._decode_parts(  # pylint: disable=protected-access
                raw_reponse,
                http_response_type,
                changeset_requests
            )
            responses.extend(changeset_responses)
        else:
            raise ValueError(
                "Multipart doesn't support part other than application/http for now"
            )
    return responses

def _get_raw_parts_helper(http_response, http_response_type, default_http_response_type):
    if http_response_type is None:
        http_response_type = default_http_response_type

    body_as_bytes = http_response.body()
    # In order to use email.message parser, I need full HTTP bytes. Faking something to make the parser happy
    http_body = (
        b"Content-Type: "
        + http_response.content_type.encode("ascii")
        + b"\r\n\r\n"
        + body_as_bytes
    )
    message = message_parser(http_body)  # type: Message
    requests = http_response.request.multipart_mixed_info[0]  # type: List[HttpRequest]
    return http_response._decode_parts(message, http_response_type, requests)  # pylint: disable=protected-access

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

def _parts_helper(http_response):
    if not http_response.content_type or not http_response.content_type.startswith("multipart/mixed"):
        raise ValueError(
            "You can't get parts if the response is not multipart/mixed"
        )

    responses = http_response._get_raw_parts()  # pylint: disable=protected-access
    if http_response.request.multipart_mixed_info:
        policies = http_response.request.multipart_mixed_info[1]  # type: List[SansIOHTTPPolicy]

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
