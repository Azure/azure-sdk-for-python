# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the decorator-based handler registration pattern."""
from __future__ import annotations

import httpx
import pytest
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from azure.ai.agentserver import AgentServer


# ---------------------------------------------------------------------------
# Decorator registration
# ---------------------------------------------------------------------------


class TestDecoratorRegistration:
    """Verify that decorators store the function and return it unchanged."""

    def test_invoke_handler_stores_function(self):
        server = AgentServer()

        @server.invoke_handler
        async def handle(request: Request) -> Response:
            return JSONResponse({"ok": True})

        assert server._invoke_fn is handle

    def test_invoke_handler_returns_original_function(self):
        server = AgentServer()
        original = None

        async def handle(request: Request) -> Response:
            return JSONResponse({"ok": True})

        original = handle
        result = server.invoke_handler(handle)
        assert result is original

    def test_get_invocation_handler_stores_function(self):
        server = AgentServer()

        @server.get_invocation_handler
        async def handle(request: Request) -> Response:
            return JSONResponse({"found": True})

        assert server._get_invocation_fn is handle

    def test_cancel_invocation_handler_stores_function(self):
        server = AgentServer()

        @server.cancel_invocation_handler
        async def handle(request: Request) -> Response:
            return JSONResponse({"cancelled": True})

        assert server._cancel_invocation_fn is handle

    def test_shutdown_handler_stores_function(self):
        server = AgentServer()

        @server.shutdown_handler
        async def handle():
            pass

        assert server._shutdown_fn is handle


# ---------------------------------------------------------------------------
# Invoke handler — full request flow
# ---------------------------------------------------------------------------


