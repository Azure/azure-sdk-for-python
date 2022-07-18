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
from io import BytesIO

from pyodide import JsException  # pylint: disable=import-error
from pyodide.http import pyfetch  # pylint: disable=import-error

from azure.core.utils import CaseInsensitiveDict
from azure.core.exceptions import HttpResponseError
from azure.core.rest._http_response_impl_async import AsyncHttpResponseImpl

from ._requests_asyncio import AsyncioRequestsTransport
from . import HttpRequest

class PyodideTransportResponse(AsyncHttpResponseImpl):
    """Async response object for the `PyodideTransport`."""

    def __init__(self, **kwargs):
        super(PyodideTransportResponse, self).__init__(**kwargs)
        # clone to avoid reading from the same `FetchResponse` a second time in `load_body`.
        self.reader = self.internal_response.clone().js_response.body.getReader()

    async def close(self) -> None:
        """We don't actually have control over closing connections in the browser, so we just pretend
        to close.
        """
        self._is_closed = True

    async def load_body(self) -> None:
        """Load the body of the response."""
        if self._content is None:
            self._content = await self._internal_response.bytes()


class PyodideStreamDownloadGenerator(AsyncIterator[bytes]):
    """Simple stream download generator that returns the contents of
    a request.
    """

    def __init__(self, response: PyodideTransportResponse, *_, **__):
        self.block_size = response.block_size
        self.response = response
        # use this to efficiently store bytes.
        self.stream = BytesIO()
        self.closed = False
        # We cannot control how many bytes we get from `response.reader`. `self.buffer_left`
        # indicates how many unread bytes there are in `self.stream`
        self.buffer_left = 0
        self.done = False

    async def __anext__(self) -> bytes:
        """Get the next block of bytes."""
        if self.closed:
            raise StopAsyncIteration()

        # remember the initial stream position
        start_pos = self.stream.tell()
        # move stream position to the end
        self.stream.read()
        # read from reader until there is no more data or we have `self.block_size` unread bytes.
        while self.buffer_left < self.block_size:
            read = await self.response.reader.read()
            if read.done:
                self.closed = True
                break
            self.buffer_left += self.stream.write(bytes(read.value))

        # move the stream position back to where we started
        self.stream.seek(start_pos)
        self.buffer_left -= self.block_size
        return self.stream.read(self.block_size)

class PyodideTransport(AsyncioRequestsTransport):
    """Implements a basic HTTP sender using the Pyodide Javascript Fetch API.

    WARNING: Pyodide is still an alpha technology. As such, this transport
    is highly experimental and subject to breaking changes. This transport was
    built around Pyodide version 0.20.0.
    """

    async def send(self, request: HttpRequest, **kwargs) -> PyodideTransportResponse:
        """Send request object according to configuration.

        :param request: The request object to be sent.
        :type request: ~azure.core.pipeline.transport.HttpRequest
        :return: An HTTPResponse object.
        :rtype: PyodideResponseTransport
        """
        stream_response = kwargs.pop("stream_response", False)
        endpoint = request.url
        request_headers = dict(request.headers)
        init = {
            "method": request.method,
            "headers": request_headers,
            "body": request.data,
            "files": request.files,
            "verify": kwargs.pop("connection_verify", self.connection_config.verify),
            "cert": kwargs.pop("connection_cert", self.connection_config.cert),
            "allow_redirects": False,
            **kwargs,
        }

        try:
            response = await pyfetch(endpoint, **init)
        except JsException as error:
            raise HttpResponseError(error, error=error)

        headers = CaseInsensitiveDict(response.js_response.headers)
        transport_response = PyodideTransportResponse(
            request=request,
            internal_response=response,
            block_size=self.connection_config.data_block_size,
            status_code=response.status,
            reason=response.status_text,
            content_type=headers.get("content-type"),
            headers=headers,
            stream_download_generator=PyodideStreamDownloadGenerator,
        )
        if not stream_response:
            await transport_response.load_body()

        return transport_response

