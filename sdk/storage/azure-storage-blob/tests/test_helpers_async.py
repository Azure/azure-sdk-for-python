# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from io import IOBase, UnsupportedOperation
from typing import Any, Dict, Optional

from azure.core.pipeline.transport import AsyncHttpTransport, AioHttpTransportResponse
from azure.core.rest import AsyncHttpResponse, HttpRequest
from azure.core.rest._aiohttp import RestAioHttpTransportResponse
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
    def __init__(self, url: str, body_bytes: bytes, headers: Optional[Dict[str, Any]] = None):
        self._url = url
        self._body = body_bytes
        self._headers = headers
        self._cache = {}
        self._loop = None
        self.status = 200
        self.reason = "OK"

class MockStorageTransport(AsyncHttpTransport):
    async def send(self, request: HttpRequest, **kwargs: Any) -> AioHttpTransportResponse:
        if request.method == 'GET':
            # download blob
            return AioHttpTransportResponse(
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
        elif request.method == 'HEAD':
            # get blob properties
            core_response = RestAioHttpTransportResponse(
                request=request,
                internal_response=MockAioHttpClientResponse(
                    request.url,
                    b"",
                    {
                        "Content-Type": "application/octet-stream",
                        "Content-Length": "1024",
                        "Content-MD5": "yaNM/IXZgmmMasifdgcavQ=="
                    },
                ),
                decompress=False
            )
            # resp = AioHttpTransportResponse(
            #     request,
            #     MockAioHttpClientResponse(
            #         request.url,
            #         b"",
            #         {
            #             "Content-Type": "application/octet-stream",
            #             "Content-Length": "1024",
            #             "Content-MD5": "yaNM/IXZgmmMasifdgcavQ=="
            #         },
            #     ),
            # )
            # await resp.read()

            # Emulate the logic that would call into read()
            await core_response.read()
            return core_response

        return None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def open(self):
        pass

    async def close(self):
        pass