# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""In-memory mock transport shared by the HTTP operation unit tests.

No network is used. A ``handler`` callable maps each outgoing request to a
canned ``(status_code, body, headers)`` triple and the transport wraps it in a
real ``azure-core`` response object. This lets the tests assert routes, the
``Foundry-Features`` opt-in header, request/response serialization, paging, and
audio streaming without recordings or a live service.
"""

import json
import time
from typing import Any, Callable, Optional, Tuple
from urllib.parse import urlsplit

from azure.core.credentials import AccessToken
from azure.core.utils import case_insensitive_dict
from azure.core.rest._http_response_impl import HttpResponseImpl
from azure.core.rest._http_response_impl_async import AsyncHttpResponseImpl

# handler(request) -> (status_code, body, headers)
Handler = Callable[[Any], Tuple[int, Any, Optional[dict]]]


class _InMemoryInternalResponse:
    """Stand-in for a transport's raw response object.

    The synchronous ``HttpResponseImpl`` calls ``close()`` on its underlying
    transport response once the (already in-memory) content is read; this stub
    satisfies that call without a real network response.
    """

    def close(self) -> None:
        pass


def _build_response(request: Any, status: int, body: Any, headers: Optional[dict], is_async: bool):
    resolved_headers = case_insensitive_dict(headers or {})
    if isinstance(body, (bytes, bytearray)):
        content = bytes(body)
        resolved_headers.setdefault("content-type", "application/octet-stream")
    elif body is None:
        content = b""
    else:
        content = json.dumps(body).encode("utf-8")
        resolved_headers.setdefault("content-type", "application/json")

    response_cls = AsyncHttpResponseImpl if is_async else HttpResponseImpl
    response = response_cls(
        request=request,
        internal_response=None if is_async else _InMemoryInternalResponse(),
        status_code=status,
        reason="OK",
        content_type=resolved_headers.get("content-type"),
        headers=resolved_headers,
        stream_download_generator=None,
        block_size=4096,
    )
    # The content is already in memory, so short-circuit any stream download.
    response._content = content  # pylint: disable=protected-access
    return response


class MockTransport:
    """Synchronous transport that records requests and replays canned responses."""

    def __init__(self, handler: Handler) -> None:
        self._handler = handler
        self.requests = []

    def __enter__(self) -> "MockTransport":
        return self

    def __exit__(self, *args: Any) -> None:
        pass

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass

    def send(self, request: Any, **kwargs: Any):
        self.requests.append(request)
        status, body, headers = self._handler(request)
        return _build_response(request, status, body, headers, is_async=False)


class AsyncMockTransport:
    """Asynchronous transport that records requests and replays canned responses."""

    def __init__(self, handler: Handler) -> None:
        self._handler = handler
        self.requests = []

    async def __aenter__(self) -> "AsyncMockTransport":
        return self

    async def __aexit__(self, *args: Any) -> None:
        pass

    async def open(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def send(self, request: Any, **kwargs: Any):
        self.requests.append(request)
        status, body, headers = self._handler(request)
        return _build_response(request, status, body, headers, is_async=True)


def request_path(request: Any) -> str:
    return urlsplit(request.url).path


def request_query(request: Any) -> str:
    return urlsplit(request.url).query


def request_json(request: Any) -> Any:
    content = request.content
    if isinstance(content, (bytes, bytearray)):
        content = content.decode("utf-8")
    return json.loads(content)


class FakeCredential:
    """Minimal synchronous TokenCredential stand-in (never contacts an authority)."""

    def get_token(self, *scopes: Any, **kwargs: Any) -> AccessToken:
        return AccessToken("fake-token", int(time.time()) + 3600)


class FakeAsyncCredential:
    """Minimal asynchronous TokenCredential stand-in (never contacts an authority)."""

    async def get_token(self, *scopes: Any, **kwargs: Any) -> AccessToken:
        return AccessToken("fake-token", int(time.time()) + 3600)

    async def close(self) -> None:
        return None
