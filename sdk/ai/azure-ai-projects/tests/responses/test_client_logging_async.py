# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async unit tests for logger wiring and transport logging behavior."""

import logging
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from azure.core.credentials_async import AsyncTokenCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.aio._patch import _OpenAILoggingTransport

from openai_test_helpers import ASYNC_OPENAI_PATCH, ASYNC_TOKEN_PROVIDER_PATCH, make_async_client, mock_openai


class DummyAsyncTokenCredential(AsyncTokenCredential):
    """A dummy async credential that returns None for testing purposes."""

    async def get_token(self, *scopes: str, **kwargs: Any):  # type: ignore[override]
        return None

    async def close(self) -> None:
        pass


def _attach_file_handler(logger_name: str, log_file: Path) -> logging.FileHandler:
    handler = logging.FileHandler(log_file, encoding="utf-8")
    handler.setLevel(logging.DEBUG)
    logger = logging.getLogger(logger_name)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return handler


def _read_log_file(handler: logging.FileHandler, log_file: Path) -> str:
    handler.flush()
    return log_file.read_text(encoding="utf-8")


def _assert_json_request_body(log_text: str, expected: bool) -> None:
    marker = 'Body:\n  {"message":"hello"}'
    assert (marker in log_text) is expected


def _assert_json_response_body(log_text: str, expected: bool) -> None:
    marker = 'Body:\n {"result":"ok"}'
    assert (marker in log_text) is expected


def _assert_bearer_token_logging(log_text: str, logging_enabled: bool) -> None:
    raw_token = "authorization: Bearer secret-token"
    redacted_token = "authorization: Bearer <REDACTED>"
    assert (raw_token in log_text) is logging_enabled
    assert (redacted_token in log_text) is (not logging_enabled)


@pytest.fixture
def restore_logger_state():
    logger_names = [
        "azure",
        "azure.identity",
        "azure.core.pipeline.policies.http_logging_policy",
        "azure.ai.projects.openai_transport",
    ]
    original_state = {}
    for logger_name in logger_names:
        logger = logging.getLogger(logger_name)
        original_state[logger_name] = {
            "handlers": list(logger.handlers),
            "level": logger.level,
            "propagate": logger.propagate,
        }
        logger.handlers = []

    yield

    for logger_name, state in original_state.items():
        logger = logging.getLogger(logger_name)
        for handler in list(logger.handlers):
            logger.removeHandler(handler)
            try:
                handler.close()
            except Exception:  # pylint: disable=broad-exception-caught
                pass
        logger.handlers = list(state["handlers"])
        logger.setLevel(state["level"])
        logger.propagate = state["propagate"]


def test_project_client_console_logging_configures_loggers_async(monkeypatch, restore_logger_state):
    """Console logging should attach a shared stream handler and enable verbose logging."""
    monkeypatch.setenv("AZURE_AI_PROJECTS_CONSOLE_LOGGING", "true")

    with (
        patch("azure.ai.projects.aio._patch.AIProjectClientGenerated.__init__", return_value=None),
        patch("azure.ai.projects.aio._patch.TelemetryOperations", return_value=MagicMock()),
    ):
        client = AIProjectClient(
            endpoint="https://example.com/api/projects/test", credential=DummyAsyncTokenCredential()
        )

    azure_logger = logging.getLogger("azure")
    identity_logger = logging.getLogger("azure.identity")
    http_logging_logger = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
    transport_logger = logging.getLogger("azure.ai.projects.openai_transport")

    assert client._console_logging_enabled is True
    assert client._kwargs["logging_enable"] is True
    assert azure_logger.level == logging.DEBUG
    assert identity_logger.level == logging.ERROR
    assert http_logging_logger.level == logging.ERROR
    assert len(azure_logger.handlers) == 1
    assert len(transport_logger.handlers) == 0
    assert isinstance(azure_logger.handlers[0], logging.StreamHandler)