class TestInvokeHandlerFlow:
    """Verify that POST /invocations delegates to @invoke_handler."""

    @pytest.mark.asyncio
    async def test_invoke_returns_handler_response(self):
        server = AgentServer()

        @server.invoke_handler
        async def handle(request: Request) -> Response:
            data = await request.json()
            return JSONResponse({"echo": data["msg"]})

        transport = httpx.ASGITransport(app=server.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations", json={"msg": "hello"})
            assert resp.status_code == 200
            assert resp.json()["echo"] == "hello"

    @pytest.mark.asyncio
    async def test_invoke_includes_invocation_id_header(self):
        server = AgentServer()

        @server.invoke_handler
        async def handle(request: Request) -> Response:
            return JSONResponse({"ok": True})

        transport = httpx.ASGITransport(app=server.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations", json={})
            assert "x-agent-invocation-id" in resp.headers

    @pytest.mark.asyncio
    async def test_invoke_request_has_invocation_id_in_state(self):
        """The handler receives request.state.invocation_id."""
        server = AgentServer()
        captured_id = None

        @server.invoke_handler
        async def handle(request: Request) -> Response:
            nonlocal captured_id
            captured_id = request.state.invocation_id
            return JSONResponse({"id": captured_id})

        transport = httpx.ASGITransport(app=server.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations", json={})
            assert resp.status_code == 200
            assert captured_id is not None
            assert resp.json()["id"] == captured_id


# ---------------------------------------------------------------------------
# Missing invoke handler
# ---------------------------------------------------------------------------


class TestMissingInvokeHandler:
    """When no invoke handler is registered and invoke() is not overridden, 500."""

    @pytest.mark.asyncio
    async def test_no_handler_returns_500(self):
        server = AgentServer()
        # No @invoke_handler registered
        transport = httpx.ASGITransport(app=server.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations", json={})
            assert resp.status_code == 500


# ---------------------------------------------------------------------------
# Optional handler defaults
# ---------------------------------------------------------------------------


class TestOptionalHandlerDefaults:
    """get_invocation and cancel_invocation return 404 by default."""

    @pytest.mark.asyncio
    async def test_get_invocation_returns_404_by_default(self):
        server = AgentServer()

        @server.invoke_handler
        async def handle(request: Request) -> Response:
            return JSONResponse({"ok": True})

        transport = httpx.ASGITransport(app=server.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/invocations/some-id")
            assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_cancel_invocation_returns_404_by_default(self):
        server = AgentServer()

        @server.invoke_handler
        async def handle(request: Request) -> Response:
            return JSONResponse({"ok": True})

        transport = httpx.ASGITransport(app=server.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations/some-id/cancel")
            assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Optional handler overrides via decorator
# ---------------------------------------------------------------------------


class TestOptionalHandlerOverrides:
    """Registered optional handlers are called instead of the defaults."""

    @pytest.mark.asyncio
    async def test_get_invocation_handler_called(self):
        server = AgentServer()

        @server.invoke_handler
        async def invoke(request: Request) -> Response:
            return JSONResponse({"ok": True})

        @server.get_invocation_handler
        async def get_inv(request: Request) -> Response:
            inv_id = request.state.invocation_id
            return JSONResponse({"id": inv_id, "status": "completed"})

        transport = httpx.ASGITransport(app=server.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/invocations/test-123")
            assert resp.status_code == 200
            assert resp.json()["id"] == "test-123"
            assert resp.json()["status"] == "completed"

    @pytest.mark.asyncio
    async def test_cancel_invocation_handler_called(self):
        server = AgentServer()

        @server.invoke_handler
        async def invoke(request: Request) -> Response:
            return JSONResponse({"ok": True})

        @server.cancel_invocation_handler
        async def cancel(request: Request) -> Response:
            inv_id = request.state.invocation_id
            return JSONResponse({"id": inv_id, "cancelled": True})

        transport = httpx.ASGITransport(app=server.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.post("/invocations/test-456/cancel")
            assert resp.status_code == 200
            assert resp.json()["cancelled"] is True


# ---------------------------------------------------------------------------
# Shutdown handler via decorator
# ---------------------------------------------------------------------------


class TestShutdownHandler:
    """@shutdown_handler is called during lifespan teardown."""

    @pytest.mark.asyncio
    async def test_shutdown_handler_called(self):
        server = AgentServer()
        shutdown_called = False

        @server.invoke_handler
        async def invoke(request: Request) -> Response:
            return JSONResponse({"ok": True})

        @server.shutdown_handler
        async def cleanup():
            nonlocal shutdown_called
            shutdown_called = True

        # Exercise the lifespan directly
        lifespan = server.app.router.lifespan_context
        async with lifespan(server.app):
            pass  # startup; on exit → shutdown

        assert shutdown_called is True

    @pytest.mark.asyncio
    async def test_no_shutdown_handler_is_noop(self):
        """Without @shutdown_handler, on_shutdown is a silent no-op."""
        server = AgentServer()

        @server.invoke_handler
        async def invoke(request: Request) -> Response:
            return JSONResponse({"ok": True})

        # Should not raise
        lifespan = server.app.router.lifespan_context
        async with lifespan(server.app):
            pass


# ---------------------------------------------------------------------------
# Config passthrough
# ---------------------------------------------------------------------------


class TestConfigPassthrough:
    """All AgentServer kwargs still work in decorator mode."""

    def test_request_timeout_resolved(self):
        server = AgentServer(request_timeout=42)

        @server.invoke_handler
        async def handle(request: Request) -> Response:
            return JSONResponse({"ok": True})

        assert server._request_timeout == 42

    def test_graceful_shutdown_timeout_resolved(self):
        server = AgentServer(graceful_shutdown_timeout=10)

        @server.invoke_handler
        async def handle(request: Request) -> Response:
            return JSONResponse({"ok": True})

        assert server._graceful_shutdown_timeout == 10

    def test_debug_errors_resolved(self):
        server = AgentServer(debug_errors=True)
        assert server._debug_errors is True


# ---------------------------------------------------------------------------
# Health endpoints work in decorator mode
# ---------------------------------------------------------------------------


class TestHealthEndpointsDecoratorMode:
    """Health endpoints respond even when using the decorator pattern."""

    @pytest.mark.asyncio
    async def test_liveness(self):
        server = AgentServer()

        @server.invoke_handler
        async def handle(request: Request) -> Response:
            return JSONResponse({"ok": True})

        transport = httpx.ASGITransport(app=server.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/liveness")
            assert resp.status_code == 200
            assert resp.json()["status"] == "alive"

    @pytest.mark.asyncio
    async def test_readiness(self):
        server = AgentServer()

        @server.invoke_handler
        async def handle(request: Request) -> Response:
            return JSONResponse({"ok": True})

        transport = httpx.ASGITransport(app=server.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.get("/readiness")
            assert resp.status_code == 200
            assert resp.json()["status"] == "ready"
