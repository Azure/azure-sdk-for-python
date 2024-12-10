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

# This is the base response that worked fine with my download_blob example.
# You may or may not need to make more of these containing different information,
# it just depends on what is expected in the response per request type.
class MockAioHttpClientResponse(ClientResponse):
    def __init__(self, url, body_bytes, headers=None):
        self._body = body_bytes
        self._headers = headers
        self._cache = {}
        self.status = 200
        self.reason = "OK"
        self._url = url

# Here we are mocking out the real Storage transport.
# Instead of it taking our HttpRequest and making a real network roundtrip and returning the response,
# instead we will mock in the responses.
class MockStorageTransport(AsyncHttpTransport):
    async def send(self, request: HttpRequest, **kwargs) -> AioHttpTransportResponse:

        # So this is what the response needs to look like for the test-case I've written
        # (download_blob in test_mocking_transport in test_common_blob_async.py)

        # TODO:
        # 1. Add in logic to conditionally return different responses based on request type
        # 2. Add test cases for each of the following:
        #     - download_blob (with and without content validation, as this hits two different key content loading areas)
        #     - get properties
        #     - upload blob (with and without content validation, as this hits two different key content loading areas)
        #     - delete blob
        # 3. Duplicate test case to sync
        # 4. Duplicate work to other packages
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
        return aiohttp_transport_resp

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def open(self):
        pass

    async def close(self):
        pass