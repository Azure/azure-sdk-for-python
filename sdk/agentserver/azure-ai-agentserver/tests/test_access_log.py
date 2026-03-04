# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for structured access logging: AccessLogHelper, AccessLogMiddleware."""
import json
import logging
import os
from unittest.mock import patch

import httpx
import pytest

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver import AgentServer
from azure.ai.agentserver._access_log import (
    AccessLogHelper,
    _ACCESS_LOGGER_NAME,
    _KeyValueFormatter,
)
from azure.ai.agentserver._constants import Constants


# ---------------------------------------------------------------------------
# Test agents
# ---------------------------------------------------------------------------


class _FastAgent(AgentServer):
    """Returns immediately."""

    async def invoke(self, request: Request) -> Response:
        return JSONResponse({"ok": True})


class _EchoAgent(AgentServer):
    """Echoes body length."""

    async def invoke(self, request: Request) -> Response:
        body = await request.body()
        return JSONResponse({"body_len": len(body)})


class _ErrorAgent(AgentServer):
    """Always raises."""

    async def invoke(self, request: Request) -> Response:
        raise RuntimeError("boom")


class _StreamAgent(AgentServer):
    """Returns a streaming response."""

    async def invoke(self, request: Request) -> Response:
        async def _gen():
            yield b"chunk1"
            yield b"chunk2"

        return StreamingResponse(_gen(), media_type="text/plain")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_access_logger():
    """Remove handlers from the access logger between tests."""
    logger = logging.getLogger(_ACCESS_LOGGER_NAME)
    yield
    logger.handlers.clear()


class _LogCapture(logging.Handler):
    """Captures log records for assertion."""

    def __init__(self):  # type: ignore[no-untyped-def]
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


# ===========================================================================
# AccessLogHelper unit tests
# ===========================================================================


class TestAccessLogHelperInit:
    """Test AccessLogHelper initialization and gating."""

    def test_disabled_by_default(self):
        helper = AccessLogHelper()
        assert not helper.enabled

    def test_enabled_via_constructor(self):
        helper = AccessLogHelper(enabled=True)
        assert helper.enabled

    def test_enabled_via_env_var(self):
        with patch.dict(os.environ, {Constants.AGENT_ENABLE_ACCESS_LOG: "true"}):
            helper = AccessLogHelper()
            assert helper.enabled

    def test_env_var_false(self):
        with patch.dict(os.environ, {Constants.AGENT_ENABLE_ACCESS_LOG: "false"}):
            helper = AccessLogHelper()
            assert not helper.enabled

    def test_constructor_overrides_env_var(self):
        with patch.dict(os.environ, {Constants.AGENT_ENABLE_ACCESS_LOG: "true"}):
            helper = AccessLogHelper(enabled=False)
            assert not helper.enabled

    def test_log_request_noop_when_disabled(self):
        helper = AccessLogHelper(enabled=False)
        # Should not raise
        helper.log_request(
            method="POST",
            path="/invocations",
            status=200,
            duration_ms=10.5,
            request_size=100,
            response_size=50,
            invocation_id="abc",
            client_ip="127.0.0.1",
            user_agent="test",
            protocol="HTTP/1.1",
        )


