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
from typing import Any, Optional, AsyncIterator as AsyncIteratorType
from collections.abc import AsyncIterator

import logging
import asyncio
import aiohttp

from azure.core.configuration import Configuration
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline import Pipeline

from requests.exceptions import (
    ChunkedEncodingError,
    StreamConsumedError)

from .base import HttpRequest
from .base_async import (
    AsyncHttpTransport,
    AsyncHttpResponse,
    _ResponseStopIteration)

# Matching requests, because why not?
CONTENT_CHUNK_SIZE = 10 * 1024
_LOGGER = logging.getLogger(__name__)


class AioHttpTransport(AsyncHttpTransport):
    """AioHttp HTTP sender implementation.

    Fully asynchronous implementation using the aiohttp library.

    :param configuration: The service configuration.
    :type configuration: ~azure.core.Configuration
    :param session: The client session.
    :param loop: The event loop.
    :param bool session_owner: Session owner. Defaults True.
    """
    def __init__(self, configuration=None, *, session=None, loop=None, session_owner=True):
        self._loop = loop
        self._session_owner = session_owner
        self.session = session
        self.config = configuration or Configuration()

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, *args):  # pylint: disable=arguments-differ
        await self.close()

    async def open(self):
        """Opens the connection.
        """
        if not self.session and self._session_owner:
            self.session = aiohttp.ClientSession(loop=self._loop)
        if self.session is not None:
            await self.session.__aenter__()

    async def close(self):
        """Closes the connection.
        """
        if self._session_owner and self.session:
            await self.session.close()
            self._session_owner = False
            self.session = None

    def _build_ssl_config(self, **config):
        verify = config.get('connection_verify', self.config.connection.verify)
        cert = config.get('connection_cert', self.config.connection.cert)
        ssl_ctx = None

        if cert or verify not in (True, False):
            import ssl
            if verify not in (True, False):
                ssl_ctx = ssl.create_default_context(cafile=verify)
            else:
                ssl_ctx = ssl.create_default_context()
            if cert:
                ssl_ctx.load_cert_chain(*cert)
            return ssl_ctx
        return verify

    def _get_request_data(self, request): #pylint: disable=no-self-use
        if request.files:
            form_data = aiohttp.FormData()
            for form_file, data in request.files.items():
                content_type = data[2] if len(data) > 2 else None
                try:
                    form_data.add_field(form_file, data[1], filename=data[0], content_type=content_type)
                except IndexError:
                    raise ValueError("Invalid formdata formatting: {}".format(data))
            return form_data
        return request.data

    async def send(self, request: HttpRequest, **config: Any) -> Optional[AsyncHttpResponse]:
        """Send the request using this HTTP sender.

        Will pre-load the body into memory to be available with a sync method.
        Pass stream=True to avoid this behavior.

        :param request: The HttpRequest object
        :type request: ~azure.core.pipeline.transport.HttpRequest
        :param config: Any keyword arguments
        :return: The AsyncHttpResponse
        :rtype: ~azure.core.pipeline.transport.AsyncHttpResponse

        **Keyword argument:**

        *stream (bool)* - Defaults to False.
        """
        await self.open()
        error = None
        response = None
        config['ssl'] = self._build_ssl_config(**config)
        try:
            stream_response = config.pop("stream", False)
            result = await self.session.request(
                request.method,
                request.url,
                headers=request.headers,
                data=self._get_request_data(request),
                timeout=config.get('connection_timeout', self.config.connection.timeout),
                allow_redirects=False,
                **config
            )
            response = AioHttpTransportResponse(request, result, self.config.connection.data_block_size)
            if not stream_response:
                await response.load_body()
        except aiohttp.client_exceptions.ClientConnectorError as err:
            error = ServiceRequestError(err, error=err)

        if error:
            raise error
        return response


class AioHttpStreamDownloadGenerator(AsyncIterator):
    """Streams the response body data.

    :param pipeline: The pipeline object
    :param request: The request object
    :param response: The client response object.
    :type response: aiohttp.ClientResponse
    :param block_size: block size of data sent over connection.
    :type block_size: int
    """
    def __init__(self, pipeline: Pipeline, request: HttpRequest,
                 response: aiohttp.ClientResponse, block_size: int) -> None:
        self.pipeline = pipeline
        self.request = request
        self.response = response
        self.block_size = block_size
        self.content_length = int(response.headers.get('Content-Length', 0))
        self.downloaded = 0

    def __len__(self):
        return self.content_length

    async def __anext__(self):
        retry_active = True
        retry_total = 3
        retry_interval = 1000
        while retry_active:
            try:
                chunk = await self.response.content.read(self.block_size)
                if not chunk:
                    raise _ResponseStopIteration()
                self.downloaded += self.block_size
                return chunk
            except _ResponseStopIteration:
                self.response.close()
                raise StopAsyncIteration()
            except (ChunkedEncodingError, ConnectionError):
                retry_total -= 1
                if retry_total <= 0:
                    retry_active = False
                else:
                    await asyncio.sleep(retry_interval)
                    headers = {'range': 'bytes=' + self.downloaded + '-'}
                    resp = self.pipeline.run(self.request, stream=True, headers=headers)
                    if resp.status_code == 416:
                        raise
                    chunk = await self.response.content.read(self.block_size)
                    if not chunk:
                        raise StopIteration()
                    self.downloaded += chunk
                    return chunk
                continue
            except StreamConsumedError:
                raise
            except Exception as err:
                _LOGGER.warning("Unable to stream download: %s", err)
                self.response.close()
                raise

class AioHttpTransportResponse(AsyncHttpResponse):
    """Methods for accessing response body data.

    :param request: The HttpRequest object
    :type request: ~azure.core.pipeline.transport.HttpRequest
    :param aiohttp_response: Returned from ClientSession.request().
    :type aiohttp_response: aiohttp.ClientResponse object
    :param block_size: block size of data sent over connection.
    :type block_size: int
    """
    def __init__(self, request: HttpRequest, aiohttp_response: aiohttp.ClientResponse, block_size=None) -> None:
        super(AioHttpTransportResponse, self).__init__(request, aiohttp_response, block_size=block_size)
        # https://aiohttp.readthedocs.io/en/stable/client_reference.html#aiohttp.ClientResponse
        self.status_code = aiohttp_response.status
        self.headers = aiohttp_response.headers
        self.reason = aiohttp_response.reason
        self.content_type = aiohttp_response.headers.get('content-type')
        self._body = None

    def body(self) -> bytes:
        """Return the whole body as bytes in memory.
        """
        if self._body is None:
            raise ValueError("Body is not available. Call async method load_body, or do your call with stream=False.")
        return self._body

    async def load_body(self) -> None:
        """Load in memory the body, so it could be accessible from sync methods."""
        self._body = await self.internal_response.read()

    def stream_download(self, pipeline) -> AsyncIteratorType[bytes]:
        """Generator for streaming response body data.

        :param pipeline: The pipeline object
        :type pipeline: azure.core.pipeline
        """
        return AioHttpStreamDownloadGenerator(pipeline, self.request, self.internal_response, self.block_size)
