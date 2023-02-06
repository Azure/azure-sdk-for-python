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

from typing import TYPE_CHECKING, Generic, TypeVar, Union

from .. import PipelineRequest

if TYPE_CHECKING:
    from ..transport._base_async import AsyncHttpTransport


AsyncHTTPResponseTypeVar = TypeVar("AsyncHTTPResponseTypeVar")
HTTPResponseTypeVar = TypeVar("HTTPResponseTypeVar")
HTTPRequestTypeVar = TypeVar("HTTPRequestTypeVar")


class AsyncHTTPPolicy(abc.ABC, Generic[HTTPRequestTypeVar, AsyncHTTPResponseTypeVar]):
    """An async HTTP policy ABC.

    Use with an asynchronous pipeline.

    :param next: Use to process the next policy in the pipeline. Set when pipeline
     is instantiated and all policies chained.
    :type next: ~azure.core.pipeline.policies.AsyncHTTPPolicy or ~azure.core.pipeline.transport.AsyncHttpTransport
    """

    next: Union[
        "AsyncHTTPPolicy[HTTPRequestTypeVar, AsyncHTTPResponseTypeVar]",
        "AsyncHttpTransport[HTTPRequestTypeVar, AsyncHTTPResponseTypeVar]",
    ]
    """Pointer to the next policy or a transport. Will be set at pipeline creation."""

    @abc.abstractmethod
    async def send(self, request: PipelineRequest[HTTPRequestTypeVar]):
        """Abstract send method for a asynchronous pipeline. Mutates the request.

        Context content is dependent on the HttpTransport.

        :param request: The pipeline request object.
        :type request: ~azure.core.pipeline.PipelineRequest
        :return: The pipeline response object.
        :rtype: ~azure.core.pipeline.PipelineResponse
        """
