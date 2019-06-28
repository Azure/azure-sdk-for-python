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

import asyncio
import abc

from typing import Any, List, Union, Callable, AsyncIterator, Optional, Generic, TypeVar
from azure.core.pipeline import PipelineRequest, PipelineResponse, Pipeline
from azure.core.pipeline.policies import SansIOHTTPPolicy
from .base import _HttpResponseBase

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


class _ResponseStopIteration(Exception):
    pass


def _iterate_response_content(iterator):
    """"To avoid:
    TypeError: StopIteration interacts badly with generators and cannot be raised into a Future
    """
    try:
        return next(iterator)
    except StopIteration:
        raise _ResponseStopIteration()


class AsyncHttpResponse(_HttpResponseBase):
    """An AsyncHttpResponse ABC.

    Allows for the asynchronous streaming of data from the response.
    """
    def stream_download(self, pipeline) -> AsyncIterator[bytes]:
        """Generator for streaming response body data.

        Should be implemented by sub-classes if streaming download
        is supported. Will return an asynchronous generator.

        :param pipeline: The pipeline object
        :type pipeline: azure.core.pipeline
        """


class AsyncHttpTransport(AbstractAsyncContextManager, abc.ABC, Generic[HTTPRequestType, AsyncHTTPResponseType]):
    """An http sender ABC.
    """

    @abc.abstractmethod
    async def send(self, request, **kwargs):
        """Send the request using this HTTP sender.
        """

    @abc.abstractmethod
    async def open(self):
        """Assign new session if one does not already exist."""

    @abc.abstractmethod
    async def close(self):
        """Close the session if it is not externally owned."""

    async def sleep(self, duration):
        await asyncio.sleep(duration)

    def __enter__(self):
        raise TypeError("Use async with instead")

    def __exit__(self, exc_type, exc_val, exc_tb):
        # __exit__ should exist in pair with __enter__ but never executed
        pass  # pragma: no cover
