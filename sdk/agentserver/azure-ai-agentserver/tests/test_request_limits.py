# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for request body size limits and invoke timeout guards."""
import asyncio
import os
from unittest.mock import patch

import httpx
import pytest
import pytest_asyncio

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver import AgentServer
from azure.ai.agentserver._constants import Constants


# ---------------------------------------------------------------------------
# Test agents
# ---------------------------------------------------------------------------


class _EchoAgent(AgentServer):
    """Echoes the body back — used to test body size limits."""

    async def invoke(self, request: Request) -> Response:
        body = await request.body()
        return Response(content=body, media_type="application/octet-stream")


class _SlowAgent(AgentServer):
    """Sleeps for a long time — used to test invoke timeout."""

    async def invoke(self, request: Request) -> Response:
        await asyncio.sleep(999)
        return Response(content=b"done")


class _FastAgent(AgentServer):
    """Returns immediately — used to verify no false timeout."""

    async def invoke(self, request: Request) -> Response:
        return JSONResponse({"ok": True})


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def small_limit_client():
    """Client with 1 KB body limit."""
    agent = _EchoAgent(max_request_body_size=1024)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def no_limit_client():
    """Client with body limit disabled (0)."""
    agent = _EchoAgent(max_request_body_size=0)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def default_client():
    """Client with default body limit (100 MB)."""
    agent = _EchoAgent()
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


# ===========================================================================
# Max request body size
# ===========================================================================


class TestMaxRequestBodySizeConstants:
    """Verify constants are wired correctly."""

    def test_default_is_100mb(self):
        assert Constants.DEFAULT_MAX_REQUEST_BODY_SIZE == 100 * 1024 * 1024

    def test_env_var_name(self):
        assert Constants.AGENT_MAX_REQUEST_BODY_SIZE == "AGENT_MAX_REQUEST_BODY_SIZE"


class TestMaxRequestBodySizeResolution:
    """Test the resolution hierarchy: explicit > env > default."""

    def test_explicit_value(self):
        agent = _EchoAgent(max_request_body_size=5000)
        assert agent._max_request_body_size == 5000

    def test_explicit_zero_disables(self):
        agent = _EchoAgent(max_request_body_size=0)
        assert agent._max_request_body_size == 0

    def test_env_var_used_when_no_explicit(self):
        with patch.dict(os.environ, {Constants.AGENT_MAX_REQUEST_BODY_SIZE: "2048"}):
            agent = _EchoAgent()
            assert agent._max_request_body_size == 2048

    def test_invalid_env_var_raises(self):
        with patch.dict(os.environ, {Constants.AGENT_MAX_REQUEST_BODY_SIZE: "abc"}):
            with pytest.raises(ValueError, match="AGENT_MAX_REQUEST_BODY_SIZE"):
                _EchoAgent()

    def test_default_when_nothing_set(self):
        with patch.dict(os.environ, {}, clear=True):
            agent = _EchoAgent()
            assert agent._max_request_body_size == Constants.DEFAULT_MAX_REQUEST_BODY_SIZE


