# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from io import IOBase, UnsupportedOperation
from typing import Any, Dict, Optional

from azure.core.pipeline.transport import HttpTransport
from azure.core.rest import HttpRequest
from azure.core.rest._http_response_impl import HttpResponseImpl, RestHttpClientTransportResponse

class ProgressTracker:
    def __init__(self, total: int, step: int):
        self.total = total
        self.step = step
        self.current = 0

    def assert_progress(self, current: int, total: Optional[int]):
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


class MockHttpClientResponse(HttpResponseImpl):
    def __init__(
        self, url: str,
        body_bytes: bytes,
        headers: Dict[str, Any],
        status: int = 200,
        reason: str = "OK"
    ) -> None:
        super(MockHttpClientResponse).__init__()
        self._url = url
        self._body = body_bytes
        self._headers = headers
        self._cache = {}
        self._loop = None
        self.status = status
        self.reason = reason


class MockStorageTransport(HttpTransport):
    def send(self, request: HttpRequest, **kwargs: Any) -> RestHttpClientTransportResponse:
        if request.method == 'GET':
            # download_blob
            rest_response = RestHttpClientTransportResponse(
                request=request,
                internal_response=MockHttpClientResponse(
                    request.url,
                    b"Hello Async World!",
                    {
                        "Content-Type": "application/octet-stream",
                        "Content-Range": "bytes 0-17/18",
                        "Content-Length": "18",
                    },
                )
            )
        else:
            raise ValueError("The request is not accepted as part of MockStorageTransport.")
        return rest_response.read()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def open(self):
        pass

    def close(self):
        pass
