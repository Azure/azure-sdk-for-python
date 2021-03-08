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
from ..pipeline.transport._base import (
    _deserialize_response,
    HttpClientTransportResponse,
    PipelineType,
)
from ..pipeline.policies import SansIOHTTPPolicy
from ..exceptions import HttpResponseError
from typing import (
    Any,
    Optional,
    MutableMapping,
    List,
    Type,
    Iterator,
)
from email.message import Message
from ._http_request import HttpRequest
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

class _HttpResponseBase(object):
    """Represent a HTTP response.

    No body is defined here on purpose, since async pipeline
    will provide async ways to access the body
    Full in-memory using "body" as bytes.

    :param request: The request.
    :type request: ~azure.core.protocol.HttpRequest
    :param internal_response: The object returned from the HTTP library.
    :type internal_response: any
    :param block_size: Defaults to 4096 bytes.
    :type block_size: optional[int]
    """

    def __init__(self, request, internal_response, block_size=None):
        # type: (HttpRequest, Any, Optional[int]) -> None
        self.request = request
        self.internal_response = internal_response
        self.status_code = None  # type: Optional[int]
        self.headers = {}  # type: MutableMapping[str, str]
        self.reason = None  # type: Optional[str]
        self.content_type = None  # type: Optional[str]
        self.block_size = block_size or 4096  # Default to same as Requests

    def body(self):
        # type: () -> bytes
        """Return the whole body as bytes in memory.
        """
        raise NotImplementedError()

    def text(self, encoding=None):
        # type: (str) -> str
        """Return the whole body as a string.

        :param str encoding: The encoding to apply. If None, use "utf-8" with BOM parsing (utf-8-sig).
         Implementation can be smarter if they want (using headers or chardet).
        """
        if encoding == "utf-8" or encoding is None:
            encoding = "utf-8-sig"
        return self.body().decode(encoding)

    def _decode_parts(self, message, http_response_type, requests):
        # type: (Message, Type[_HttpResponseBase], List[HttpRequest]) -> List[HttpResponse]
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
        # type (Optional[Type[_HttpResponseBase]]) -> Iterator[HttpResponse]
        """Assuming this body is multipart, return the iterator or parts.

        If parts are application/http use http_response_type or HttpClientTransportResponse
        as enveloppe.
        """
        if http_response_type is None:
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

    def raise_for_status(self):
        # type () -> None
        """Raises an HttpResponseError if the response has an error status code.
        If response is good, does nothing.
        """
        if self.status_code >= 400:
            raise HttpResponseError(response=self)

    def __repr__(self):
        # there doesn't have to be a content type
        content_type_str = (
            ", Content-Type: {}".format(self.content_type) if self.content_type else ""
        )
        return "<{}: {} {}{}>".format(
            type(self).__name__, self.status_code, self.reason, content_type_str
        )

class HttpResponse(_HttpResponseBase):  # pylint: disable=abstract-method
    def stream_download(self, pipeline):
        # type: (PipelineType) -> Iterator[bytes]
        """Generator for streaming request body data.

        Should be implemented by sub-classes if streaming download
        is supported.

        :param PipelineType pipeline: The type of pipeline
        :rtype: Iterator[bytes]
        """

    def parts(self):
        # type: () -> Iterator[HttpResponse]
        """Assuming the content-type is multipart/mixed, will return the parts as an iterator.

        :rtype: Iterator[~azure.core.protocol.HttpResponse]
        :raises ValueError: If the content is not multipart/mixed
        """
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
