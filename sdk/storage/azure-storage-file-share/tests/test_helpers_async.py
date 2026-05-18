# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, AsyncIterator, Dict, Optional

from azure.core.pipeline.transport import AsyncHttpTransport
from azure.core.rest import HttpRequest
from azure.core.rest._http_response_impl_async import AsyncHttpResponseImpl


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


def _mock_async_stream_generator(data: bytes):
    """Simple async generator that yields data in a single chunk."""

    async def generator(response, **kwargs) -> AsyncIterator[bytes]:
        yield data

    return generator


class _MockInternalResponse:
    """Minimal internal response object for AsyncHttpResponseImpl."""

    async def close(self):
        pass


def _make_async_rest_response(
    request: HttpRequest,
    body: bytes,
    headers: Dict[str, Any],
    status_code: int = 200,
    reason: str = "OK",
) -> AsyncHttpResponseImpl:
    """Create an azure.core.rest async HttpResponse with iter_bytes/iter_raw support."""
    content_type = headers.get("Content-Type", "application/octet-stream")
    resp = AsyncHttpResponseImpl(
        request=request,
        internal_response=_MockInternalResponse(),
        status_code=status_code,
        reason=reason,
        content_type=content_type,
        headers=headers,
        stream_download_generator=_mock_async_stream_generator(body),
    )
    resp._content = body  # pylint: disable=protected-access
    return resp


class MockStorageTransport(AsyncHttpTransport):
    """
    This transport returns azure.core.rest async HttpResponse objects for
    compatibility with TypeSpec-generated code that uses iter_bytes/iter_raw.
    """

    async def send(self, request: HttpRequest, **kwargs: Any) -> AsyncHttpResponseImpl:
        if request.method == "GET":
            # download_file
            headers = {
                "Content-Type": "application/octet-stream",
                "Content-Range": "bytes 0-17/18",
                "Content-Length": "18",
            }

            if "x-ms-range-get-content-md5" in request.headers:
                headers["Content-MD5"] = "I3pVbaOCUTom+G9F9uKFoA=="

            rest_response = _make_async_rest_response(request, b"Hello Async World!", headers)
        elif request.method == "HEAD":
            # get_file_properties
            rest_response = _make_async_rest_response(
                request,
                b"",
                {
                    "Content-Type": "application/octet-stream",
                    "Content-Length": "1024",
                },
            )
        elif request.method == "PUT":
            # upload_file
            rest_response = _make_async_rest_response(
                request,
                b"",
                {"Content-Length": "0"},
                201,
                "Created",
            )
        elif request.method == "DELETE":
            # delete_file
            rest_response = _make_async_rest_response(
                request,
                b"",
                {"Content-Length": "0"},
                202,
                "Accepted",
            )
        else:
            raise ValueError("The request is not accepted as part of MockStorageTransport.")
        return rest_response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    async def open(self):
        pass

    async def close(self):
        pass
