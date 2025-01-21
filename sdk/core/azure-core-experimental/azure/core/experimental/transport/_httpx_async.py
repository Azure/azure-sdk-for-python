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
from typing import Any, AsyncIterator, ContextManager, Optional, Union

import httpx
from azure.core.configuration import ConnectionConfiguration
from azure.core.exceptions import DecodeError, ServiceRequestError, ServiceResponseError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import AsyncHttpTransport
from azure.core.pipeline.transport import HttpRequest as LegacyHttpRequest
from azure.core.rest import HttpRequest
from azure.core.rest._http_response_impl_async import AsyncHttpResponseImpl


class AsyncHttpXTransportResponse(AsyncHttpResponseImpl):
    """Async HttpX response implementation.

    :param request: The request sent to the server
    :type request: ~azure.core.rest.HTTPRequest or LegacyHTTPRequest
    :param httpx.Response httpx_response: The response object returned from HttpX library
    :param ContextManager stream_contextmanager: The context manager to stream response data.
    """

    def __init__(
        self,
        request: Union[HttpRequest, LegacyHttpRequest],
        httpx_response: httpx.Response,
        stream_contextmanager: Optional[ContextManager],
    ) -> None:
        super().__init__(
            request=request,
            internal_response=httpx_response,
            status_code=httpx_response.status_code,
            headers=httpx_response.headers,
            reason=httpx_response.reason_phrase,
            content_type=httpx_response.headers.get("content-type"),
            stream_download_generator=stream_contextmanager,
        )

    def body(self) -> bytes:
        """Return the whole body as bytes.

        :return: The whole body as bytes.
        :rtype: bytes
        """
        return self.internal_response.content

    def stream_download(self, pipeline: Pipeline, *, decompress: bool = True, **kwargs: Any) -> AsyncIterator[bytes]:
        """Generator for streaming response data.

        :param pipeline: The pipeline object
        :type pipeline: ~azure.core.pipeline.Pipeline
        :keyword bool decompress: If True which is default, will attempt to decode the body based
            on the *content-encoding* header.
        :return: An iterator for streaming response data.
        :rtype: AsyncIterator[bytes]
        """
        return AsyncHttpXStreamDownloadGenerator(pipeline, self, decompress=decompress, **kwargs)

    async def load_body(self) -> None:
        self._content = await self.internal_response.read()


# pylint: disable=unused-argument
class AsyncHttpXStreamDownloadGenerator(AsyncIterator):
    """Generator for streaming response data.

    :param pipeline: The pipeline object
    :type pipeline: ~azure.core.pipeline.Pipeline
    :param response: The response object.
    :type response: AsyncHttpXTransportResponse
    :keyword bool decompress: If True which is default, will attempt to decode the body based
        on the *content-encoding* header.
    """

    def __init__(
        self, pipeline: Pipeline, response: AsyncHttpXTransportResponse, *, decompress: bool = True, **kwargs
    ) -> None:
        self.pipeline = pipeline
        self.response = response
        should_decompress = decompress

        if should_decompress:
            self.iter_content_func = self.response.internal_response.aiter_bytes()
        else:
            self.iter_content_func = self.response.internal_response.aiter_raw()

    async def __len__(self) -> int:
        return self.response.internal_response.headers["content-length"]

    def __aiter__(self) -> "AsyncHttpXStreamDownloadGenerator":
        return self

    async def __anext__(self):
        try:
            return await self.iter_content_func.__anext__()
        except StopAsyncIteration:
            self.response.internal_response.close()
            raise
        except httpx.DecodingError as ex:
            if len(ex.args) > 1:
                raise DecodeError(ex.args[0]) from ex
            raise DecodeError("Failed to decode.") from ex


class AsyncHttpXTransport(AsyncHttpTransport):
    """Implements a basic async httpx HTTP sender

    :keyword httpx.AsyncClient client: HTTPX client to use instead of the default one
    :keyword bool client_owner: Decide if the client provided by user is owned by this transport. Default to True.
    :keyword bool use_env_settings: Uses proxy settings from environment. Defaults to True.
    """

    def __init__(
        self,
        *,
        client: Optional[httpx.AsyncClient] = None,
        client_owner: bool = True,
        use_env_settings: bool = True,
        **kwargs: Any
    ) -> None:
        self.client = client
        self.connection_config = ConnectionConfiguration(**kwargs)
        self._client_owner = client_owner
        self._use_env_settings = use_env_settings

    async def open(self) -> None:
        if self.client is None:
            self.client = httpx.AsyncClient(
                trust_env=self._use_env_settings,
                verify=self.connection_config.verify,
                cert=self.connection_config.cert,
            )

    async def close(self) -> None:
        if self._client_owner and self.client:
            await self.client.aclose()
            self.client = None

    async def __aenter__(self) -> "AsyncHttpXTransport":
        await self.open()
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

    async def send(
        self, request: Union[HttpRequest, LegacyHttpRequest], *, stream: bool = False, **kwargs
    ) -> AsyncHttpXTransportResponse:
        """Send the request using this HTTP sender.

        :param request: The request object to be sent.
        :type request: ~azure.core.rest.HttpRequest or LegacyHttpRequest
        :keyword bool stream: Whether to stream the response. Defaults to False.
        :return: The response object.
        :rtype: ~azure.core.experimental.transport.AsyncHttpXTransportResponse
        """
        await self.open()
        stream_response = stream
        parameters = {
            "method": request.method,
            "url": request.url,
            "headers": request.headers.items(),
            "data": request.data,
            "content": request.content if hasattr(request, "content") else None,
            "files": request.files,
            **kwargs,
        }

        stream_ctx: Optional[ContextManager] = None
        response: httpx.Response
        try:
            if stream_response and self.client:
                req = self.client.build_request(**parameters)
                response = await self.client.send(req, stream=stream_response)
            elif self.client:
                response = await self.client.request(**parameters)
        except (
            httpx.ReadTimeout,
            httpx.ProtocolError,
        ) as err:
            raise ServiceResponseError(err, error=err) from err
        except httpx.RequestError as err:
            raise ServiceRequestError(err, error=err) from err

        return AsyncHttpXTransportResponse(request, response, stream_contextmanager=stream_ctx)
