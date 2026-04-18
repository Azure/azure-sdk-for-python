# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for FoundryStorageLoggingPolicy."""

from __future__ import annotations

import logging
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.ai.agentserver.responses.store._foundry_logging_policy import FoundryStorageLoggingPolicy, _mask_storage_url


def _make_request(method: str = "GET", url: str = "https://storage.example.com/responses/r1") -> MagicMock:
    http_request = MagicMock()
    http_request.method = method
    http_request.url = url
    http_request.headers = {"x-ms-client-request-id": "test-client-id-123"}
    pipeline_request = MagicMock()
    pipeline_request.http_request = http_request
    return pipeline_request


def _make_response(status_code: int = 200, headers: dict | None = None) -> MagicMock:
    http_response = MagicMock()
    http_response.status_code = status_code
    http_response.headers = headers or {"x-ms-request-id": "server-req-456"}
    response = MagicMock()
    response.http_response = http_response
    return response


@pytest.mark.asyncio
async def test_logging_policy_logs_successful_request(caplog: pytest.LogCaptureFixture) -> None:
    policy = FoundryStorageLoggingPolicy()
    next_policy = AsyncMock()
    next_policy.send = AsyncMock(return_value=_make_response(200))
    policy.next = next_policy

    request = _make_request("GET", "https://storage.example.com/responses/r1")

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        await policy.send(request)

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.INFO
    assert "GET" in record.message
    assert "200" in record.message
    assert "test-client-id-123" in record.message
    assert "server-req-456" in record.message
    assert "ms" in record.message


@pytest.mark.asyncio
async def test_logging_policy_logs_error_response_at_warning(caplog: pytest.LogCaptureFixture) -> None:
    policy = FoundryStorageLoggingPolicy()
    next_policy = AsyncMock()
    next_policy.send = AsyncMock(return_value=_make_response(500))
    policy.next = next_policy

    request = _make_request("PUT", "https://storage.example.com/responses/r1")

    with caplog.at_level(logging.WARNING, logger="azure.ai.agentserver"):
        await policy.send(request)

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.WARNING
    assert "PUT" in record.message
    assert "500" in record.message


@pytest.mark.asyncio
async def test_logging_policy_logs_transport_failure(caplog: pytest.LogCaptureFixture) -> None:
    policy = FoundryStorageLoggingPolicy()
    next_policy = AsyncMock()
    next_policy.send = AsyncMock(side_effect=ConnectionError("network failure"))
    policy.next = next_policy

    request = _make_request("POST", "https://storage.example.com/responses")

    with caplog.at_level(logging.WARNING, logger="azure.ai.agentserver"):
        with pytest.raises(ConnectionError):
            await policy.send(request)

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.WARNING
    assert "POST" in record.message
    assert "failed" in record.message.lower()
    assert "test-client-id-123" in record.message


@pytest.mark.asyncio
async def test_logging_policy_handles_missing_correlation_headers(caplog: pytest.LogCaptureFixture) -> None:
    policy = FoundryStorageLoggingPolicy()
    next_policy = AsyncMock()
    next_policy.send = AsyncMock(return_value=_make_response(200, headers={}))
    policy.next = next_policy

    request = _make_request("DELETE", "https://storage.example.com/responses/r1")
    request.http_request.headers = {}  # No correlation headers

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        await policy.send(request)

    assert len(caplog.records) == 1
    assert "DELETE" in caplog.records[0].message
    assert "200" in caplog.records[0].message


@pytest.mark.asyncio
async def test_logging_policy_logs_isolation_header_presence(caplog: pytest.LogCaptureFixture) -> None:
    """Isolation header *presence* is logged but actual values are NOT."""
    policy = FoundryStorageLoggingPolicy()
    next_policy = AsyncMock()
    next_policy.send = AsyncMock(return_value=_make_response(200))
    policy.next = next_policy

    request = _make_request("GET", "https://storage.example.com/responses/r1")
    request.http_request.headers["x-agent-user-isolation-key"] = "secret-user-key"
    request.http_request.headers["x-agent-chat-isolation-key"] = "secret-chat-key"

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        await policy.send(request)

    msg = caplog.records[0].message
    assert "has_user_isolation_key=True" in msg
    assert "has_chat_isolation_key=True" in msg
    # Values must never appear
    assert "secret-user-key" not in msg
    assert "secret-chat-key" not in msg


@pytest.mark.asyncio
async def test_logging_policy_logs_isolation_header_absence(caplog: pytest.LogCaptureFixture) -> None:
    """When isolation headers are absent both flags are False."""
    policy = FoundryStorageLoggingPolicy()
    next_policy = AsyncMock()
    next_policy.send = AsyncMock(return_value=_make_response(200))
    policy.next = next_policy

    request = _make_request("GET", "https://storage.example.com/responses/r1")
    # Default _make_request has no isolation headers

    with caplog.at_level(logging.INFO, logger="azure.ai.agentserver"):
        await policy.send(request)

    msg = caplog.records[0].message
    assert "has_user_isolation_key=False" in msg
    assert "has_chat_isolation_key=False" in msg


@pytest.mark.asyncio
async def test_logging_policy_failure_logs_isolation_header_presence(caplog: pytest.LogCaptureFixture) -> None:
    """Isolation presence is also logged on transport failure."""
    policy = FoundryStorageLoggingPolicy()
    next_policy = AsyncMock()
    next_policy.send = AsyncMock(side_effect=ConnectionError("oops"))
    policy.next = next_policy

    request = _make_request("POST", "https://storage.example.com/responses")
    request.http_request.headers["x-agent-chat-isolation-key"] = "secret"

    with caplog.at_level(logging.WARNING, logger="azure.ai.agentserver"):
        with pytest.raises(ConnectionError):
            await policy.send(request)

    msg = caplog.records[0].message
    assert "has_user_isolation_key=False" in msg
    assert "has_chat_isolation_key=True" in msg
    assert "secret" not in msg


class TestMaskStorageUrl:
    """Tests for the _mask_storage_url helper."""

    def test_masks_host_and_project_path(self) -> None:
        result = _mask_storage_url(
            "https://acct.services.ai.azure.com/api/projects/myproj"
            "/storage/responses/resp_123?api-version=2025-01-01"
        )
        assert result == "***/storage/responses/resp_123?api-version=2025-01-01"
        assert "acct.services.ai.azure.com" not in result
        assert "myproj" not in result

    def test_strips_non_api_version_query_params(self) -> None:
        result = _mask_storage_url(
            "https://myproject.foundry.azure.com/api/projects/p1"
            "/storage/responses?api-version=1&conversation_id=abc&previous_response_id=xyz"
        )
        assert "conversation_id" not in result
        assert "previous_response_id" not in result
        assert result == "***/storage/responses?api-version=1"

    def test_preserves_storage_relative_path(self) -> None:
        result = _mask_storage_url(
            "https://myhost.com/api/projects/proj/storage/responses/resp_abc/input_items?api-version=1"
        )
        assert result == "***/storage/responses/resp_abc/input_items?api-version=1"
        assert "myhost.com" not in result
        assert "proj" not in result

    def test_simple_storage_url(self) -> None:
        result = _mask_storage_url("https://myhost.com/storage/items/batch/retrieve")
        assert result == "***/storage/items/batch/retrieve"

    def test_no_storage_segment_returns_redacted(self) -> None:
        assert _mask_storage_url("https://example.com/other/path") == "(redacted)"

    def test_empty_returns_redacted(self) -> None:
        assert _mask_storage_url("") == "(redacted)"
