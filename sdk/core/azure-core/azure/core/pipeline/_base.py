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

import logging
from typing import Generic, TypeVar, List, Union, Any, Dict
from email.message import Message
from six.moves.http_client import HTTPConnection
from azure.core.pipeline import (
    AbstractContextManager,
    PipelineRequest,
    PipelineResponse,
    PipelineContext,
)
from azure.core.pipeline.policies import HTTPPolicy, SansIOHTTPPolicy
from ._tools import await_result as _await_result

HTTPResponseType = TypeVar("HTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")
HttpTransportType = TypeVar("HttpTransportType")

_LOGGER = logging.getLogger(__name__)
PoliciesType = List[Union[HTTPPolicy, SansIOHTTPPolicy]]

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

def serialize(request):
    serializer = _HTTPSerializer()
    serializer.request(
        method=request.method,
        url=request.url,
        body=request.content,
        headers=request.headers
    )
    return serializer.buffer

def prepare_multipart_body(request, content_index=0):

    # code taken from here https://github.com/Azure/azure-sdk-for-python/blob/4ee53d07a14b8c76af01768ad98068d8a2766f54/sdk/core/azure-core/azure/core/pipeline/transport/_base.py#L406
    if not hasattr(request, "requests"):
        return 0

    requests = request.requests  # type: List[HttpRequest]
    boundary = request.boundary  # type: Optional[str]

    # Update the main request with the body
    main_message = Message()
    main_message.add_header("Content-Type", "multipart/mixed")
    if boundary:
        main_message.set_boundary(boundary)

    for req in requests:
        part_message = Message()
        if hasattr(req, "requests"):
            content_index = prepare_multipart_body(req, content_index=content_index)
            part_message.add_header("Content-Type", request.headers['Content-Type'])
            payload = serialize(request)
            # We need to remove the ~HTTP/1.1 prefix along with the added content-length
            payload = payload[payload.index(b'--'):]
        else:
            part_message.add_header("Content-Type", "application/http")
            part_message.add_header("Content-Transfer-Encoding", "binary")
            part_message.add_header("Content-ID", str(content_index))
            payload = serialize(req)
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
    request._data = body
    request.headers["Content-Type"] = (
        "multipart/mixed; boundary=" + main_message.get_boundary()
    )
    return content_index


class _SansIOHTTPPolicyRunner(HTTPPolicy, Generic[HTTPRequestType, HTTPResponseType]):
    """Sync implementation of the SansIO policy.

    Modifies the request and sends to the next policy in the chain.

    :param policy: A SansIO policy.
    :type policy: ~azure.core.pipeline.policies.SansIOHTTPPolicy
    """

    def __init__(self, policy):
        # type: (SansIOHTTPPolicy) -> None
        super(_SansIOHTTPPolicyRunner, self).__init__()
        self._policy = policy

    def send(self, request):
        # type: (PipelineRequest) -> PipelineResponse
        """Modifies the request and sends to the next policy in the chain.

        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The PipelineResponse object.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        _await_result(self._policy.on_request, request)
        try:
            response = self.next.send(request)
        except Exception:  # pylint: disable=broad-except
            if not _await_result(self._policy.on_exception, request):
                raise
        else:
            _await_result(self._policy.on_response, request, response)
        return response


class _TransportRunner(HTTPPolicy):
    """Transport runner.

    Uses specified HTTP transport type to send request and returns response.

    :param sender: The Http Transport instance.
    """

    def __init__(self, sender):
        # type: (HttpTransportType) -> None
        super(_TransportRunner, self).__init__()
        self._sender = sender

    def send(self, request):
        """HTTP transport send method.

        :param request: The PipelineRequest object.
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The PipelineResponse object.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        return PipelineResponse(
            request.http_request,
            self._sender.send(request.http_request, **request.context.options),
            context=request.context,
        )


class Pipeline(AbstractContextManager, Generic[HTTPRequestType, HTTPResponseType]):
    """A pipeline implementation.

    This is implemented as a context manager, that will activate the context
    of the HTTP sender. The transport is the last node in the pipeline.

    :param transport: The Http Transport instance
    :param list policies: List of configured policies.

    .. admonition:: Example:

        .. literalinclude:: ../samples/test_example_sync.py
            :start-after: [START build_pipeline]
            :end-before: [END build_pipeline]
            :language: python
            :dedent: 4
            :caption: Builds the pipeline for synchronous transport.
    """

    def __init__(self, transport, policies=None):
        # type: (HttpTransportType, PoliciesType) -> None
        self._impl_policies = []  # type: List[HTTPPolicy]
        self._transport = transport

        for policy in policies or []:
            if isinstance(policy, SansIOHTTPPolicy):
                self._impl_policies.append(_SansIOHTTPPolicyRunner(policy))
            elif policy:
                self._impl_policies.append(policy)
        for index in range(len(self._impl_policies) - 1):
            self._impl_policies[index].next = self._impl_policies[index + 1]
        if self._impl_policies:
            self._impl_policies[-1].next = _TransportRunner(self._transport)

    def __enter__(self):
        # type: () -> Pipeline
        self._transport.__enter__()  # type: ignore
        return self

    def __exit__(self, *exc_details):  # pylint: disable=arguments-differ
        self._transport.__exit__(*exc_details)

    @staticmethod
    def _prepare_multipart_mixed_request(request):
        # type: (HTTPRequestType) -> None
        """Will execute the multipart policies.

        Does nothing if "set_multipart_mixed" was never called.
        """
        if not hasattr(request, "requests"):
            return

        requests = request.requests  # type: List[HTTPRequestType]
        policies = request.policies  # type: List[SansIOHTTPPolicy]
        pipeline_options = request.kwargs  # type: Dict[str, Any]

        # Apply on_requests concurrently to all requests
        import concurrent.futures

        def prepare_requests(req):
            if hasattr(request, "requests"):
                # Recursively update changeset "sub requests"
                Pipeline._prepare_multipart_mixed_request(req)
            context = PipelineContext(None, **pipeline_options)
            pipeline_request = PipelineRequest(req, context)
            for policy in policies:
                _await_result(policy.on_request, pipeline_request)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # List comprehension to raise exceptions if happened
            [  # pylint: disable=expression-not-assigned, unnecessary-comprehension
                _ for _ in executor.map(prepare_requests, requests)
            ]

    def _prepare_multipart(self, request):
        # type: (HTTPRequestType) -> None
        # This code is fine as long as HTTPRequestType is actually
        # azure.core.pipeline.transport.HTTPRequest, bu we don't check it in here
        # since we didn't see (yet) pipeline usage where it's not this actual instance
        # class used
        self._prepare_multipart_mixed_request(request)
        prepare_multipart_body(request)  # type: ignore

    def run(self, request, **kwargs):
        # type: (HTTPRequestType, Any) -> PipelineResponse
        """Runs the HTTP Request through the chained policies.

        :param request: The HTTP request object.
        :type request: ~azure.core.pipeline.transport.HttpRequest
        :return: The PipelineResponse object
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
        self._prepare_multipart(request)
        context = PipelineContext(self._transport, **kwargs)
        pipeline_request = PipelineRequest(
            request, context
        )  # type: PipelineRequest[HTTPRequestType]
        first_node = (
            self._impl_policies[0]
            if self._impl_policies
            else _TransportRunner(self._transport)
        )
        return first_node.send(pipeline_request)  # type: ignore
