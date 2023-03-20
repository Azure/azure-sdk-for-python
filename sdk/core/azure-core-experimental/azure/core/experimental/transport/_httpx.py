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
import httpx
from typing import ContextManager, Iterator, Optional
from azure.core.pipeline.transport import HttpResponse, HttpRequest, HttpTransport
from azure.core.exceptions import ServiceRequestError, ServiceResponseError


class HttpXTransportResponse(HttpResponse):
    def __init__(
        self, request: HttpRequest, httpx_response: httpx.Response, stream_contextmanager: Optional[ContextManager]
    ) -> None:
        super().__init__(request, httpx_response)
        self.status_code = httpx_response.status_code
        self.headers = httpx_response.headers
        self.reason = httpx_response.reason_phrase
        self.content_type = httpx_response.headers.get("content-type")
        self.stream_contextmanager = stream_contextmanager

    def body(self) -> bytes:
        return self.internal_response.content

    def stream_download(self, _) -> Iterator[bytes]:
        return HttpXStreamDownloadGenerator(_, self)


class HttpXStreamDownloadGenerator:
    def __init__(self, _, response) -> None:
        self.response = response
        self.iter_bytes_func = self.response.internal_response.iter_bytes()

    def __iter__(self) -> "HttpXStreamDownloadGenerator":
        return self

    def __next__(self):
        try:
            return next(self.iter_bytes_func)
        except StopIteration as se:
            self.response.stream_contextmanager.__exit__(None, None, None)
            raise


class HttpXTransport(HttpTransport):
    def __init__(self) -> None:
        self.client: Optional[httpx.Client] = None

    def open(self) -> None:
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
            "files": request.files,
            **kwargs,
        }

        stream_ctx: Optional[ContextManager] = None

        try:
            if stream_response:
                response = stream_ctx.__enter__()
                stream_ctx = self.client.stream(**parameters)
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
    