class TestAccessLogHelperEmit:
    """Test that AccessLogHelper emits structured log entries."""

    def test_emits_log_record(self):
        helper = AccessLogHelper(enabled=True)
        capture = _LogCapture()
        logging.getLogger(_ACCESS_LOGGER_NAME).addHandler(capture)

        helper.log_request(
            method="POST",
            path="/invocations",
            status=200,
            duration_ms=42.3,
            request_size=1024,
            response_size=512,
            invocation_id="inv-123",
            client_ip="10.0.0.1",
            user_agent="python-httpx/0.27",
            protocol="HTTP/2",
        )

        assert len(capture.records) == 1
        rec = capture.records[0]
        assert rec.method == "POST"  # type: ignore[attr-defined]
        assert rec.path == "/invocations"  # type: ignore[attr-defined]
        assert rec.status == 200  # type: ignore[attr-defined]
        assert rec.protocol == "HTTP/2"  # type: ignore[attr-defined]
        assert rec.duration_ms == 42.3  # type: ignore[attr-defined]
        assert rec.request_size == 1024  # type: ignore[attr-defined]
        assert rec.response_size == 512  # type: ignore[attr-defined]
        assert rec.invocation_id == "inv-123"  # type: ignore[attr-defined]
        assert rec.client_ip == "10.0.0.1"  # type: ignore[attr-defined]
        assert rec.user_agent == "python-httpx/0.27"  # type: ignore[attr-defined]

    def test_log_message_format(self):
        helper = AccessLogHelper(enabled=True)
        capture = _LogCapture()
        logging.getLogger(_ACCESS_LOGGER_NAME).addHandler(capture)

        helper.log_request(
            method="GET",
            path="/liveness",
            status=200,
            duration_ms=1.0,
            request_size=0,
            response_size=20,
            invocation_id="",
            client_ip="127.0.0.1",
            user_agent="curl/8.0",
            protocol="HTTP/1.1",
        )

        rec = capture.records[0]
        assert "GET" in rec.getMessage()
        assert "/liveness" in rec.getMessage()
        assert "200" in rec.getMessage()


class TestKeyValueFormatter:
    """Test the fallback key=value formatter."""

    def test_formats_fields(self):
        formatter = _KeyValueFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test",
            args=(),
            exc_info=None,
        )
        record.method = "POST"  # type: ignore[attr-defined]
        record.path = "/invocations"  # type: ignore[attr-defined]
        record.status = 200  # type: ignore[attr-defined]
        record.protocol = "HTTP/2"  # type: ignore[attr-defined]
        record.duration_ms = 42.3  # type: ignore[attr-defined]
        record.request_size = 100  # type: ignore[attr-defined]
        record.response_size = 50  # type: ignore[attr-defined]
        record.invocation_id = "inv-1"  # type: ignore[attr-defined]
        record.client_ip = "10.0.0.1"  # type: ignore[attr-defined]
        record.user_agent = "test-ua"  # type: ignore[attr-defined]

        formatted = formatter.format(record)
        assert "method=POST" in formatted
        assert "path=/invocations" in formatted
        assert "status=200" in formatted
        assert "protocol=HTTP/2" in formatted
        assert "duration_ms=42.3" in formatted
        assert "invocation_id=inv-1" in formatted
        assert "client_ip=10.0.0.1" in formatted


# ===========================================================================
# AgentServer integration: AccessLogMiddleware
# ===========================================================================


