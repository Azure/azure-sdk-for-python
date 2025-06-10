# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import requests
from datetime import datetime, timezone
from io import IOBase, UnsupportedOperation
from typing import Any, Dict, Optional, Tuple
from typing_extensions import Self

from azure.core.pipeline.transport import HttpTransport, RequestsTransportResponse
from azure.core.rest import HttpRequest
from azure.storage.blob._serialize import get_api_version
from requests import Response
from urllib3 import HTTPResponse


def _build_base_file_share_headers(bearer_token_string: str, content_length: int = 0) -> Dict[str, Any]:
    return {
        'Authorization': bearer_token_string,
        'Content-Length': str(content_length),
        'x-ms-date': datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'),
        'x-ms-version': get_api_version({}),
        'x-ms-file-request-intent': 'backup',
    }


def _create_file_share_oauth(
    share_name: str,
    file_name: str,
    bearer_token_string: str,
    storage_account_name: str,
    data: bytes
) -> Tuple[str, str]:
    base_url = f"https://{storage_account_name}.file.core.windows.net/{share_name}"

    # Creates file share
    with requests.Session() as session:
        session.put(
            url=base_url,
            headers=_build_base_file_share_headers(bearer_token_string),
            params={'restype': 'share'}
        )

        # Creates the file itself
        headers = _build_base_file_share_headers(bearer_token_string)
        headers.update({'x-ms-content-length': '1024', 'x-ms-type': 'file'})
        session.put(url=base_url + "/" + file_name, headers=headers)

        # Upload the supplied data to the file
        headers = _build_base_file_share_headers(bearer_token_string, 1024)
        headers.update({'x-ms-range': 'bytes=0-1023', 'x-ms-write': 'update'})
        session.put(url=base_url + "/" + file_name, headers=headers, data=data, params={'comp': 'range'})

    return file_name, base_url


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
            # download_blob
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
            # get_blob_properties
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
            # upload_blob
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
        elif request.method == 'DELETE':
            # delete_blob
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
