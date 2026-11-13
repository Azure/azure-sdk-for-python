# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline request tests for listing memory-store items."""

import json
from typing import Any

import pytest
from azure.core.credentials import AccessToken
from azure.core.pipeline.transport import AsyncHttpTransport, HttpRequest, HttpTransport

from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient


class _Credential:
    def get_token(self, *args: Any, **kwargs: Any) -> AccessToken:
        return AccessToken("fake-token", 9_999_999_999)


class _AsyncCredential:
    async def get_token(self, *args: Any, **kwargs: Any) -> AccessToken:
        return AccessToken("fake-token", 9_999_999_999)


class _RequestCaptured(Exception):
    def __init__(self, request: HttpRequest) -> None:
        self.request = request


class _Transport(HttpTransport):
    def send(self, request: HttpRequest, **kwargs: Any) -> Any:
        raise _RequestCaptured(request)

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass

    def __exit__(self, *args: Any) -> None:
        pass


class _AsyncTransport(AsyncHttpTransport):
    async def send(self, request: HttpRequest, **kwargs: Any) -> Any:
        raise _RequestCaptured(request)

    async def open(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def __aexit__(self, *args: Any) -> None:
        pass


@pytest.mark.parametrize("kwargs", [{"scope": "user-123"}, {"body": {"scope": "user-123"}}])
def test_list_memories_sends_scope(kwargs: dict[str, Any]) -> None:
    with AIProjectClient(
        endpoint="https://example.services.ai.azure.com/api/projects/test",
        credential=_Credential(),  # type: ignore[arg-type]
        transport=_Transport(),
    ) as client:
        with pytest.raises(_RequestCaptured) as captured:
            next(iter(client.beta.memory_stores.list_memories("store", **kwargs)))
    assert json.loads(captured.value.request.body) == {"scope": "user-123"}


@pytest.mark.asyncio
@pytest.mark.parametrize("kwargs", [{"scope": "user-123"}, {"body": {"scope": "user-123"}}])
async def test_list_memories_sends_scope_async(kwargs: dict[str, Any]) -> None:
    async with AsyncAIProjectClient(
        endpoint="https://example.services.ai.azure.com/api/projects/test",
        credential=_AsyncCredential(),  # type: ignore[arg-type]
        transport=_AsyncTransport(),
    ) as client:
        with pytest.raises(_RequestCaptured) as captured:
            async for _ in client.beta.memory_stores.list_memories("store", **kwargs):
                pass
    assert json.loads(captured.value.request.body) == {"scope": "user-123"}
