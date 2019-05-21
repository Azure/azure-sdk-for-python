
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

from typing import Generic, TypeVar, Any, List, Union, Callable, AsyncIterator, Optional

from azure.core.pipeline import PipelineRequest, PipelineResponse

try:
    from contextlib import AbstractAsyncContextManager  # type: ignore
except ImportError: # Python <= 3.7
    class AbstractAsyncContextManager(object):  # type: ignore
        async def __aenter__(self):
            """Return `self` upon entering the runtime context."""
            return self

        @abc.abstractmethod
        async def __aexit__(self, exc_type, exc_value, traceback):
            """Raise any exception triggered within the runtime context."""
            return None


AsyncHTTPResponseType = TypeVar("AsyncHTTPResponseType")
HTTPResponseType = TypeVar("HTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")


class AsyncHTTPPolicy(abc.ABC, Generic[HTTPRequestType, AsyncHTTPResponseType]):
    """An async HTTP policy ABC.
    """
    def __init__(self) -> None:
        # next will be set once in the pipeline
        self.next = None  # type: Optional[Union[AsyncHTTPPolicy[HTTPRequestType, AsyncHTTPResponseType], AsyncHttpTransport[HTTPRequestType, AsyncHTTPResponseType]]]

    @abc.abstractmethod
    async def send(self, request: PipelineRequest):
        """Mutate the request.

        Context content is dependent on the HttpTransport.
        """
        pass