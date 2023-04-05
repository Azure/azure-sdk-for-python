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
from typing import ContextManager, Iterator, Optional

import httpx
from azure.core.pipeline import Pipeline

from azure.core.exceptions import ServiceRequestError, ServiceResponseError
from azure.core.pipeline.transport import HttpTransport
from azure.core.rest import HttpRequest
from azure.core.rest._http_response_impl import HttpResponseImpl


class HttpXTransportResponse(HttpResponseImpl):
    def __init__(
        self, request: HttpRequest, httpx_response: httpx.Response, stream_contextmanager: Optional[ContextManager]
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
        return self.internal_response.content

    def stream_download(self, pipeline: Pipeline, **kwargs) -> Iterator[bytes]:
        return HttpXStreamDownloadGenerator(pipeline, self, **kwargs)


# pylint: disable=unused-argument
class HttpXStreamDownloadGenerator:
    """Generator for streaming response data.

    :param pipeline: The pipeline object
    :param response: The response object.
    :keyword bool decompress: If True which is default, will attempt to decode the body based
        on the *content-encoding* header.
    """

    def __init__(self, pipeline: Pipeline, response: HttpXTransportResponse, **kwargs) -> None:
        self.pipeline = pipeline
        self.response = response
        decompress = kwargs.pop("decompress", True)

        if decompress:
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


class HttpXTransport(HttpTransport):
    """Implements a basic httpx HTTP sender

    :keyword httpx.Client client: HTTPX client to use instead of the default one
    """

    def __init__(self, **kwargs) -> None:
        self.client = kwargs.get("client", None)

    def open(self) -> None:
        if self.client is None:
            self.client = httpx.Client()

    def close(self) -> None:
        if self.client:
            self.client.close()
            self.client = None

    def __enter__(self) -> "HttpXTransport":
        self.open()
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def send(self, request: HttpRequest, **kwargs) -> HttpXTransportResponse:
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
                stream_ctx = self.client.stream(**parameters)
                if stream_ctx:
                    response = stream_ctx.__enter__()
            else:
                response = self.client.request(**parameters)
        except (
            httpx.ReadTimeout,
            httpx.ProtocolError,
        ) as err:
            raise ServiceResponseError(err, error=err)
        except httpx.RequestError as err:
            raise ServiceRequestError(err, error=err)

        return HttpXTransportResponse(request, response, stream_contextmanager=stream_ctx)