class TestMaxRequestBodySizeEnforcement:
    """Test that oversized requests are rejected with 413."""

    @pytest.mark.asyncio
    async def test_request_within_limit_succeeds(self, small_limit_client):
        body = b"x" * 512  # 512 bytes < 1024 limit
        resp = await small_limit_client.post("/invocations", content=body)
        assert resp.status_code == 200
        assert resp.content == body

    @pytest.mark.asyncio
    async def test_request_at_exact_limit_succeeds(self, small_limit_client):
        body = b"x" * 1024  # exactly 1024 bytes
        resp = await small_limit_client.post("/invocations", content=body)
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_request_over_limit_returns_413(self, small_limit_client):
        body = b"x" * 2048  # 2 KB > 1 KB limit
        resp = await small_limit_client.post("/invocations", content=body)
        assert resp.status_code == 413
        data = resp.json()
        assert data["error"]["code"] == "payload_too_large"
        assert data["error"]["code"] == "payload_too_large"

    @pytest.mark.asyncio
    async def test_limit_disabled_allows_large_body(self, no_limit_client):
        body = b"x" * 1024 * 1024  # 1 MB with no limit
        resp = await no_limit_client.post("/invocations", content=body)
        assert resp.status_code == 200
        assert resp.content == body

    @pytest.mark.asyncio
    async def test_get_endpoints_not_affected(self, small_limit_client):
        """GET endpoints (liveness, readiness) should not be affected by body limits."""
        resp = await small_limit_client.get("/liveness")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_content_length_header_fast_reject(self):
        """If Content-Length exceeds the limit, reject before reading body."""
        agent = _EchoAgent(max_request_body_size=100)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post(
                "/invocations",
                content=b"x" * 200,
                headers={"Content-Length": "200"},
            )
            assert resp.status_code == 413

    @pytest.mark.asyncio
    async def test_chunked_transfer_passes_through(self):
        """Requests without Content-Length (e.g. chunked/streamed) pass through.

        Streaming data arrives in small frames and is processed incrementally,
        so memory is naturally bounded per chunk.  Infrastructure-level limits
        (gateways, Hypercorn max_content_length) guard those cases.
        """
        agent = _EchoAgent(max_request_body_size=100)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Streaming upload omits Content-Length
            async def _stream():
                yield b"x" * 200  # larger than the 100-byte limit

            resp = await client.post("/invocations", content=_stream())
            # Passes through — middleware only checks Content-Length
            assert resp.status_code == 200
            assert len(resp.content) == 200


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
        agent = _FastAgent(request_timeout=60)
        assert agent._request_timeout == 60

    def test_explicit_zero_disables(self):
        agent = _FastAgent(request_timeout=0)
        assert agent._request_timeout == 0

    def test_env_var_used_when_no_explicit(self):
        with patch.dict(os.environ, {Constants.AGENT_REQUEST_TIMEOUT: "120"}):
            agent = _FastAgent()
            assert agent._request_timeout == 120

    def test_invalid_env_var_raises(self):
        with patch.dict(os.environ, {Constants.AGENT_REQUEST_TIMEOUT: "abc"}):
            with pytest.raises(ValueError, match="AGENT_REQUEST_TIMEOUT"):
                _FastAgent()

    def test_default_when_nothing_set(self):
        with patch.dict(os.environ, {}, clear=True):
            agent = _FastAgent()
            assert agent._request_timeout == Constants.DEFAULT_REQUEST_TIMEOUT


class TestInvokeTimeoutEnforcement:
    """Test that long-running invoke() calls are cancelled."""

    @pytest.mark.asyncio
    async def test_slow_invoke_returns_504(self):
        agent = _SlowAgent(request_timeout=1)
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
        agent = _SlowAgent(request_timeout=1)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations", content=b"{}")
            assert resp.status_code == 504
            assert Constants.INVOCATION_ID_HEADER in resp.headers

    @pytest.mark.asyncio
    async def test_fast_invoke_not_affected(self):
        agent = _FastAgent(request_timeout=5)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations", content=b"{}")
            assert resp.status_code == 200
            assert resp.json() == {"ok": True}

    @pytest.mark.asyncio
    async def test_timeout_disabled_allows_no_limit(self):
        """request_timeout=0 means no timeout (passes None to wait_for)."""
        agent = _FastAgent(request_timeout=0)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations", content=b"{}")
            assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_timeout_error_is_logged(self):
        agent = _SlowAgent(request_timeout=1)
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


# ===========================================================================
# Max concurrent requests
# ===========================================================================


class _DelayAgent(AgentServer):
    """Holds requests for a controllable duration — used to test concurrency limits."""

    def __init__(self, delay: float = 1.0, **kwargs):  # type: ignore[no-untyped-def]
        self._delay = delay
        super().__init__(**kwargs)

    async def invoke(self, request: Request) -> Response:
        await asyncio.sleep(self._delay)
        return JSONResponse({"ok": True})


class TestMaxConcurrentRequestsConstants:
    """Verify constants are wired correctly."""

    def test_default_is_zero_disabled(self):
        assert Constants.DEFAULT_MAX_CONCURRENT_REQUESTS == 0

    def test_env_var_name(self):
        assert Constants.AGENT_MAX_CONCURRENT_REQUESTS == "AGENT_MAX_CONCURRENT_REQUESTS"


