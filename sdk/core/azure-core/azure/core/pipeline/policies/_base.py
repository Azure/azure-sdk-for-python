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

import abc
import copy
import logging

from typing import (
    Generic,
    TypeVar,
    Union,
    Any,
    Dict,
    Optional,
)  # pylint: disable=unused-import

try:
    from typing import Awaitable   # pylint: disable=unused-import
except ImportError:
    pass

from azure.core.pipeline import ABC, PipelineRequest, PipelineResponse


HTTPResponseType = TypeVar("HTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")

_LOGGER = logging.getLogger(__name__)

class HTTPPolicy(ABC, Generic[HTTPRequestType, HTTPResponseType]):
    """An HTTP policy ABC.

    Use with a synchronous pipeline.

    :param next: Use to process the next policy in the pipeline. Set when pipeline is
     instantiated and all policies chained.
    :type next: ~azure.core.pipeline.policies.HTTPPolicy or ~azure.core.pipeline.transport.HttpTransport
    """

    def __init__(self):
        self.next = None # type: Union[HTTPPolicy, HttpTransport]

    @abc.abstractmethod
    def send(self, request):
        # type: (PipelineRequest) -> PipelineResponse
        """Abstract send method for a synchronous pipeline. Mutates the request.

        Context content is dependent on the HttpTransport.

        :param request: The pipeline request object
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The pipeline response object.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """


class SansIOHTTPPolicy(Generic[HTTPRequestType, HTTPResponseType]):
    """Represents a sans I/O policy.

    SansIOHTTPPolicy is a base class for policies that only modify or
    mutate a request based on the HTTP specification, and do no depend
    on the specifics of any particular transport. SansIOHTTPPolicy
    subclasses will function in either a Pipeline or an AsyncPipeline,
    and can act either before the request is done, or after.
    You can optionally make these methods coroutines (or return awaitable objects)
    but they will then be tied to AsyncPipeline usage.
    """

    def on_request(self, request):
        # type: (PipelineRequest) -> Union[None, Awaitable[None]]
        """Is executed before sending the request from next policy.

        :param request: Request to be modified before sent from next policy.
        :type request: ~azure.core.pipeline.PipelineRequest
        """

    def on_response(self, request, response):
        # type: (PipelineRequest, PipelineResponse) -> Union[None, Awaitable[None]]
        """Is executed after the request comes back from the policy.

        :param request: Request to be modified after returning from the policy.
        :type request: ~azure.core.pipeline.PipelineRequest
        :param response: Pipeline response object
        :type response: ~azure.core.pipeline.PipelineResponse
        """

    # pylint: disable=no-self-use
    def on_exception(self, request):  # pylint: disable=unused-argument
        # type: (PipelineRequest) -> Union[bool, Awaitable[bool]]
        """Is executed if an exception is raised while executing the next policy.

        Developer can optionally implement this method to return True
        if the exception has been handled and should not be forwarded to the caller.

        This method is executed inside the exception handler.

        :param request: The Pipeline request object
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: False by default, override with True to stop the exception.
        :rtype: bool

        .. admonition:: Example:

            .. literalinclude:: ../samples/test_example_sansio.py
                :start-after: [START on_exception]
                :end-before: [END on_exception]
                :language: python
                :dedent: 4
        """
        return False


class RequestHistory(object):
    """A container for an attempted request and the applicable response.

    This is used to document requests/responses that resulted in redirected/retried requests.

    :param http_request: The request.
    :type http_request: ~azure.core.pipeline.transport.HttpRequest
    :param http_response: The HTTP response.
    :type http_response: ~azure.core.pipeline.transport.HttpResponse
    :param Exception error: An error encountered during the request, or None if the response was received successfully.
    :param dict context: The pipeline context.
    """

    def __init__(self, http_request, http_response=None, error=None, context=None):
        # type: (HTTPRequestType, Optional[HTTPResponseType], Exception, Optional[Dict[str, Any]]) -> None
        self.http_request = copy.deepcopy(http_request)
        self.http_response = http_response
        self.error = error
        self.context = context