class TestAccessLogMiddleware:
    """Test structured access logging through the full middleware stack."""

    @pytest.mark.asyncio
    async def test_no_access_log_when_disabled(self):
        capture = _LogCapture()
        logging.getLogger(_ACCESS_LOGGER_NAME).addHandler(capture)

        agent = _FastAgent(enable_access_log=False)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            await client.post("/invocations", content=b"{}")

        assert len(capture.records) == 0

    @pytest.mark.asyncio
    async def test_access_log_emitted_on_request(self):
        agent = _FastAgent(enable_access_log=True)
        capture = _LogCapture()
        logging.getLogger(_ACCESS_LOGGER_NAME).addHandler(capture)

        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            await client.post("/invocations", content=b'{"hello": "world"}')

        assert len(capture.records) == 1
        rec = capture.records[0]
        assert rec.method == "POST"  # type: ignore[attr-defined]
        assert rec.path == "/invocations"  # type: ignore[attr-defined]
        assert rec.status == 200  # type: ignore[attr-defined]
        assert rec.duration_ms > 0  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    async def test_health_paths_excluded(self):
        agent = _FastAgent(enable_access_log=True)
        capture = _LogCapture()
        logging.getLogger(_ACCESS_LOGGER_NAME).addHandler(capture)

        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            await client.get("/liveness")
            await client.get("/readiness")

        # Health endpoints don't generate access log entries
        assert len(capture.records) == 0

    @pytest.mark.asyncio
    async def test_error_responses_logged(self):
        agent = _ErrorAgent(enable_access_log=True)
        capture = _LogCapture()
        logging.getLogger(_ACCESS_LOGGER_NAME).addHandler(capture)

        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            await client.post("/invocations", content=b"{}")

        assert len(capture.records) == 1
        rec = capture.records[0]
        assert rec.status == 500  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    async def test_streaming_response_logged(self):
        agent = _StreamAgent(enable_access_log=True)
        capture = _LogCapture()
        logging.getLogger(_ACCESS_LOGGER_NAME).addHandler(capture)

        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            await client.post("/invocations", content=b"{}")

        assert len(capture.records) == 1
        rec = capture.records[0]
        assert rec.status == 200  # type: ignore[attr-defined]
        assert rec.response_size > 0  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    async def test_invocation_id_captured(self):
        agent = _FastAgent(enable_access_log=True)
        capture = _LogCapture()
        logging.getLogger(_ACCESS_LOGGER_NAME).addHandler(capture)

        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations", content=b"{}")
            expected_id = resp.headers[Constants.INVOCATION_ID_HEADER]

        assert len(capture.records) == 1
        rec = capture.records[0]
        assert rec.invocation_id == expected_id  # type: ignore[attr-defined]

    @pytest.mark.asyncio
    async def test_multiple_requests_produce_multiple_entries(self):
        agent = _FastAgent(enable_access_log=True)
        capture = _LogCapture()
        logging.getLogger(_ACCESS_LOGGER_NAME).addHandler(capture)

        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            await client.post("/invocations", content=b"{}")
            await client.post("/invocations", content=b"{}")
            await client.post("/invocations", content=b"{}")

        assert len(capture.records) == 3


class TestAccessLogWithEnvVar:
    """Test enabling access log via environment variable."""

    @pytest.mark.asyncio
    async def test_env_var_enables_access_log(self):
        with patch.dict(os.environ, {Constants.AGENT_ENABLE_ACCESS_LOG: "true"}):
            agent = _FastAgent()

        capture = _LogCapture()
        logging.getLogger(_ACCESS_LOGGER_NAME).addHandler(capture)

        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            await client.post("/invocations", content=b"{}")

        assert len(capture.records) == 1


class TestAccessLogJsonFormat:
    """Test JSON formatting when python-json-logger is installed."""

    @pytest.mark.asyncio
    async def test_json_format_output(self):
        helper = AccessLogHelper(enabled=True)

        # Get the handler's formatter output
        access_logger = logging.getLogger(_ACCESS_LOGGER_NAME)
        # Find a handler with JsonFormatter
        json_handler = None
        for h in access_logger.handlers:
            from pythonjsonlogger.json import JsonFormatter

            if isinstance(h.formatter, JsonFormatter):
                json_handler = h
                break

        if json_handler is None:
            pytest.skip("python-json-logger not producing JsonFormatter handler")

        # Capture formatted output
        capture = _LogCapture()
        capture.setFormatter(json_handler.formatter)
        access_logger.addHandler(capture)

        helper.log_request(
            method="POST",
            path="/invocations",
            status=200,
            duration_ms=42.3,
            request_size=1024,
            response_size=512,
            invocation_id="inv-json",
            client_ip="10.0.0.1",
            user_agent="test-ua",
            protocol="HTTP/2",
        )

        assert len(capture.records) == 1
        formatted = capture.formatter.format(capture.records[0])  # type: ignore[union-attr]
        parsed = json.loads(formatted)
        assert parsed["method"] == "POST"
        assert parsed["path"] == "/invocations"
        assert parsed["status"] == 200
        assert parsed["protocol"] == "HTTP/2"
        assert parsed["invocation_id"] == "inv-json"
