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
import httpx
from typing import ContextManager, Optional
from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.core.pipeline.transport import AsyncHttpResponse, HttpRequest, AsyncHttpTransport


class AsyncHttpXTransportResponse(AsyncHttpResponse):
    def __init__(self, request: HttpRequest, httpx_response: httpx.Response, stream_contextmanager: Optional[ContextManager]) -> None:
        super().__init__(request, httpx_response)
        self.status_code = httpx_response.status_code
        self.headers = httpx_response.headers
        self.reason = httpx_response.reason_phrase
        self._content = None
        self.content_type = httpx_response.headers.get('content-type')
        self.stream_contextmanager = stream_contextmanager
    
    def body(self) -> bytes:
        return self.internal_response.content

    def stream_download(self, _) -> AsyncIterator[bytes]:
        return AsyncHttpXStreamDownloadGenerator(_, self)

    async def load_body(self) -> None:
        self._content = self.internal_response.content


class AsyncHttpXStreamDownloadGenerator(AsyncIterator):
    def __init__(self, _, response) -> None:
        self.response = response
        self.iter_bytes_func = self.response.internal_response.aiter_bytes()

    async def __len__(self) -> int:
        return self.response.internal_response.headers['content-length']

    def __aiter__(self) -> 'AsyncHttpXStreamDownloadGenerator':
        return self

    async def __anext__(self):
        try:
            return anext(self.iter_bytes_func)
        except StopAsyncIteration:
            self.response.internal_response.close()
            raise

class AsyncHttpXTransport(AsyncHttpTransport):
    """Implements a basic async httpx HTTP sender

    :keyword httpx.AsyncClient client: HTTPX client to use instead of the default one
    """
    def __init__(self, **kwargs) -> None:
        self.client: Optional[httpx.AsyncClient] = kwargs.get("client", None)

    async def open(self) -> None:
        self.client = httpx.AsyncClient()

    async def close(self) -> None:
        if self.client:
            await self.client.aclose()
            self.client = None
    
    async def __aenter__(self) -> "AsyncHttpXTransport":
        await self.open()
        return self
    
    async def __aexit__(self, *args) -> None:
        await self.close()

    async def send(self, request: HttpRequest, **kwargs) -> AsyncHttpXTransportResponse:
        stream_response = kwargs.pop("stream", False)
        parameters = {
            "method": request.method,
            "url": request.url,
            "headers": request.headers.items(),
            "data": request.data,
            "content": request.content,
            "files": request.files,
            **kwargs,
        }

        stream_ctx: Optional[ContextManager] = None

        try:
            if stream_response:
                req = self.client.build_request(**parameters)
                response = await self.client.send(req, stream=stream_response)
            else:
                response = await self.client.request(**parameters)
        except (
            httpx.ReadTimeout,
            httpx.ProtocolError,
            ) as err:
            raise ServiceResponseError(err, error=err)
        except httpx.RequestError as err:
            raise ServiceRequestError(err, error=err)

        return AsyncHttpXTransportResponse(request, response, stream_contextmanager=stream_ctx)