class TestMaxConcurrentRequestsResolution:
    """Test the resolution hierarchy: explicit > env > default (0 = disabled)."""

    def test_explicit_value(self):
        agent = _FastAgent(max_concurrent_requests=5)
        assert agent._max_concurrent_requests == 5

    def test_explicit_zero_disables(self):
        agent = _FastAgent(max_concurrent_requests=0)
        assert agent._max_concurrent_requests == 0

    def test_env_var_used_when_no_explicit(self):
        with patch.dict(os.environ, {Constants.AGENT_MAX_CONCURRENT_REQUESTS: "10"}):
            agent = _FastAgent()
            assert agent._max_concurrent_requests == 10

    def test_invalid_env_var_raises(self):
        with patch.dict(os.environ, {Constants.AGENT_MAX_CONCURRENT_REQUESTS: "abc"}):
            with pytest.raises(ValueError, match="AGENT_MAX_CONCURRENT_REQUESTS"):
                _FastAgent()

    def test_default_when_nothing_set(self):
        with patch.dict(os.environ, {}, clear=True):
            agent = _FastAgent()
            assert agent._max_concurrent_requests == 0


class TestMaxConcurrentRequestsEnforcement:
    """Test that excess concurrent requests are rejected with 503."""

    @pytest.mark.asyncio
    async def test_excess_requests_get_503(self):
        """When concurrency limit is 1 and a request is in-flight, the next gets 503."""
        agent = _DelayAgent(delay=2.0, max_concurrent_requests=1)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Fire first request (will occupy the slot for 2s)
            task1 = asyncio.create_task(client.post("/invocations", content=b"{}"))
            await asyncio.sleep(0.1)  # let it start
            # Second request should be rejected
            resp2 = await client.post("/invocations", content=b"{}")
            assert resp2.status_code == 503
            data = resp2.json()
            assert data["error"]["code"] == "server_overloaded"
            # First request should still succeed
            resp1 = await task1
            assert resp1.status_code == 200

    @pytest.mark.asyncio
    async def test_within_limit_succeeds(self):
        """Two concurrent requests within a limit of 2 should both succeed."""
        agent = _DelayAgent(delay=0.2, max_concurrent_requests=2)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            results = await asyncio.gather(
                client.post("/invocations", content=b"{}"),
                client.post("/invocations", content=b"{}"),
            )
            assert all(r.status_code == 200 for r in results)

    @pytest.mark.asyncio
    async def test_disabled_allows_unlimited(self):
        """max_concurrent_requests=0 means no middleware — all requests pass."""
        agent = _DelayAgent(delay=0.1, max_concurrent_requests=0)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            results = await asyncio.gather(
                *[client.post("/invocations", content=b"{}") for _ in range(5)]
            )
            assert all(r.status_code == 200 for r in results)

    @pytest.mark.asyncio
    async def test_503_response_body_structure(self):
        """Verify the 503 response contains the expected error detail."""
        agent = _DelayAgent(delay=2.0, max_concurrent_requests=1)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Occupy the slot
            task1 = asyncio.create_task(client.post("/invocations", content=b"{}"))
            await asyncio.sleep(0.1)
            # Verify the 503 response body structure.
            resp = await client.post("/invocations", content=b"{}")
            assert resp.status_code == 503
            assert resp.json()["error"]["code"] == "server_overloaded"
            resp1 = await task1
            assert resp1.status_code == 200

    @pytest.mark.asyncio
    async def test_slot_freed_after_completion(self):
        """After a request completes, the slot is freed for the next request."""
        agent = _DelayAgent(delay=0.1, max_concurrent_requests=1)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            # First request — completes
            resp1 = await client.post("/invocations", content=b"{}")
            assert resp1.status_code == 200
            # Second request — slot freed, should succeed
            resp2 = await client.post("/invocations", content=b"{}")
            assert resp2.status_code == 200

    @pytest.mark.asyncio
    async def test_health_probes_bypass_concurrency_limit(self):
        """Health endpoints must respond even when all request slots are occupied."""
        agent = _DelayAgent(delay=2.0, max_concurrent_requests=1)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Occupy the single slot
            task1 = asyncio.create_task(client.post("/invocations", content=b"{}"))
            await asyncio.sleep(0.1)
            # Health probes should still succeed
            liveness = await client.get("/liveness")
            assert liveness.status_code == 200
            readiness = await client.get("/readiness")
            assert readiness.status_code == 200
            resp1 = await task1
            assert resp1.status_code == 200

    @pytest.mark.asyncio
    async def test_health_probes_bypass_body_size_limit(self):
        """Health endpoints are not affected by the body size middleware."""
        agent = _EchoAgent(max_request_body_size=1)  # 1 byte limit
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            liveness = await client.get("/liveness")
            assert liveness.status_code == 200
            readiness = await client.get("/readiness")
            assert readiness.status_code == 200
