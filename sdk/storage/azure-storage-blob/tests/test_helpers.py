# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from itertools import count
from datetime import datetime, timezone
from io import IOBase, UnsupportedOperation
from typing import Any, Dict, Optional, Tuple

import requests
from requests import Response
from typing_extensions import Self
from urllib3 import HTTPResponse

from azure.core.pipeline.transport import (  # pylint: disable=no-name-in-module
    RequestsTransport,
    RequestsTransportResponse,
)
from azure.core.rest import HttpRequest
from azure.storage.blob._serialize import get_api_version


def _deterministic_urandom():
    counter = count(1)
    return lambda size: next(counter).to_bytes(size, "big")


def _build_base_file_share_headers(bearer_token_string: str, content_length: int = 0) -> Dict[str, Any]:
    return {
        "Authorization": bearer_token_string,
        "Content-Length": str(content_length),
        "x-ms-date": datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "x-ms-version": get_api_version({}),
        "x-ms-file-request-intent": "backup",
    }


def _create_file_share_oauth(
    share_name: str, file_name: str, bearer_token_string: str, storage_account_name: str, data: bytes, is_live: bool
) -> Tuple[str, str]:
    base_url = f"https://{storage_account_name}.file.core.windows.net/{share_name}"

    if not is_live:
        return file_name, base_url

    # Creates file share
    with requests.Session() as session:
        session.put(
            url=base_url, headers=_build_base_file_share_headers(bearer_token_string), params={"restype": "share"}
        )

        # Creates the file itself
        headers = _build_base_file_share_headers(bearer_token_string)
        headers.update({"x-ms-content-length": "1024", "x-ms-type": "file"})
        session.put(url=base_url + "/" + file_name, headers=headers)

        # Upload the supplied data to the file
        headers = _build_base_file_share_headers(bearer_token_string, 1024)
        headers.update({"x-ms-range": "bytes=0-1023", "x-ms-write": "update"})
        session.put(url=base_url + "/" + file_name, headers=headers, data=data, params={"comp": "range"})

    return file_name, base_url


def _parse_session_token(auth: str) -> str:
    """Extract the token from a "Session {token}:{signature}" Authorization header.

    :param str auth: The raw Authorization header value.
    :return: The session token portion (before the ':').
    :rtype: str
    """
    assert auth.startswith("Session ")
    return auth[len("Session ") :].split(":", 1)[0]


def _find_session_policy(pipeline: Any, policy_name: str = "StorageSessionPolicy") -> Any:
    """Return the session policy instance on a client pipeline, matched by class name.

    Matching by name avoids importing SDK internals into the test modules.

    :param pipeline: The client pipeline to search (e.g. ``client._pipeline``).
    :type pipeline: Any
    :param str policy_name: The policy class name to find. Use "StorageSessionPolicy"
        for the sync stack and "AsyncStorageSessionPolicy" for the async stack.
    :return: The matching policy instance.
    :rtype: Any
    """
    for policy in getattr(pipeline, "_impl_policies", []):
        if type(policy).__name__ == policy_name:
            return policy
    raise AssertionError(f"{policy_name} not found on the pipeline")


class CaptureAuthHeader:
    """Captures per-label Authorization headers via ``raw_response_hook`` callbacks.

    Encapsulates the captured-headers dict so the hook factory doesn't need a
    closure over a test-local variable. Works for both sync and async clients,
    since the response hook is invoked as a plain callable in both stacks.
    """

    def __init__(self) -> None:
        self.captured: Dict[str, str] = {}

    def hook(self, label: str):
        """Return a ``raw_response_hook`` that records the request's Authorization header.

        :param str label: The key under which to store the captured header.
        :return: A callable suitable for ``raw_response_hook``.
        :rtype: callable
        """

        def _hook(response):
            self.captured[label] = response.http_request.headers.get("Authorization", "")

        return _hook

    def __getitem__(self, label: str) -> str:
        return self.captured[label]


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


class MockClientResponse(Response):
    def __init__(
        self, url: str, body_bytes: bytes, headers: Dict[str, Any], status: int = 200, reason: str = "OK"
    ) -> None:
        super(MockClientResponse).__init__()
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


class MockLegacyTransport(RequestsTransport):
    """
    This transport returns http response objects from azure core pipelines and is
    intended only to test our backwards compatibility support.
    """

    def send(self, request: HttpRequest, **kwargs: Any) -> RequestsTransportResponse:  # pylint: disable=unused-argument
        if request.method == "GET":
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
                requests_response=MockClientResponse(
                    request.url,
                    b"Hello World!",
                    headers,
                ),
            )
        elif request.method == "HEAD":
            # get_blob_properties
            rest_response = RequestsTransportResponse(
                request=request,
                requests_response=MockClientResponse(
                    request.url,
                    b"",
                    {
                        "Content-Type": "application/octet-stream",
                        "Content-Length": "1024",
                    },
                ),
            )
        elif request.method == "PUT":
            # upload_blob
            rest_response = RequestsTransportResponse(
                request=request,
                requests_response=MockClientResponse(
                    request.url,
                    b"",
                    {
                        "Content-Length": "0",
                    },
                    201,
                    "Created",
                ),
            )
        elif request.method == "DELETE":
            # delete_blob
            rest_response = RequestsTransportResponse(
                request=request,
                requests_response=MockClientResponse(
                    request.url,
                    b"",
                    {
                        "Content-Length": "0",
                    },
                    202,
                    "Accepted",
                ),
            )
        else:
            raise ValueError("The request is not accepted as part of MockLegacyTransport.")
        return rest_response

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: Any) -> None:
        pass

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass
