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
from collections.abc import AsyncIterator
import functools
import logging
from typing import Any, Callable, Optional, AsyncIterator as AsyncIteratorType

import requests
from requests.models import CONTENT_CHUNK_SIZE

from .base import HttpRequest
from .base_async import AsyncHttpTransport, AsyncHttpResponse
from .requests_basic import RequestsTransport, RequestsTransportResponse
from .requests_asyncio import _ResponseStopIteration, _iterate_response_content
from azure.core.exceptions import (
    ClientRequestError,
    raise_with_traceback)


_LOGGER = logging.getLogger(__name__)


import trio

class TrioStreamDownloadGenerator(AsyncIterator):

    def __init__(self, response: requests.Response, user_callback: Optional[Callable] = None, block: Optional[int] = None) -> None:
        self.response = response
        self.block = block or CONTENT_CHUNK_SIZE
        self.user_callback = user_callback
        self.iter_content_func = self.response.iter_content(self.block)

    async def __anext__(self):
        try:
            chunk = await trio.run_sync_in_worker_thread(
                _iterate_response_content,
                self.iter_content_func,
            )
            if not chunk:
                raise _ResponseStopIteration()
            if self.user_callback and callable(self.user_callback):
                self.user_callback(chunk, self.response)
            return chunk
        except _ResponseStopIteration:
            self.response.close()
            raise StopAsyncIteration()
        except Exception as err:
            _LOGGER.warning("Unable to stream download: %s", err)
            self.response.close()
            raise

class TrioRequestsTransportResponse(AsyncHttpResponse, RequestsTransportResponse):

    def stream_download(self, chunk_size: Optional[int] = None, callback: Optional[Callable] = None) -> AsyncIteratorType[bytes]:
        """Generator for streaming request body data.

        :param callback: Custom callback for monitoring progress.
        :param int chunk_size:
        """
        return TrioStreamDownloadGenerator(
            self.internal_response,
            callback,
            chunk_size
        )


class TrioRequestsTransport(RequestsTransport, AsyncHttpTransport):  # type: ignore

    async def __aenter__(self):
        return super(TrioRequestsTransport, self).__enter__()

    async def __aexit__(self, *exc_details):  # pylint: disable=arguments-differ
        return super(TrioRequestsTransport, self).__exit__()

    async def send(self, request: HttpRequest, **kwargs: Any) -> AsyncHttpResponse:  # type: ignore
        """Send the request using this HTTP sender.
        """
        trio_limiter = kwargs.get("trio_limiter", None)
        future = trio.run_sync_in_worker_thread(
            functools.partial(
                self.session.request,
                request.method,
                request.url,
                **kwargs
            ),
            limiter=trio_limiter
        )
        try:
            return TrioRequestsTransportResponse(
                request,
                await future
            )
        except requests.RequestException as err:
            msg = "Error occurred in request."
            raise_with_traceback(ClientRequestError, msg, err)
