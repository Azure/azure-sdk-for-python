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
from typing import Any, ContextManager, Iterator, Optional, Union

import httpx
from azure.core.configuration import ConnectionConfiguration
from azure.core.exceptions import DecodeError, ServiceRequestError, ServiceResponseError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import HttpTransport
from azure.core.rest import HttpRequest
from azure.core.rest._http_response_impl import HttpResponseImpl
from azure.core.pipeline.transport import HttpRequest as LegacyHttpRequest


class HttpXTransportResponse(HttpResponseImpl):
    """HttpX response implementation.

    :param request: The request sent to the server
    :type request: ~azure.core.rest.HTTPRequest or LegacyHTTPRequest
    :param httpx.Response httpx_response: The response object returned from the HttpX library
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

    def read(self) -> bytes:
        """Read the response's bytes.

        :return: The response's bytes.
        :rtype: bytes
        """
        if self._content is None:
            self._content = self.internal_response.read()
        return self.content

    def body(self) -> bytes:
        """Get the body of the response.

        :return: The response's bytes.
        :rtype: bytes
        """
        return self.internal_response.content

    def stream_download(self, pipeline: Pipeline, *, decompress: bool = True, **kwargs) -> Iterator[bytes]:
        """Generator for streaming response data.

        :param pipeline: The pipeline object
        :type pipeline: ~azure.core.pipeline.Pipeline
        :keyword bool decompress: If True which is default, will attempt to decode the body based
            on the *content-encoding* header.
        :return: An iterator for streaming response data.
        :rtype: Iterator[bytes]
        """
        return HttpXStreamDownloadGenerator(pipeline, self, decompress=decompress, **kwargs)


# pylint: disable=unused-argument
class HttpXStreamDownloadGenerator:
    """Generator for streaming response data.

    :param pipeline: The pipeline object
    :type pipeline: ~azure.core.pipeline.Pipeline
    :param response: The response object.
    :type response: HttpXTransportResponse
    :keyword bool decompress: If True which is default, will attempt to decode the body based
        on the *content-encoding* header.
    """

    def __init__(
        self, pipeline: Pipeline, response: HttpXTransportResponse, *, decompress: bool = True, **kwargs
    ) -> None:
        self.pipeline = pipeline
        self.response = response
        should_decompress = decompress

        if should_decompress:
            self.iter_content_func = self.response.internal_response.iter_bytes()
        else:
            self.iter_content_func = self.response.internal_response.iter_raw()

    def __iter__(self) -> "HttpXStreamDownloadGenerator":
        return self

    def __next__(self):
        try:
            return next(self.iter_content_func)
        except StopIteration:
            self.response.stream_contextmanager.__exit__(None, None, None)
            raise
        except httpx.DecodingError as ex:
            if len(ex.args) > 0:
                raise DecodeError(ex.args[0]) from ex
            raise DecodeError("Failed to decode.") from ex


class HttpXTransport(HttpTransport):
    """Implements a basic httpx HTTP sender

    :keyword httpx.Client client: HTTPX client to use instead of the default one
    :keyword bool client_owner: Decide if the client provided by user is owned by this transport. Default to True.
    :keyword bool use_env_settings: Uses proxy settings from environment. Defaults to True.
    """

    def __init__(
        self,
        *,
        client: Optional[httpx.Client] = None,
        client_owner: bool = True,
        use_env_settings: bool = True,
        **kwargs: Any
    ) -> None:
        self.client = client
        self.connection_config = ConnectionConfiguration(**kwargs)
        self._client_owner = client_owner
        self._use_env_settings = use_env_settings

    def open(self) -> None:
        if self.client is None:
            self.client = httpx.Client(
                trust_env=self._use_env_settings,
                verify=self.connection_config.verify,
                cert=self.connection_config.cert,
            )

    def close(self) -> None:
        """Close the session.

        :return: None
        :rtype: None
        """
        if self._client_owner and self.client:
            self.client.close()
            self.client = None

    def __enter__(self) -> "HttpXTransport":
        self.open()
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def send(
        self, request: Union[HttpRequest, LegacyHttpRequest], *, stream: bool = False, **kwargs
    ) -> HttpXTransportResponse:
        """Send a request and get back a response.

        :param request: The request object to be sent.
        :type request: ~azure.core.rest.HTTPRequest or LegacyHTTPRequest
        :keyword bool stream: Whether to stream the response. Defaults to False.
        :return: An HTTPResponse object.
        :rtype: ~azure.core.experimental.transport.HttpXTransportResponse
        """
        self.open()
        stream_response = stream
        timeout = kwargs.pop("connection_timeout", self.connection_config.timeout)
        # not needed here as its already handled during init
        kwargs.pop("connection_verify", None)
        parameters = {
            "method": request.method,
            "url": request.url,
            "headers": request.headers.items(),
            "data": request.data,
            "files": request.files,
            "timeout": timeout,
            **kwargs,
        }

        if hasattr(request, "content"):
            parameters["content"] = request.content

        stream_ctx: Optional[ContextManager] = None
        try:
            if stream_response and self.client:
                stream_ctx = self.client.stream(**parameters)
                if stream_ctx:
                    response = stream_ctx.__enter__()
            elif self.client:
                response = self.client.request(**parameters)
        except (
            httpx.ReadTimeout,
            httpx.ProtocolError,
        ) as err:
            raise ServiceResponseError(err, error=err) from err
        except httpx.RequestError as err:
            raise ServiceRequestError(err, error=err) from err

        return HttpXTransportResponse(
            request, response, stream_contextmanager=stream_ctx  # pylint: disable=used-before-assignment
        )
