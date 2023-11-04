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
from __future__ import annotations
import asyncio
import abc
from typing import TypeVar, Generic, Any, AsyncContextManager, TYPE_CHECKING

if TYPE_CHECKING:
    from ..rest import AsyncHttpResponse

AsyncHTTPResponseType = TypeVar("AsyncHTTPResponseType")
HTTPResponseType = TypeVar("HTTPResponseType")
HTTPRequestType = TypeVar("HTTPRequestType")


async def _handle_non_stream_rest_response(response: AsyncHttpResponse) -> None:
    """Handle reading and closing of non stream rest responses.
    For our new rest responses, we have to call .read() and .close() for our non-stream
    responses. This way, we load in the body for users to access.

    :param response: The response to read and close.
    :type response: ~corehttp.rest.AsyncHttpResponse
    """
    try:
        await response.read()
        await response.close()
    except Exception as exc:
        await response.close()
        raise exc


class _ResponseStopIteration(Exception):
    pass


class AsyncHttpTransport(
    AsyncContextManager["AsyncHttpTransport"],
    abc.ABC,
    Generic[HTTPRequestType, AsyncHTTPResponseType],
):
    """An http sender ABC."""

    @abc.abstractmethod
    async def send(self, request: HTTPRequestType, **kwargs: Any) -> AsyncHTTPResponseType:
        """Send the request using this HTTP sender.

        :param request: The request object. Exact type can be inferred from the pipeline.
        :type request: any
        :return: The response object. Exact type can be inferred from the pipeline.
        :rtype: any
        """

    @abc.abstractmethod
    async def open(self) -> None:
        """Assign new session if one does not already exist."""

    @abc.abstractmethod
    async def close(self) -> None:
        """Close the session if it is not externally owned."""

    async def sleep(self, duration: float) -> None:
        """Sleep for the specified duration.

        You should always ask the transport to sleep, and not call directly
        the stdlib. This is mostly important in async, as the transport
        may not use asyncio but other implementation like trio and they their own
        way to sleep, but to keep design
        consistent, it's cleaner to always ask the transport to sleep and let the transport
        implementor decide how to do it.
        By default, this method will use "asyncio", and don't need to be overridden
        if your transport does too.

        :param float duration: The number of seconds to sleep.
        """
        await asyncio.sleep(duration)
