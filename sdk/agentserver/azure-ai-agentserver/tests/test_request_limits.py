# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for invoke timeout guards."""
import asyncio
import os
from unittest.mock import patch

import httpx
import pytest

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver import AgentServer
from azure.ai.agentserver._constants import Constants


# ---------------------------------------------------------------------------
# Agent factory functions
# ---------------------------------------------------------------------------


def _make_slow_agent(**kwargs) -> AgentServer:
    """Create an agent that sleeps forever — used to test invoke timeout."""
    server = AgentServer(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        await asyncio.sleep(999)
        return Response(content=b"done")

    return server


def _make_fast_agent(**kwargs) -> AgentServer:
    """Create an agent that returns immediately — used to verify no false timeout."""
    server = AgentServer(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        return JSONResponse({"ok": True})

    return server


# ===========================================================================
# Request timeout
# ===========================================================================


class TestRequestTimeoutConstants:
    """Verify constants are wired correctly."""

    def test_default_is_300_seconds(self):
        assert Constants.DEFAULT_REQUEST_TIMEOUT == 300

    def test_env_var_name(self):
        assert Constants.AGENT_REQUEST_TIMEOUT == "AGENT_REQUEST_TIMEOUT"


class TestRequestTimeoutResolution:
    """Test the resolution hierarchy: explicit > env > default."""

    def test_explicit_value(self):
        agent = _make_fast_agent(request_timeout=60)
        assert agent._request_timeout == 60

    def test_explicit_zero_disables(self):
        agent = _make_fast_agent(request_timeout=0)
        assert agent._request_timeout == 0

    def test_env_var_used_when_no_explicit(self):
        with patch.dict(os.environ, {Constants.AGENT_REQUEST_TIMEOUT: "120"}):
            agent = _make_fast_agent()
            assert agent._request_timeout == 120

    def test_invalid_env_var_raises(self):
        with patch.dict(os.environ, {Constants.AGENT_REQUEST_TIMEOUT: "abc"}):
            with pytest.raises(ValueError, match="AGENT_REQUEST_TIMEOUT"):
                _make_fast_agent()

    def test_default_when_nothing_set(self):
        with patch.dict(os.environ, {}, clear=True):
            agent = _make_fast_agent()
            assert agent._request_timeout == Constants.DEFAULT_REQUEST_TIMEOUT


class TestInvokeTimeoutEnforcement:
    """Test that long-running invoke() calls are cancelled."""

    @pytest.mark.asyncio
    async def test_slow_invoke_returns_504(self):
        agent = _make_slow_agent(request_timeout=1)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations", content=b"{}")
            assert resp.status_code == 504
            data = resp.json()
            assert data["error"]["code"] == "request_timeout"
            assert "timed out" in data["error"]["message"].lower()
            assert "1s" in data["error"]["message"]

    @pytest.mark.asyncio
    async def test_slow_invoke_includes_invocation_id_header(self):
        agent = _make_slow_agent(request_timeout=1)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations", content=b"{}")
            assert resp.status_code == 504
            assert Constants.INVOCATION_ID_HEADER in resp.headers

    @pytest.mark.asyncio
    async def test_fast_invoke_not_affected(self):
        agent = _make_fast_agent(request_timeout=5)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations", content=b"{}")
            assert resp.status_code == 200
            assert resp.json() == {"ok": True}

    @pytest.mark.asyncio
    async def test_timeout_disabled_allows_no_limit(self):
        """request_timeout=0 means no timeout (passes None to wait_for)."""
        agent = _make_fast_agent(request_timeout=0)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations", content=b"{}")
            assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_timeout_error_is_logged(self):
        agent = _make_slow_agent(request_timeout=1)
        transport = httpx.ASGITransport(app=agent.app)
        with patch("azure.ai.agentserver.server._base.logger") as mock_logger:
            async with httpx.AsyncClient(
                transport=transport, base_url="http://testserver"
            ) as client:
                resp = await client.post("/invocations", content=b"{}")
                assert resp.status_code == 504

            timeout_calls = [
                c
                for c in mock_logger.error.call_args_list
                if "timed out" in str(c).lower()
            ]
            assert len(timeout_calls) == 1