def test_project_client_without_console_logging_leaves_loggers_unwired_async(monkeypatch, restore_logger_state):
    """Without the env flag, the constructor should not attach handlers or override logging_enable."""
    monkeypatch.delenv("AZURE_AI_PROJECTS_CONSOLE_LOGGING", raising=False)

    with (
        patch("azure.ai.projects.aio._patch.AIProjectClientGenerated.__init__", return_value=None),
        patch("azure.ai.projects.aio._patch.TelemetryOperations", return_value=MagicMock()),
    ):
        client = AIProjectClient(
            endpoint="https://example.com/api/projects/test",
            credential=DummyAsyncTokenCredential(),
            logging_enable=False,
        )

    assert client._console_logging_enabled is False
    assert client._kwargs["logging_enable"] is False
    assert logging.getLogger("azure").handlers == []
    assert logging.getLogger("azure.ai.projects.openai_transport").handlers == []


def test_get_openai_client_logs_creation_message_async(tmp_path, restore_logger_state):
    """Creating the AsyncOpenAI client should write the creation log message to the log file."""
    client = make_async_client(logging_enable=False)
    mock_cls, _ = mock_openai()
    log_file = tmp_path / "openai_client_async.log"
    handler = _attach_file_handler("azure.ai.projects.aio._patch", log_file)

    with (
        patch(ASYNC_OPENAI_PATCH, mock_cls),
        patch(ASYNC_TOKEN_PROVIDER_PATCH, return_value="provider"),
    ):
        client.get_openai_client(agent_name="my-agent")

    log_text = _read_log_file(handler, log_file)

    assert log_file.exists()
    assert "[get_openai_client] Creating OpenAI client using Entra ID authentication" in log_text
    assert "/agents/my-agent/endpoint/protocols/openai" in log_text


@pytest.mark.asyncio
async def test_openai_transport_full_logging_writes_request_response_and_raw_token_to_file_async(
    tmp_path, restore_logger_state
):
    """With logging_enable=True, the log file should include request, response, JSON bodies, and the raw bearer token."""
    request = httpx.Request(
        "POST",
        "https://example.com/openai/v1/responses",
        headers={"authorization": "Bearer secret-token", "content-type": "application/json"},
        content=b'{"message":"hello"}',
    )
    response = httpx.Response(
        200,
        request=request,
        headers={"content-type": "application/json"},
        content=b'{"result":"ok"}',
    )
    log_file = tmp_path / "transport_full_async.log"
    handler = _attach_file_handler("azure.ai.projects.openai_transport", log_file)

    with patch.object(httpx.AsyncHTTPTransport, "handle_async_request", new=AsyncMock(return_value=response)):
        result = await _OpenAILoggingTransport(logging_enabled=True).handle_async_request(request)

    log_text = _read_log_file(handler, log_file)

    assert result is response
    assert log_file.exists()
    assert "==> Request:" in log_text
    assert "<== Response:" in log_text
    _assert_bearer_token_logging(log_text, logging_enabled=True)
    _assert_json_request_body(log_text, expected=True)
    _assert_json_response_body(log_text, expected=True)
    assert "Body: [Content exists]" not in log_text


@pytest.mark.asyncio
async def test_openai_transport_reduced_logging_writes_metadata_only_to_file_async(tmp_path, restore_logger_state):
    """With logging_enable=False, the log file should include metadata but not the raw bearer token or JSON bodies."""
    request = httpx.Request(
        "POST",
        "https://example.com/openai/v1/responses",
        headers={"authorization": "Bearer secret-token", "content-type": "application/json"},
        content=b'{"message":"hello"}',
    )
    response = httpx.Response(
        200,
        request=request,
        headers={"content-type": "application/json"},
        content=b'{"result":"ok"}',
    )
    log_file = tmp_path / "transport_reduced_async.log"
    handler = _attach_file_handler("azure.ai.projects.openai_transport", log_file)

    with patch.object(httpx.AsyncHTTPTransport, "handle_async_request", new=AsyncMock(return_value=response)):
        result = await _OpenAILoggingTransport(logging_enabled=False).handle_async_request(request)

    log_text = _read_log_file(handler, log_file)

    assert result is response
    assert log_file.exists()
    assert "==> Request:" in log_text
    assert "<== Response:" in log_text
    _assert_bearer_token_logging(log_text, logging_enabled=False)
    _assert_json_request_body(log_text, expected=False)
    _assert_json_response_body(log_text, expected=False)
    assert log_text.count("Body: [Content exists]") == 2
