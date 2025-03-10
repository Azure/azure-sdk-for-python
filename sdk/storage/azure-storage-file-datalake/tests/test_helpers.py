# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Dict, Optional
from typing_extensions import Self
from urllib.parse import urlparse

from azure.core.pipeline.transport import HttpTransport, RequestsTransportResponse
from azure.core.rest import HttpRequest
from requests import Response
from urllib3 import HTTPResponse


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


class MockHttpClientResponse(Response):
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
        self._content = body_bytes
        self._cache = {}
        self._loop = None
        self._content_consumed = True
        self.headers = headers
        self.status_code = status
        self.reason = reason
        self.raw = HTTPResponse()


class MockStorageTransport(HttpTransport):
    """
    This transport returns legacy http response objects from azure core and is
    intended only to test our backwards compatibility support.
    """
    def send(self, request: HttpRequest, **kwargs: Any) -> RequestsTransportResponse:
        if request.method == 'GET':
            # download_file
            headers = {
                "Content-Type": "application/octet-stream",
                "Content-Range": "bytes 0-17/18",
                "Content-Length": "18",
            }

            if "x-ms-range-get-content-md5" in request.headers:
                headers["Content-MD5"] = "7Qdih1MuhjZehB6Sv8UNjA=="  # cspell:disable-line

            rest_response = RequestsTransportResponse(
                request=request,
                requests_response=MockHttpClientResponse(
                    request.url,
                    b"Hello World!",
                    headers,
                )
            )
        elif request.method == 'HEAD':
            # get_file_properties
            rest_response = RequestsTransportResponse(
                request=request,
                requests_response=MockHttpClientResponse(
                    request.url,
                    b"",
                    {
                        "Content-Type": "application/octet-stream",
                        "Content-Length": "1024",
                    },
                )
            )
        elif request.method == 'PUT':
            # upload_data
            rest_response = RequestsTransportResponse(
                request=request,
                requests_response=MockHttpClientResponse(
                    request.url,
                    b"",
                    {
                        "Content-Length": "0",
                    },
                    201,
                    "Created"
                )
            )
        elif request.method == 'PATCH':
            # upload_data_chunks
            parsed = urlparse(request.url)
            if "action=flush" in parsed.query:
                rest_response = RequestsTransportResponse(
                    request=request,
                    requests_response=MockHttpClientResponse(
                        request.url,
                        b"",
                        {
                            "Content-Length": "0",
                        },
                        200,
                        "OK"
                    )
                )
            else:
                rest_response = RequestsTransportResponse(
                    request=request,
                    requests_response=MockHttpClientResponse(
                        request.url,
                        b"",
                        {
                            "Content-Length": "0",
                        },
                        202,
                        "Accepted"
                    )
                )
        elif request.method == 'DELETE':
            # delete_file
            rest_response = RequestsTransportResponse(
                request=request,
                requests_response=MockHttpClientResponse(
                    request.url,
                    b"",
                    {
                        "Content-Length": "0",
                    },
                    202,
                    "Accepted"
                )
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
