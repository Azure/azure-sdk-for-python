# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from io import IOBase, UnsupportedOperation
from typing import Any, Dict, Optional

from azure.core.pipeline.transport import AsyncHttpTransport
from azure.core.rest import HttpRequest
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
    def __init__(
        self, url: str,
        body_bytes: bytes,
        headers: Dict[str, Any],
        status: int = 200,
        reason: str = "OK"
    ) -> None:
        super(MockAioHttpClientResponse).__init__()
        self._url = url
        self._body = body_bytes
        self._headers = headers
        self._cache = {}
        self._loop = None
        self.status = status
        self.reason = reason


class MockStorageTransport(AsyncHttpTransport):
    """
    This transport returns legacy http response objects from azure core and is 
    intended only to test our backwards compatibility support.
    """
    async def send(self, request: HttpRequest, **kwargs: Any) -> RestAioHttpTransportResponse:
        if request.method == 'GET':
            # download_blob
            headers = {
                "Content-Type": "application/octet-stream",
                "Content-Range": "bytes 0-17/18",
                "Content-Length": "18",
            }

            if "x-ms-range-get-content-md5" in request.headers:
                headers["Content-MD5"] = "I3pVbaOCUTom+G9F9uKFoA=="

            rest_response = RestAioHttpTransportResponse(
                request=request,
                internal_response=MockAioHttpClientResponse(
                    request.url,
                    b"Hello Async World!",
                    headers,
                ),
                decompress=False
            )
        elif request.method == 'HEAD':
            # get_blob_properties
            rest_response = RestAioHttpTransportResponse(
                request=request,
                internal_response=MockAioHttpClientResponse(
                    request.url,
                    b"",
                    {
                        "Content-Type": "application/octet-stream",
                        "Content-Length": "1024",
                    },
                ),
                decompress=False
            )
        elif request.method == 'PUT':
            # upload_blob
            rest_response = RestAioHttpTransportResponse(
                request=request,
                internal_response=MockAioHttpClientResponse(
                    request.url,
                    b"",
                    {
                        "Content-Length": "0",
                    },
                    201,
                    "Created"
                ),
                decompress=False
            )
        elif request.method == 'DELETE':
            # delete_blob
            rest_response = RestAioHttpTransportResponse(
                request=request,
                internal_response=MockAioHttpClientResponse(
                    request.url,
                    b"",
                    {
                        "Content-Length": "0",
                    },
                    202,
                    "Accepted"
                ),
                decompress=False
            )
        else:
            raise ValueError("The request is not accepted as part of MockStorageTransport.")

        await rest_response.read()
        return rest_response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def open(self):
        pass

    async def close(self):
        pass
