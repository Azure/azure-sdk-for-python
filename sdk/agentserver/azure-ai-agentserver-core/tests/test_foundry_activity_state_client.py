# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for Foundry Activity state storage request construction."""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.ai.agentserver.core._platform_headers import CHAT_ISOLATION_KEY, USER_ISOLATION_KEY
from azure.ai.agentserver.core.storage import (
    FoundryActivityStateClient,
    FoundryActivityStateSettings,
    FoundryApiError,
    FoundryBadRequestError,
)

_BASE_URL = "https://foundry.example.com/storage/"
_SETTINGS = FoundryActivityStateSettings(storage_base_url=_BASE_URL)


def _make_response(status_code: int, body: Any) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.headers = {}
    resp.text = MagicMock(return_value=json.dumps(body))
    return resp


def _make_client(response: MagicMock) -> FoundryActivityStateClient:
    client = FoundryActivityStateClient.__new__(FoundryActivityStateClient)
    client._settings = _SETTINGS
    mock_pipeline = AsyncMock()
    mock_pipeline.send_request = AsyncMock(return_value=response)
    mock_pipeline.close = AsyncMock()
    client._client = mock_pipeline
    return client


def _sent_request(client: FoundryActivityStateClient):
    return client._client.send_request.call_args[0][0]


@pytest.mark.asyncio
async def test_read_posts_keys_to_activity_state_read() -> None:
    client = _make_client(_make_response(200, {"items": {"k/1": {"value": {"count": 1}, "etag": "e1"}}}))

    result = await client.read(["k/1", "missing"])

    request = _sent_request(client)
    assert request.method == "POST"
    assert request.url == f"{_BASE_URL}activity/state:read?api-version=v1"
    assert json.loads(request.content.decode("utf-8")) == {"keys": ["k/1", "missing"]}
    assert result == {"k/1": {"value": {"count": 1}, "etag": "e1"}}


@pytest.mark.asyncio
async def test_read_omits_missing_keys_returned_by_service() -> None:
    client = _make_client(_make_response(200, {"items": {"present": {"value": {"x": True}, "etag": "etag"}}}))

    result = await client.read(["present", "missing"])

    assert "present" in result
    assert "missing" not in result


@pytest.mark.asyncio
async def test_write_posts_changes_to_activity_state_write() -> None:
    client = _make_client(_make_response(200, {"items": {"state:key": {"etag": "new-etag"}}}))

    result = await client.write({"state:key": {"turn": 2}})

    request = _sent_request(client)
    assert request.method == "POST"
    assert request.url == f"{_BASE_URL}activity/state:write?api-version=v1"
    assert json.loads(request.content.decode("utf-8")) == {
        "changes": {"state:key": {"value": {"turn": 2}}}
    }
    assert "If-Match" not in request.headers
    assert result == {"state:key": {"etag": "new-etag"}}


@pytest.mark.asyncio
async def test_write_last_write_wins_sends_raw_latest_value_without_etag_condition() -> None:
    client = _make_client(_make_response(200, {"items": {"k": {"etag": "e2"}}}))

    await client.write({"k": {"value": "latest"}})

    request = _sent_request(client)
    assert json.loads(request.content.decode("utf-8")) == {"changes": {"k": {"value": {"value": "latest"}}}}
    assert "If-Match" not in request.headers


@pytest.mark.asyncio
async def test_delete_posts_keys_to_activity_state_delete() -> None:
    client = _make_client(_make_response(204, {}))

    await client.delete(["a/b", "c:d"])

    request = _sent_request(client)
    assert request.method == "POST"
    assert request.url == f"{_BASE_URL}activity/state:delete?api-version=v1"
    assert json.loads(request.content.decode("utf-8")) == {"keys": ["a/b", "c:d"]}


@pytest.mark.asyncio
async def test_delete_missing_keys_is_idempotent_when_service_returns_204() -> None:
    client = _make_client(_make_response(204, {}))

    await client.delete(["already-gone"])

    client._client.send_request.assert_awaited_once()


@pytest.mark.asyncio
async def test_activity_state_requests_do_not_send_isolation_headers() -> None:
    client = _make_client(_make_response(200, {"items": {}}))

    await client.read(["key"])

    request = _sent_request(client)
    assert USER_ISOLATION_KEY not in request.headers
    assert CHAT_ISOLATION_KEY not in request.headers


@pytest.mark.asyncio
async def test_write_raises_bad_request_for_400() -> None:
    client = _make_client(_make_response(400, {"error": {"message": "bad input"}}))

    with pytest.raises(FoundryBadRequestError, match="bad input"):
        await client.write({"k": {"v": 1}})


@pytest.mark.asyncio
async def test_read_raises_platform_tagged_api_error_for_500() -> None:
    client = _make_client(_make_response(500, {"error": {"message": "storage down"}}))

    with pytest.raises(FoundryApiError, match="storage down") as exc_info:
        await client.read(["k"])

    assert getattr(exc_info.value, "Azure.AI.AgentServer.PlatformError") is True


def test_settings_from_endpoint_builds_storage_base_url() -> None:
    settings = FoundryActivityStateSettings.from_endpoint("https://example.test/project/")

    assert settings.storage_base_url == "https://example.test/project/storage/"
    assert settings.build_url("activity/state:read") == "https://example.test/project/storage/activity/state:read?api-version=v1"
