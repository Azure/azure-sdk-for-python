# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from io import IOBase, UnsupportedOperation
from typing import Optional
from azure.core.pipeline.transport import AsyncHttpTransport, AioHttpTransportResponse
from azure.core.rest import AsyncHttpResponse, HttpRequest
from aiohttp import ClientResponse

class ProgressTracker:
    def __init__(self, total: int, step: int):
        self.total = total
        self.step = step
        self.current = 0

    async def assert_progress(self, current: int, total: Optional[int]):
        if self.current != self.total:
            self.current += self.step

        if total:
            assert self.total == total
        assert self.current == current

    def assert_complete(self):
        assert self.total == self.current


class NonSeekableStream(IOBase):
    def __init__(self, wrapped_stream):
        self.wrapped_stream = wrapped_stream

    def write(self, data):
        return self.wrapped_stream.write(data)

    def read(self, count):
        return self.wrapped_stream.read(count)

    def seek(self, *args, **kwargs):
        raise UnsupportedOperation("boom!")

    def tell(self):
        return self.wrapped_stream.tell()


class AsyncStream:
    def __init__(self, data: bytes):
        self._data = data
        self._offset = 0

    def __len__(self) -> int:
        return len(self._data)

    async def read(self, size: int = -1) -> bytes:
        if size == -1:
            return self._data

        start = self._offset
        end = self._offset + size
        data = self._data[start:end]
        self._offset += len(data)

        return data

class MockAioHttpClientResponse(ClientResponse):
    def __init__(self, url, body_bytes, headers=None):
        self._body = body_bytes
        self._headers = headers
        self._cache = {}
        self.status = 200
        self.reason = "OK"
        self._url = url
        # self._content = b"test content"
        # self.content = b"test content"

class MockStorageTransport(AsyncHttpTransport):
    async def send(self, request: HttpRequest, **kwargs) -> AioHttpTransportResponse:
        aiohttp_transport_resp = AioHttpTransportResponse(
            request,
            MockAioHttpClientResponse(
                request.url,
                b"test content",
                {
                    "Content-Type": "application/octet-stream",
                    "Content-Range": "bytes 0-27/28",
                    "Content-Length": "28",
                },
            ),
        )

        # Everything is working as expected, but AttributeError: 'AioHttpTransportResponse' object has no attribute 'content'
        # I believe this is because typically in the real REST transport, we would switch to a RestAioHttpTransportResponse in the send()
        # logic, will which give the 'content' @property, which calls into the intermediary layer to do whatever works needs to be done
        # to retrieve the response from the underlying internal response.

        # aiohttp_transport_resp.content = aiohttp_transport_resp.internal_response._body
        return aiohttp_transport_resp

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def open(self):
        pass

    async def close(self):
        pass