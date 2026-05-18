# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Dict, Iterator, Optional
from typing_extensions import Self

from azure.core.pipeline.transport import HttpTransport
from azure.core.rest import HttpRequest
from azure.core.rest._http_response_impl import HttpResponseImpl


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


def _mock_stream_generator(data: bytes):
    """Simple generator that yields data in a single chunk."""

    def generator(response, **kwargs):
        yield data

    return generator


class _MockInternalResponse:
    """Minimal internal response object for HttpResponseImpl."""

    def close(self):
        pass


def _make_rest_response(
    request: HttpRequest,
    body: bytes,
    headers: Dict[str, Any],
    status_code: int = 200,
    reason: str = "OK",
) -> HttpResponseImpl:
    """Create an azure.core.rest HttpResponse with iter_bytes/iter_raw support."""
    content_type = headers.get("Content-Type", "application/octet-stream")
    resp = HttpResponseImpl(
        request=request,
        internal_response=_MockInternalResponse(),
        status_code=status_code,
        reason=reason,
        content_type=content_type,
        headers=headers,
        stream_download_generator=_mock_stream_generator(body),
    )
    resp._content = body  # pylint: disable=protected-access
    return resp


class MockStorageTransport(HttpTransport):
    """
    This transport returns azure.core.rest HttpResponse objects for
    compatibility with TypeSpec-generated code that uses iter_bytes/iter_raw.
    """

    def send(self, request: HttpRequest, **kwargs: Any) -> HttpResponseImpl:
        if request.method == "GET":
            # download_file
            headers = {
                "Content-Type": "application/octet-stream",
                "Content-Range": "bytes 0-17/18",
                "Content-Length": "18",
            }

            if "x-ms-range-get-content-md5" in request.headers:
                headers["Content-MD5"] = "7Qdih1MuhjZehB6Sv8UNjA=="  # cspell:disable-line

            rest_response = _make_rest_response(request, b"Hello World!", headers)
        elif request.method == "HEAD":
            # get_file_properties
            rest_response = _make_rest_response(
                request,
                b"",
                {
                    "Content-Type": "application/octet-stream",
                    "Content-Length": "1024",
                },
            )
        elif request.method == "PUT":
            # upload_file
            rest_response = _make_rest_response(
                request,
                b"",
                {"Content-Length": "0"},
                201,
                "Created",
            )
        elif request.method == "DELETE":
            # delete_file
            rest_response = _make_rest_response(
                request,
                b"",
                {"Content-Length": "0"},
                202,
                "Accepted",
            )
        else:
            raise ValueError("The request is not accepted as part of MockStorageTransport.")
        return rest_response

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: Any) -> None:
        pass

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass
