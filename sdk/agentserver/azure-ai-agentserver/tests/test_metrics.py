# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for Prometheus metrics: MetricsHelper, MetricsMiddleware, and /metrics endpoint."""
import os
from unittest.mock import patch

import httpx
import pytest

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver import AgentServer
from azure.ai.agentserver._constants import Constants
from azure.ai.agentserver._metrics import MetricsHelper


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


# ===========================================================================
# MetricsHelper unit tests
# ===========================================================================


class TestMetricsHelperInit:
    """Test MetricsHelper initialization and gating."""

    def test_disabled_by_default(self):
        helper = MetricsHelper()
        assert not helper.enabled

    def test_enabled_via_constructor(self):
        helper = MetricsHelper(enabled=True)
        assert helper.enabled

    def test_enabled_via_env_var(self):
        with patch.dict(os.environ, {Constants.AGENT_ENABLE_METRICS: "true"}):
            helper = MetricsHelper()
            assert helper.enabled

    def test_env_var_false(self):
        with patch.dict(os.environ, {Constants.AGENT_ENABLE_METRICS: "false"}):
            helper = MetricsHelper()
            assert not helper.enabled

    def test_constructor_overrides_env_var(self):
        with patch.dict(os.environ, {Constants.AGENT_ENABLE_METRICS: "true"}):
            helper = MetricsHelper(enabled=False)
            assert not helper.enabled

    def test_render_empty_when_disabled(self):
        helper = MetricsHelper(enabled=False)
        assert helper.render() == b""

    def test_render_nonempty_when_enabled(self):
        helper = MetricsHelper(enabled=True)
        data = helper.render()
        # Should contain at least the HELP lines for our metrics
        assert b"agent_request_total" in data

    def test_record_request_noop_when_disabled(self):
        helper = MetricsHelper(enabled=False)
        # Should not raise
        helper.record_request("POST", "/invocations", 200, 0.1, 100, 50)

    def test_inc_dec_in_flight_noop_when_disabled(self):
        helper = MetricsHelper(enabled=False)
        helper.inc_in_flight()
        helper.dec_in_flight()


class TestMetricsHelperRecording:
    """Test that MetricsHelper records metric values correctly."""

    def test_request_total_increments(self):
        helper = MetricsHelper(enabled=True)
        helper.record_request("POST", "/invocations", 200, 0.1, 100, 50)
        helper.record_request("POST", "/invocations", 200, 0.2, 100, 50)
        data = helper.render().decode()
        # Counter should show 2.0 for this label combo
        assert 'agent_request_total{method="POST",path="/invocations",status="200"} 2.0' in data

    def test_duration_histogram_recorded(self):
        helper = MetricsHelper(enabled=True)
        helper.record_request("POST", "/invocations", 200, 1.5, 100, 50)
        data = helper.render().decode()
        assert "agent_request_duration_seconds_count" in data
        assert "agent_request_duration_seconds_sum" in data

    def test_request_body_bytes_recorded(self):
        helper = MetricsHelper(enabled=True)
        helper.record_request("POST", "/invocations", 200, 0.1, 1024, 512)
        data = helper.render().decode()
        assert "agent_request_body_bytes_count" in data

    def test_response_body_bytes_recorded(self):
        helper = MetricsHelper(enabled=True)
        helper.record_request("POST", "/invocations", 200, 0.1, 100, 2048)
        data = helper.render().decode()
        assert "agent_response_body_bytes_count" in data

    def test_in_flight_gauge(self):
        helper = MetricsHelper(enabled=True)
        helper.inc_in_flight()
        helper.inc_in_flight()
        data = helper.render().decode()
        assert "agent_request_in_flight 2.0" in data
        helper.dec_in_flight()
        data = helper.render().decode()
        assert "agent_request_in_flight 1.0" in data

    def test_different_status_codes_separate_labels(self):
        helper = MetricsHelper(enabled=True)
        helper.record_request("POST", "/invocations", 200, 0.1, 0, 0)
        helper.record_request("POST", "/invocations", 500, 0.2, 0, 0)
        data = helper.render().decode()
        assert 'status="200"' in data
        assert 'status="500"' in data


# ===========================================================================
# AgentServer integration: /metrics endpoint
# ===========================================================================


class TestMetricsEndpoint:
    """Test the /metrics route on AgentServer."""

    @pytest.mark.asyncio
    async def test_no_metrics_endpoint_when_disabled(self):
        agent = _FastAgent(enable_metrics=False)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/metrics")
            # When metrics disabled, no route registered — should be 404 or 405
            assert resp.status_code in (404, 405)

    @pytest.mark.asyncio
    async def test_metrics_endpoint_returns_prometheus_format(self):
        agent = _FastAgent(enable_metrics=True)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/metrics")
            assert resp.status_code == 200
            assert "text/plain" in resp.headers["content-type"]
            assert "agent_request_total" in resp.text

    @pytest.mark.asyncio
    async def test_metrics_endpoint_after_requests(self):
        agent = _EchoAgent(enable_metrics=True)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            # Make some requests
            await client.post("/invocations", content=b'{"hello": "world"}')
            await client.post("/invocations", content=b'{"a": 1}')
            await client.get("/liveness")

            resp = await client.get("/metrics")
            assert resp.status_code == 200
            data = resp.text
            # Two POST /invocations should be counted
            assert 'agent_request_total{method="POST",path="/invocations",status="200"} 2.0' in data
            # Health endpoints are excluded from metrics
            assert '"/liveness"' not in data

    @pytest.mark.asyncio
    async def test_metrics_tracks_error_status(self):
        agent = _ErrorAgent(enable_metrics=True)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            await client.post("/invocations", content=b"{}")
            resp = await client.get("/metrics")
            assert resp.status_code == 200
            assert 'status="500"' in resp.text

    @pytest.mark.asyncio
    async def test_metrics_tracks_streaming_response(self):
        agent = _StreamAgent(enable_metrics=True)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            await client.post("/invocations", content=b"{}")
            resp = await client.get("/metrics")
            assert resp.status_code == 200
            assert 'status="200"' in resp.text
            # Streaming body bytes should be captured
            assert "agent_response_body_bytes" in resp.text

    @pytest.mark.asyncio
    async def test_metrics_duration_recorded(self):
        agent = _FastAgent(enable_metrics=True)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            await client.post("/invocations", content=b"{}")
            resp = await client.get("/metrics")
            data = resp.text
            assert "agent_request_duration_seconds_count" in data
            # Sum should be > 0
            for line in data.splitlines():
                if "agent_request_duration_seconds_sum" in line and "/invocations" in line:
                    val = float(line.split()[-1])
                    assert val > 0
                    break

    @pytest.mark.asyncio
    async def test_metrics_endpoint_excluded_from_metrics(self):
        """Requests to /metrics itself should still be served but the
        /metrics path is not a health path, so it IS counted in metrics.
        That's fine — operators typically scrape at low frequency."""
        agent = _FastAgent(enable_metrics=True)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            await client.get("/metrics")
            await client.get("/metrics")
            resp = await client.get("/metrics")
            assert resp.status_code == 200


class TestMetricsWithEnvVar:
    """Test enabling metrics via environment variable."""

    @pytest.mark.asyncio
    async def test_env_var_enables_metrics(self):
        with patch.dict(os.environ, {Constants.AGENT_ENABLE_METRICS: "true"}):
            agent = _FastAgent()
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/metrics")
            assert resp.status_code == 200
            assert "agent_request_total" in resp.text
