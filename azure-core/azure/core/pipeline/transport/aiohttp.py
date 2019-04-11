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
from typing import Any, Callable, AsyncIterator, Optional

import aiohttp

from .base import HttpRequest
from .base_async import AsyncHttpTransport, AsyncHttpResponse

# Matching requests, because why not?
CONTENT_CHUNK_SIZE = 10 * 1024


class AioHttpContext(object):
    def __init__(self, session, transport, **kwargs):
        self.session = session
        self.transport = transport
        self.options = kwargs


class AioHttpTransport(AsyncHttpTransport):
    """AioHttp HTTP sender implementation.
    """

    def __init__(self, configuration=None, *, loop=None):
        self.session = aiohttp.ClientSession(loop=loop)
        self.config = configuration
        self._init_session(self.session)

    async def __aenter__(self):
        await self.session.__aenter__()
        return self

    async def __aexit__(self, *exc_details):  # pylint: disable=arguments-differ
        await self.session.__aexit__(*exc_details)

    def _init_session(self, session):
        pass  # configure sesison

    def build_context(self, **kwargs):
        # type: () -> AioHttpContext
        return AioHttpContext(session=self.session, transport=self, **kwargs)

    async def send(self, request: HttpRequest, **config: Any) -> AsyncHttpResponse:
        """Send the request using this HTTP sender.

        Will pre-load the body into memory to be available with a sync method.
        pass stream=True to avoid this behavior.
        """
        # TODO SSL config
        # ssl_ctx = None
        # if self.config.connection.verify not in (True, False):
        #    import ssl
         #   ssl_ctx = ssl.create_default_context(cafile=self.config.connection.verify)

        stream_response = config.pop("stream", False)
        result = await self.session.request(
            request.method,
            request.url,
            headers=request.headers,
            data=request.data,
            # files=request.files,  # TODO: What is aiohttp equivalent...?
            # verify=config.get('connection_verify', self.config.connection.verify),
            timeout=config.get('connection_timeout', self.config.connection.timeout),
            # cert=config.get('connection_cert', self.config.connection.cert),
            allow_redirects=False,
            **config
        )
        response = AioHttpTransportResponse(request, result, self.config.connection.data_block_size)
        if not stream_response:
            await response.load_body()
        return response


class AioHttpTransportResponse(AsyncHttpResponse):

    def __init__(self, request: HttpRequest, aiohttp_response: aiohttp.ClientResponse, blob_size: int) -> None:
        super(AioHttpTransportResponse, self).__init__(request, aiohttp_response, blob_size)
        # https://aiohttp.readthedocs.io/en/stable/client_reference.html#aiohttp.ClientResponse
        self.status_code = aiohttp_response.status
        self.headers = aiohttp_response.headers
        self.reason = aiohttp_response.reason
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

    def stream_download(self, chunk_size: Optional[int] = None, callback: Optional[Callable] = None) -> AsyncIterator[bytes]:
        """Generator for streaming request body data.
        """
        chunk_size = chunk_size or CONTENT_CHUNK_SIZE
        async def async_gen(resp):
            while True:
                chunk = await resp.content.read(chunk_size)
                if not chunk:
                    break
                callback(chunk, resp)
        return async_gen(self.internal_response)