# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for decorator-based handler registration on WebsocketAgentServerHost."""
from starlette.testclient import TestClient

from azure.ai.agentserver.websocket import (
    WebsocketAgentServerHost,
    WebsocketContext,
    WebsocketError,
)


# ---------------------------------------------------------------------------
# invoke_handler stores function
# ---------------------------------------------------------------------------

def test_invoke_handler_stores_function():
    """@app.invoke_handler stores the function on the protocol object."""
    app = WebsocketAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {"ok": True}

    assert app._invoke_fn is handle


# ---------------------------------------------------------------------------
# invoke_handler returns original function
# ---------------------------------------------------------------------------

def test_invoke_handler_returns_original_function():
    """@app.invoke_handler returns the original function."""
    app = WebsocketAgentServerHost()

    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {"ok": True}

    result = app.invoke_handler(handle)
    assert result is handle


# ---------------------------------------------------------------------------
# get_websocket_handler stores function
# ---------------------------------------------------------------------------

def test_get_websocket_handler_stores_function():
    """@app.get_websocket_handler stores the function."""
    app = WebsocketAgentServerHost()

    @app.get_websocket_handler
    async def get_handler(context: WebsocketContext) -> dict:
        return {"ok": True}

    assert app._get_websocket_fn is get_handler


# ---------------------------------------------------------------------------
# cancel_websocket_handler stores function
# ---------------------------------------------------------------------------

def test_cancel_websocket_handler_stores_function():
    """@app.cancel_websocket_handler stores the function."""
    app = WebsocketAgentServerHost()

    @app.cancel_websocket_handler
    async def cancel_handler(context: WebsocketContext) -> dict:
        return {"ok": True}

    assert app._cancel_websocket_fn is cancel_handler


# ---------------------------------------------------------------------------
# shutdown_handler stores function
# ---------------------------------------------------------------------------

def test_shutdown_handler_stores_function():
    """@server.shutdown_handler stores the function on the server."""
    app = WebsocketAgentServerHost()

    @app.shutdown_handler
    async def on_shutdown():
        pass

    assert app._shutdown_fn is on_shutdown


# ---------------------------------------------------------------------------
# Full request flow
# ---------------------------------------------------------------------------

def test_full_request_flow():
    """Full lifecycle: invoke → get → cancel → get (not_found)."""
    app = WebsocketAgentServerHost()
    store: dict[str, dict] = {}

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        store[context.websocket_id] = payload
        return {"stored": True}

    @app.get_websocket_handler
    async def get_handler(context: WebsocketContext) -> dict:
        if context.websocket_id not in store:
            raise WebsocketError("not_found", "Not found")
        return {"data": store[context.websocket_id]}

    @app.cancel_websocket_handler
    async def cancel_handler(context: WebsocketContext) -> dict:
        if context.websocket_id not in store:
            raise WebsocketError("not_found", "Not found")
        del store[context.websocket_id]
        return {"status": "cancelled"}

    client = TestClient(app)
    with client.websocket_connect("/websocket/ws") as ws:
        # Invoke
        ws.send_json({"action": "invoke", "payload": {"key": "lifecycle-test"}})
        invoke_resp = ws.receive_json()
        assert invoke_resp["type"] == "result"
        inv_id = invoke_resp["websocket_id"]

        # Get
        ws.send_json({"action": "get_websocket", "websocket_id": inv_id})
        get_resp = ws.receive_json()
        assert get_resp["type"] == "result"
        assert get_resp["payload"]["data"]["key"] == "lifecycle-test"

        # Cancel
        ws.send_json({"action": "cancel_websocket", "websocket_id": inv_id})
        cancel_resp = ws.receive_json()
        assert cancel_resp["type"] == "result"
        assert cancel_resp["payload"]["status"] == "cancelled"

        # Get after cancel
        ws.send_json({"action": "get_websocket", "websocket_id": inv_id})
        get_resp2 = ws.receive_json()
        assert get_resp2["type"] == "error"
        assert get_resp2["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# Missing optional handlers
# ---------------------------------------------------------------------------

def test_missing_invoke_handler_returns_error():
    """Invoke without registered handler returns not_implemented error."""
    app = WebsocketAgentServerHost()
    client = TestClient(app)
    with client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "not_implemented"


def test_missing_get_handler_returns_error():
    """get_websocket without registered handler returns not_found error."""
    app = WebsocketAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {"ok": True}

    client = TestClient(app)
    with client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "get_websocket", "websocket_id": "some-id"})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "not_found"


def test_missing_cancel_handler_returns_error():
    """cancel_websocket without registered handler returns not_found error."""
    app = WebsocketAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {"ok": True}

    client = TestClient(app)
    with client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "cancel_websocket", "websocket_id": "some-id"})
        resp = ws.receive_json()
    assert resp["type"] == "error"
    assert resp["error"]["code"] == "not_found"


# ---------------------------------------------------------------------------
# Optional handler defaults and overrides
# ---------------------------------------------------------------------------

def test_optional_handlers_default_none():
    """Get and cancel handlers default to None."""
    app = WebsocketAgentServerHost()
    assert app._get_websocket_fn is None
    assert app._cancel_websocket_fn is None


def test_optional_handler_override():
    """Setting an optional handler replaces None."""
    app = WebsocketAgentServerHost()

    @app.get_websocket_handler
    async def get_handler(context: WebsocketContext) -> dict:
        return {"ok": True}

    assert app._get_websocket_fn is not None
