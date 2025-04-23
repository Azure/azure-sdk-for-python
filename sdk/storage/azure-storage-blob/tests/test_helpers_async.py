# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import aiohttp
from datetime import datetime, timezone
from io import IOBase, UnsupportedOperation
from typing import Any, Dict, Optional, Tuple

from azure.core.pipeline.transport import AioHttpTransportResponse, AsyncHttpTransport
from azure.core.rest import HttpRequest
from azure.storage.blob._serialize import get_api_version
from aiohttp import ClientResponse


def _build_base_file_share_headers(bearer_token_string: str, content_length: int = 0) -> Dict[str, Any]:
    return {
        'Authorization': bearer_token_string,
        'Content-Length': str(content_length),
        'x-ms-date': datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'),
        'x-ms-version': get_api_version({}),
        'x-ms-file-request-intent': 'backup',
    }


async def _create_file_share_oauth(
    share_name: str,
    file_name: str,
    bearer_token_string: str,
    storage_account_name: str,
    data: bytes
) -> Tuple[str, str]:
    base_url = f"https://{storage_account_name}.file.core.windows.net/{share_name}"

    async with aiohttp.ClientSession() as session:
        # Creates file share
        await session.put(
            url=base_url,
            headers=_build_base_file_share_headers(bearer_token_string),
            params={'restype': 'share'}
        )

        # Creates the file itself
        headers = _build_base_file_share_headers(bearer_token_string)
        headers.update({'x-ms-content-length': '1024', 'x-ms-type': 'file'})
        await session.put(url=base_url + "/" + file_name, headers=headers)

        # Upload the supplied data to the file
        headers = _build_base_file_share_headers(bearer_token_string, 1024)
        headers.update({'x-ms-range': 'bytes=0-1023', 'x-ms-write': 'update'})
        await session.put(url=base_url + "/" + file_name, headers=headers, data=data, params={'comp': 'range'})

    return file_name, base_url


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
    async def send(self, request: HttpRequest, **kwargs: Any) -> AioHttpTransportResponse:
        if request.method == 'GET':
            # download_blob
            headers = {
                "Content-Type": "application/octet-stream",
                "Content-Range": "bytes 0-17/18",
                "Content-Length": "18",
            }

            if "x-ms-range-get-content-md5" in request.headers:
                headers["Content-MD5"] = "I3pVbaOCUTom+G9F9uKFoA=="

            rest_response = AioHttpTransportResponse(
                request=request,
                aiohttp_response=MockAioHttpClientResponse(
                    request.url,
                    b"Hello Async World!",
                    headers,
                ),
                decompress=False
            )
        elif request.method == 'HEAD':
            # get_blob_properties
            rest_response = AioHttpTransportResponse(
                request=request,
                aiohttp_response=MockAioHttpClientResponse(
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
            rest_response = AioHttpTransportResponse(
                request=request,
                aiohttp_response=MockAioHttpClientResponse(
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
            rest_response = AioHttpTransportResponse(
                request=request,
                aiohttp_response=MockAioHttpClientResponse(
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

        await rest_response.load_body()
        return rest_response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def open(self):
        pass

    async def close(self):
        pass
