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
from collections.abc import AsyncIterator
import functools
import logging
from typing import Any, Callable, Union, Optional, AsyncIterator as AsyncIteratorType
import trio  # type: ignore
import urllib3  # type: ignore

import requests

from azure.core.exceptions import (
    ServiceRequestError,
    ServiceResponseError
)
from .base import HttpRequest
from .base_async import (
    AsyncHttpTransport,
    AsyncHttpResponse,
    _ResponseStopIteration,
    _iterate_response_content)
from .requests_basic import RequestsTransport, RequestsTransportResponse


_LOGGER = logging.getLogger(__name__)


class TrioStreamDownloadGenerator(AsyncIterator):

    def __init__(self, response: requests.Response, block_size: int) -> None:
        self.response = response
        self.block_size = block_size
        self.iter_content_func = self.response.iter_content(self.block_size)
        self.content_length = int(response.headers.get('Content-Length', 0))

    def __len__(self):
        return self.content_length

    async def __anext__(self):
        retry_active = True
        retry_total = 3
        while retry_active:
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
            except ServiceResponseError:
                retry_total -= 1
                if retry_total <= 0:
                    retry_active = False
                continue
            except Exception as err:
                _LOGGER.warning("Unable to stream download: %s", err)
                self.response.close()
                raise

class TrioRequestsTransportResponse(AsyncHttpResponse, RequestsTransportResponse):  # type: ignore

    def stream_download(self) -> AsyncIteratorType[bytes]:  # type: ignore
        """Generator for streaming request body data.

        :param callback: Custom callback for monitoring progress.
        :param int chunk_size:
        """
        return TrioStreamDownloadGenerator(self.internal_response, self.block_size) # type: ignore


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
        self.open()
        trio_limiter = kwargs.get("trio_limiter", None)
        response = None
        error = None # type: Optional[Union[ServiceRequestError, ServiceResponseError]]
        if self.config.proxy_policy and 'proxies' not in kwargs:
            kwargs['proxies'] = self.config.proxy_policy.proxies
        try:
            response = await trio.run_sync_in_worker_thread(
                functools.partial(
                    self.session.request, # type: ignore
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
            error = ServiceRequestError(err, error=err)
        except requests.exceptions.ReadTimeout as err:
            error = ServiceResponseError(err, error=err)
        except requests.exceptions.ConnectionError as err:
            if err.args and isinstance(err.args[0], urllib3.exceptions.ProtocolError):
                error = ServiceResponseError(err, error=err)
            else:
                error = ServiceRequestError(err, error=err)
        except requests.RequestException as err:
            error = ServiceRequestError(err, error=err)

        if error:
            raise error

        return TrioRequestsTransportResponse(request, response, self.config.connection.data_block_size)
