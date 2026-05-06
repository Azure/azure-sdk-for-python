# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for decorator-based handler registration on InvocationWSAgentServerHost."""
from starlette.testclient import TestClient

from azure.ai.agentserver.invocations import (
    InvocationWSAgentServerHost,
    InvocationWSContext,
    InvocationWSError,
)


# ---------------------------------------------------------------------------
# ws_invoke_handler stores function
# ---------------------------------------------------------------------------

def test_ws_invoke_handler_stores_function():
    """@app.ws_invoke_handler stores the function on the protocol object."""
    app = InvocationWSAgentServerHost()

    @app.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext) -> dict:
        return {"ok": True}

    assert app._ws_invoke_fn is handle


# ---------------------------------------------------------------------------
# ws_invoke_handler returns original function
# ---------------------------------------------------------------------------

def test_ws_invoke_handler_returns_original_function():
    """@app.ws_invoke_handler returns the original function."""
    app = InvocationWSAgentServerHost()

    async def handle(payload: dict, context: InvocationWSContext) -> dict:
        return {"ok": True}

    result = app.ws_invoke_handler(handle)
    assert result is handle


# ---------------------------------------------------------------------------
# ws_get_invocation_handler stores function
# ---------------------------------------------------------------------------

def test_ws_get_invocation_handler_stores_function():
    """@app.ws_get_invocation_handler stores the function."""
    app = InvocationWSAgentServerHost()

    @app.ws_get_invocation_handler
    async def get_handler(context: InvocationWSContext) -> dict:
        return {"ok": True}

    assert app._ws_get_invocation_fn is get_handler


# ---------------------------------------------------------------------------
# ws_cancel_invocation_handler stores function
# ---------------------------------------------------------------------------

def test_ws_cancel_invocation_handler_stores_function():
    """@app.ws_cancel_invocation_handler stores the function."""
    app = InvocationWSAgentServerHost()

    @app.ws_cancel_invocation_handler
    async def cancel_handler(context: InvocationWSContext) -> dict:
        return {"ok": True}

    assert app._ws_cancel_invocation_fn is cancel_handler


# ---------------------------------------------------------------------------
# shutdown_handler stores function
# ---------------------------------------------------------------------------

def test_ws_shutdown_handler_stores_function():
    """@server.shutdown_handler stores the function on the server."""
    app = InvocationWSAgentServerHost()

    @app.shutdown_handler
    async def on_shutdown():
        pass

    assert app._shutdown_fn is on_shutdown


# ---------------------------------------------------------------------------
# Full request flow
# ---------------------------------------------------------------------------

def test_ws_full_request_flow():
    """Full lifecycle: invoke → get → cancel → get (not_found)."""
    app = InvocationWSAgentServerHost()
    store: dict[str, dict] = {}

    @app.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext) -> dict:
        store[context.invocation_id] = payload
        return {"stored": True}

    @app.ws_get_invocation_handler
    async def get_handler(context: InvocationWSContext) -> dict:
        if context.invocation_id not in store:
            raise InvocationWSError("not_found", "Not found")
        return {"data": store[context.invocation_id]}

    @app.ws_cancel_invocation_handler
    async def cancel_handler(context: InvocationWSContext) -> dict:
        if context.invocation_id not in store:
            raise InvocationWSError("not_found", "Not found")
        del store[context.invocation_id]
        return {"status": "cancelled"}

    client = TestClient(app)
    with client.websocket_connect("/invocations_ws/ws") as ws:
        # Invoke
        ws.send_json({"action": "invoke", "payload": {"key": "lifecycle-test"}})
        invoke_resp = ws.receive_json()
        assert invoke_resp["type"] == "result"
        inv_id = invoke_resp["invocation_id"]

        # Get
        ws.send_json({"action": "get_invocation", "invocation_id": inv_id})
        get_resp = ws.receive_json()
        assert get_resp["type"] == "result"
        assert get_resp["payload"]["data"]["key"] == "lifecycle-test"

        # Cancel
        ws.send_json({"action": "cancel_invocation", "invocation_id": inv_id})
        cancel_resp = ws.receive_json()
        assert cancel_resp["type"] == "result"
        assert cancel_resp["payload"]["status"] == "cancelled"

        # Get after cancel
        ws.send_json({"action": "get_invocation", "invocation_id": inv_id})
        get_resp2 = ws.receive_json()
        assert get_resp2["type"] == "error"
        assert get_resp2["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# Missing optional handlers
# ---------------------------------------------------------------------------

def test_ws_missing_invoke_handler_returns_error():
    """Invoke without registered handler returns not_implemented error."""
    app = InvocationWSAgentServerHost()
    client = TestClient(app)
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "not_implemented"


def test_ws_missing_get_handler_returns_error():
    """get_invocation without registered handler returns not_found error."""
    app = InvocationWSAgentServerHost()

    @app.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext) -> dict:
        return {"ok": True}

    client = TestClient(app)
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "get_invocation", "invocation_id": "some-id"})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "not_found"


def test_ws_missing_cancel_handler_returns_error():
    """cancel_invocation without registered handler returns not_found error."""
    app = InvocationWSAgentServerHost()

    @app.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext) -> dict:
        return {"ok": True}

    client = TestClient(app)
    with client.websocket_connect("/invocations_ws/ws") as ws:
        ws.send_json({"action": "cancel_invocation", "invocation_id": "some-id"})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# Optional handler defaults and overrides
# ---------------------------------------------------------------------------

def test_ws_optional_handlers_default_none():
    """Get and cancel handlers default to None."""
    app = InvocationWSAgentServerHost()
    assert app._ws_get_invocation_fn is None
    assert app._ws_cancel_invocation_fn is None


def test_ws_optional_handler_override():
    """Setting an optional handler replaces None."""
    app = InvocationWSAgentServerHost()

    @app.ws_get_invocation_handler
    async def get_handler(context: InvocationWSContext) -> dict:
        return {"ok": True}

    assert app._ws_get_invocation_fn is not None
