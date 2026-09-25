# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import Any, Dict, Optional
from urllib.parse import urlparse

from requests import Response
from typing_extensions import Self
from urllib3 import HTTPResponse

from azure.core.pipeline.transport import HttpTransport, RequestsTransportResponse  # pylint: disable=no-name-in-module
from azure.core.rest import HttpRequest


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


class MockHttpClientResponse(Response):
    def __init__(
        self, url: str, body_bytes: bytes, headers: Dict[str, Any], status: int = 200, reason: str = "OK"
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
        if request.method == "GET":
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
                ),
            )
        elif request.method == "HEAD":
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
                ),
            )
        elif request.method == "PUT":
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
                    "Created",
                ),
            )
        elif request.method == "PATCH":
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
                        "OK",
                    ),
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
                        "Accepted",
                    ),
                )
        elif request.method == "DELETE":
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
                    "Accepted",
                ),
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
