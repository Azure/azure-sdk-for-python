# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""End-to-end edge-case tests for AgentServer."""
import json
import uuid

import httpx
import pytest
import pytest_asyncio

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver import AgentServer


# ---------------------------------------------------------------------------
# Agent factory functions for edge cases
# ---------------------------------------------------------------------------


def _make_custom_header_agent(**kwargs) -> AgentServer:
    """Create an agent that sets its own x-agent-invocation-id header."""
    server = AgentServer(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        return JSONResponse(
            {"ok": True},
            headers={"x-agent-invocation-id": "custom-id-from-agent"},
        )

    return server


def _make_empty_streaming_agent(**kwargs) -> AgentServer:
    """Create an agent that returns an empty streaming response (0 chunks)."""
    server = AgentServer(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        async def generate():
            return
            yield  # noqa: RUF028 — makes this an async generator

        return StreamingResponse(generate(), media_type="text/event-stream")

    return server


def _make_slow_failing_get_agent(**kwargs) -> AgentServer:
    """Create an agent whose get_invocation raises so we can test debug errors on GET."""
    server = AgentServer(**kwargs)

    @server.invoke_handler
    async def invoke(request: Request) -> Response:
        return JSONResponse({"ok": True})

    @server.get_invocation_handler
    async def get_invocation(request: Request) -> Response:
        raise ValueError("get-debug-detail")

    return server


def _make_slow_failing_cancel_agent(**kwargs) -> AgentServer:
    """Create an agent whose cancel_invocation raises so we can test debug errors on cancel."""
    server = AgentServer(**kwargs)

    @server.invoke_handler
    async def invoke(request: Request) -> Response:
        return JSONResponse({"ok": True})

    @server.cancel_invocation_handler
    async def cancel_invocation(request: Request) -> Response:
        raise ValueError("cancel-debug-detail")

    return server


def _make_large_payload_agent(**kwargs) -> AgentServer:
    """Create an agent that echoes the request body length as JSON."""
    server = AgentServer(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        body = await request.body()
        return JSONResponse({"length": len(body)})

    return server


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def custom_header_client():
    server = _make_custom_header_agent()
    transport = httpx.ASGITransport(app=server.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def empty_streaming_client():
    server = _make_empty_streaming_agent()
    transport = httpx.ASGITransport(app=server.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def large_payload_client():
    server = _make_large_payload_agent()
    transport = httpx.ASGITransport(app=server.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


# ---------------------------------------------------------------------------
# Tests: wrong HTTP methods
# ---------------------------------------------------------------------------


class TestMethodNotAllowed:
    """Verify that wrong HTTP methods return 405."""

    @pytest.mark.asyncio
    async def test_get_on_invocations_returns_405(self, echo_client):
        """GET /invocations is not allowed (POST only)."""
        resp = await echo_client.get("/invocations")
        assert resp.status_code == 405

    @pytest.mark.asyncio
    async def test_post_on_liveness_returns_405(self, echo_client):
        """POST /liveness is not allowed (GET only)."""
        resp = await echo_client.post("/liveness")
        assert resp.status_code == 405

    @pytest.mark.asyncio
    async def test_post_on_readiness_returns_405(self, echo_client):
        """POST /readiness is not allowed (GET only)."""
        resp = await echo_client.post("/readiness")
        assert resp.status_code == 405

    @pytest.mark.asyncio
    async def test_put_on_invocations_returns_405(self, echo_client):
        """PUT /invocations is not allowed."""
        resp = await echo_client.put("/invocations", content=b"{}")
        assert resp.status_code == 405

    @pytest.mark.asyncio
    async def test_delete_on_invocations_id_returns_405(self, echo_client):
        """DELETE /invocations/{id} is not allowed."""
        resp = await echo_client.delete(f"/invocations/{uuid.uuid4()}")
        assert resp.status_code == 405

    @pytest.mark.asyncio
    async def test_post_on_openapi_spec_returns_405(self, echo_client):
        """POST /invocations/docs/openapi.json is not allowed (GET only)."""
        resp = await echo_client.post("/invocations/docs/openapi.json", content=b"{}")
        assert resp.status_code == 405


# ---------------------------------------------------------------------------
# Tests: OpenAPI validation edge cases
# ---------------------------------------------------------------------------


class TestOpenAPIValidation:
    """End-to-end OpenAPI validation via HTTP."""

    @pytest.mark.asyncio
    async def test_valid_request_returns_200(self, validated_client):
        """POST with valid body passes validation and returns greeting."""
        resp = await validated_client.post(
            "/invocations",
            content=json.dumps({"name": "Alice"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200
        assert resp.json()["greeting"] == "Hello, Alice!"

    @pytest.mark.asyncio
    async def test_missing_required_field_returns_400(self, validated_client):
        """POST missing required 'name' field returns 400 with validation details."""
        resp = await validated_client.post(
            "/invocations",
            content=json.dumps({"wrong_field": "foo"}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400
        body = resp.json()
        assert body["error"]["code"] == "invalid_payload"
        assert "details" in body["error"]

    @pytest.mark.asyncio
    async def test_malformed_json_returns_400(self, validated_client):
        """POST with non-JSON body when spec expects JSON returns 400."""
        resp = await validated_client.post(
            "/invocations",
            content=b"this is not json",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 400
        assert resp.json()["error"]["code"] == "invalid_payload"

    @pytest.mark.asyncio
    async def test_extra_field_accepted(self, validated_client):
        """Extra fields are accepted when additionalProperties is not false."""
        resp = await validated_client.post(
            "/invocations",
            content=json.dumps({"name": "Bob", "bonus": 42}).encode(),
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 200
        assert resp.json()["greeting"] == "Hello, Bob!"

    @pytest.mark.asyncio
    async def test_no_spec_skips_validation(self, no_spec_client):
        """Agent with no OpenAPI spec accepts any payload without validation."""
        resp = await no_spec_client.post(
            "/invocations",
            content=b"arbitrary bytes not json at all!",
        )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Tests: response header behaviour
# ---------------------------------------------------------------------------


class TestResponseHeaders:
    """Verify invocation-id header auto-injection and passthrough."""

    @pytest.mark.asyncio
    async def test_agent_custom_invocation_id_not_overwritten(self, custom_header_client):
        """If agent sets x-agent-invocation-id, the server doesn't overwrite it."""
        resp = await custom_header_client.post("/invocations", content=b"{}")
        assert resp.status_code == 200
        assert resp.headers["x-agent-invocation-id"] == "custom-id-from-agent"

    @pytest.mark.asyncio
    async def test_invocation_id_injected_when_missing(self, echo_client):
        """EchoAgent doesn't set the header; server auto-injects it."""
        resp = await echo_client.post("/invocations", content=b"hello")
        assert resp.status_code == 200
        invocation_id = resp.headers.get("x-agent-invocation-id")
        assert invocation_id is not None
        uuid.UUID(invocation_id)  # valid UUID


# ---------------------------------------------------------------------------
# Tests: payload edge cases
# ---------------------------------------------------------------------------


class TestPayloadEdgeCases:
    """Body content edge cases."""

    @pytest.mark.asyncio
    async def test_large_payload(self, large_payload_client):
        """Server handles a 1 MB payload correctly."""
        big = b"A" * (1024 * 1024)
        resp = await large_payload_client.post("/invocations", content=big)
        assert resp.status_code == 200
        assert resp.json()["length"] == 1024 * 1024

    @pytest.mark.asyncio
    async def test_unicode_body(self, echo_client):
        """Unicode characters round-trip correctly."""
        data = "\u3053\u3093\u306b\u3061\u306f\u4e16\u754c \U0001f30d \u0645\u0631\u062d\u0628\u0627"
        resp = await echo_client.post("/invocations", content=data.encode("utf-8"))
        assert resp.status_code == 200
        assert resp.content.decode("utf-8") == data

    @pytest.mark.asyncio
    async def test_binary_body(self, echo_client):
        """Binary (non-UTF-8) bytes round-trip correctly."""
        data = bytes(range(256))
        resp = await echo_client.post("/invocations", content=data)
        assert resp.status_code == 200
        assert resp.content == data


# ---------------------------------------------------------------------------
# Tests: streaming edge cases
# ---------------------------------------------------------------------------


class TestStreamingEdgeCases:
    """Streaming response edge cases."""

    @pytest.mark.asyncio
    async def test_empty_streaming_response(self, empty_streaming_client):
        """Empty streaming response returns 200 with no body."""
        resp = await empty_streaming_client.post("/invocations", content=b"{}")
        assert resp.status_code == 200
        assert resp.content == b""

    @pytest.mark.asyncio
    async def test_streaming_response_has_invocation_id(self, streaming_client):
        """Streaming response still gets the auto-injected invocation-id header."""
        resp = await streaming_client.post("/invocations", content=b"{}")
        assert resp.status_code == 200
        invocation_id = resp.headers.get("x-agent-invocation-id")
        assert invocation_id is not None
        uuid.UUID(invocation_id)  # valid UUID


# ---------------------------------------------------------------------------
# Tests: invocation lifecycle (storage agent)
# ---------------------------------------------------------------------------


class TestInvocationLifecycle:
    """Multi-step invocation workflows."""

    @pytest.mark.asyncio
    async def test_multiple_gets_on_same_invocation(self, async_storage_client):
        """GET /invocations/{id} returns the same data on repeated calls."""
        post_resp = await async_storage_client.post("/invocations", content=b'{"data":"hello"}')
        invocation_id = post_resp.headers["x-agent-invocation-id"]

        get1 = await async_storage_client.get(f"/invocations/{invocation_id}")
        get2 = await async_storage_client.get(f"/invocations/{invocation_id}")
        assert get1.status_code == 200
        assert get2.status_code == 200
        assert get1.content == get2.content

    @pytest.mark.asyncio
    async def test_double_cancel_returns_404_second_time(self, async_storage_client):
        """Cancelling the same invocation twice: first succeeds, second 404."""
        post_resp = await async_storage_client.post("/invocations", content=b'{"data":"x"}')
        invocation_id = post_resp.headers["x-agent-invocation-id"]

        cancel1 = await async_storage_client.post(f"/invocations/{invocation_id}/cancel")
        assert cancel1.status_code == 200

        cancel2 = await async_storage_client.post(f"/invocations/{invocation_id}/cancel")
        assert cancel2.status_code == 404

    @pytest.mark.asyncio
    async def test_invoke_then_cancel_then_get_returns_404(self, async_storage_client):
        """Full lifecycle: invoke → cancel → get returns 404."""
        post_resp = await async_storage_client.post("/invocations", content=b'{"val":1}')
        invocation_id = post_resp.headers["x-agent-invocation-id"]

        await async_storage_client.post(f"/invocations/{invocation_id}/cancel")

        get_resp = await async_storage_client.get(f"/invocations/{invocation_id}")
        assert get_resp.status_code == 404


# ---------------------------------------------------------------------------
# Tests: debug errors on get/cancel endpoints
# ---------------------------------------------------------------------------


class TestDebugErrorsOnGetCancel:
    """AGENT_DEBUG_ERRORS exposes details on GET and CANCEL error responses too."""

    @pytest.mark.asyncio
    async def test_get_hides_details_by_default(self):
        """GET error hides exception detail without AGENT_DEBUG_ERRORS."""
        agent = _make_slow_failing_get_agent()
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/invocations/some-id")
        assert resp.status_code == 500
        assert resp.json()["error"]["message"] == "Internal server error"

    @pytest.mark.asyncio
    async def test_get_exposes_details_with_debug(self, monkeypatch):
        """GET error exposes exception detail with AGENT_DEBUG_ERRORS set."""
        monkeypatch.setenv("AGENT_DEBUG_ERRORS", "true")
        agent = _make_slow_failing_get_agent()
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/invocations/some-id")
        assert resp.status_code == 500
        assert resp.json()["error"]["message"] == "get-debug-detail"

    @pytest.mark.asyncio
    async def test_cancel_hides_details_by_default(self):
        """CANCEL error hides exception detail without AGENT_DEBUG_ERRORS."""
        agent = _make_slow_failing_cancel_agent()
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations/some-id/cancel")
        assert resp.status_code == 500
        assert resp.json()["error"]["message"] == "Internal server error"

    @pytest.mark.asyncio
    async def test_cancel_exposes_details_with_debug(self, monkeypatch):
        """CANCEL error exposes exception detail with AGENT_DEBUG_ERRORS set."""
        monkeypatch.setenv("AGENT_DEBUG_ERRORS", "true")
        agent = _make_slow_failing_cancel_agent()
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations/some-id/cancel")
        assert resp.status_code == 500
        assert resp.json()["error"]["message"] == "cancel-debug-detail"

    @pytest.mark.asyncio
    async def test_get_exposes_details_with_constructor_param(self):
        """debug_errors=True in constructor exposes GET exception detail."""
        agent = _make_slow_failing_get_agent(debug_errors=True)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/invocations/some-id")
        assert resp.status_code == 500
        assert resp.json()["error"]["message"] == "get-debug-detail"

    @pytest.mark.asyncio
    async def test_cancel_exposes_details_with_constructor_param(self):
        """debug_errors=True in constructor exposes CANCEL exception detail."""
        agent = _make_slow_failing_cancel_agent(debug_errors=True)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations/some-id/cancel")
        assert resp.status_code == 500
        assert resp.json()["error"]["message"] == "cancel-debug-detail"

    @pytest.mark.asyncio
    async def test_constructor_overrides_env_var(self, monkeypatch):
        """debug_errors=False in constructor overrides AGENT_DEBUG_ERRORS=true."""
        monkeypatch.setenv("AGENT_DEBUG_ERRORS", "true")
        agent = _make_slow_failing_get_agent(debug_errors=False)
        transport = httpx.ASGITransport(app=agent.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/invocations/some-id")
        assert resp.status_code == 500
        assert resp.json()["error"]["message"] == "Internal server error"


# ---------------------------------------------------------------------------
# Tests: log_level constructor parameter
# ---------------------------------------------------------------------------


class TestLogLevel:
    """log_level parameter controls the library logger level."""

    def test_log_level_via_constructor(self):
        """log_level='DEBUG' sets library logger to DEBUG."""
        import logging
        agent = _make_custom_header_agent(log_level="DEBUG")
        lib_logger = logging.getLogger("azure.ai.agentserver")
        assert lib_logger.level == logging.DEBUG

    def test_log_level_via_env_var(self, monkeypatch):
        """AGENT_LOG_LEVEL=info sets library logger to INFO."""
        import logging
        monkeypatch.setenv("AGENT_LOG_LEVEL", "info")
        agent = _make_custom_header_agent()
        lib_logger = logging.getLogger("azure.ai.agentserver")
        assert lib_logger.level == logging.INFO

    def test_log_level_constructor_overrides_env_var(self, monkeypatch):
        """Constructor log_level overrides AGENT_LOG_LEVEL env var."""
        import logging
        monkeypatch.setenv("AGENT_LOG_LEVEL", "DEBUG")
        agent = _make_custom_header_agent(log_level="ERROR")
        lib_logger = logging.getLogger("azure.ai.agentserver")
        assert lib_logger.level == logging.ERROR

    def test_invalid_log_level_raises(self):
        """Invalid log_level raises ValueError."""
        with pytest.raises(ValueError, match="Invalid log level"):
            _make_custom_header_agent(log_level="BOGUS")


class TestConcurrency:
    """Verify multiple concurrent requests produce unique invocation IDs."""

    @pytest.mark.asyncio
    async def test_concurrent_invocations_unique_ids(self, echo_client):
        """10 concurrent POSTs each get a unique invocation ID."""
        import asyncio

        async def do_post():
            return await echo_client.post("/invocations", content=b"concurrent")

        responses = await asyncio.gather(*[do_post() for _ in range(10)])
        ids = {r.headers["x-agent-invocation-id"] for r in responses}
        assert len(ids) == 10  # all unique
