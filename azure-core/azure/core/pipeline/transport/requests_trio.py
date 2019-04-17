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
import urllib3
from typing import Any, Callable, Optional, AsyncIterator as AsyncIteratorType

import requests
from requests.models import CONTENT_CHUNK_SIZE

from .base import HttpRequest
from .base_async import (
    AsyncHttpTransport,
    AsyncHttpResponse,
    _ResponseStopIteration,
    _iterate_response_content)
from .requests_basic import RequestsTransport, RequestsTransportResponse
from azure.core.exceptions import (
    ServiceRequestError,
    ServiceResponseError,
    ConnectError,
    ReadTimeoutError,
    raise_with_traceback
)


_LOGGER = logging.getLogger(__name__)


import trio

class TrioStreamDownloadGenerator(AsyncIterator):

    def __init__(self, response: requests.Response, block_size: int) -> None:
        self.response = response
        self.block_size = block_size
        self.iter_content_func = self.response.iter_content(self.block_size)
        self.content_length = int(response.headers.get('Content-Length', 0))

    def __len__(self):
        return self.content_length

    async def __anext__(self):
        try:
            chunk = await trio.run_sync_in_worker_thread(
                _iterate_response_content,
                self.iter_content_func,
            )
            if not chunk:
                raise _ResponseStopIteration()
            return chunk
        except _ResponseStopIteration:
            self.response.close()
            raise StopAsyncIteration()
        except Exception as err:
            _LOGGER.warning("Unable to stream download: %s", err)
            self.response.close()
            raise

class TrioRequestsTransportResponse(AsyncHttpResponse, RequestsTransportResponse):

    def stream_download(self) -> AsyncIteratorType[bytes]:
        """Generator for streaming request body data.

        :param callback: Custom callback for monitoring progress.
        :param int chunk_size:
        """
        return TrioStreamDownloadGenerator(self.internal_response, self.block_size)


class TrioRequestsTransport(RequestsTransport, AsyncHttpTransport):  # type: ignore

    async def __aenter__(self):
        return super(TrioRequestsTransport, self).__enter__()

    async def __aexit__(self, *exc_details):  # pylint: disable=arguments-differ
        return super(TrioRequestsTransport, self).__exit__()

    async def sleep(self, duration):
        await trio.sleep(duration)

    async def send(self, request: HttpRequest, **kwargs: Any) -> AsyncHttpResponse:  # type: ignore
        """Send the request using this HTTP sender.
        """
        trio_limiter = kwargs.get("trio_limiter", None)
        response = None
        error = None
        if self.config.proxy_policy and 'proxies' not in kwargs:
            kwargs['proxies'] = self.config.proxy_policy.proxies
        try:
            response = await trio.run_sync_in_worker_thread(
                functools.partial(
                    self.session.request,
                    request.method,
                    request.url,
                    headers=request.headers,
                    data=request.data,
                    files=request.files,
                    verify=kwargs.get('connection_verify', self.config.connection.verify),
                    timeout=kwargs.get('connection_timeout', self.config.connection.timeout),
                    cert=kwargs.get('connection_cert', self.config.connection.cert),
                    allow_redirects=False,
                    **kwargs),
                limiter=trio_limiter)

        except urllib3.exceptions.NewConnectionError as err:
            error = ConnectError(err, error=err)
        except requests.exceptions.ReadTimeout as err:
            error = ReadTimeoutError(err, error=err)
        except requests.exceptions.ConnectionError as err:
            if err.args and isinstance(err.args[0], urllib3.exceptions.ProtocolError):
                error = ServiceResponseError(err, error=err)
            else:
                error = ConnectError(err, error=err)
        except requests.RequestException as err:
            error = ServiceRequestError(err, error=err)
        finally:
            if not self.config.connection.keep_alive and (not response or not kwargs['stream']):
                self.session.close()
        if error:
            raise error

        return TrioRequestsTransportResponse(request, response, self.config.connection.data_block_size)
