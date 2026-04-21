# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for varied payloads with WebsocketAgentServerHost over WebSocket."""
import base64

from starlette.testclient import TestClient

from azure.ai.agentserver.websocket import (
    WebsocketAgentServerHost,
    WebsocketContext,
)


# ---------------------------------------------------------------------------
# Helper: echo agent with content type tracking
# ---------------------------------------------------------------------------

def _make_content_type_echo_agent() -> WebsocketAgentServerHost:
    """Agent that echoes payload and notes the content_type field."""
    app = WebsocketAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {
            "echo": payload,
            "received_content_type": payload.get("content_type", "unknown"),
        }

    return app


def _make_sse_agent() -> WebsocketAgentServerHost:
    """Agent that returns streaming chunks."""
    app = WebsocketAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext):
        for i in range(3):
            yield {"event": i}

    return app


# ---------------------------------------------------------------------------
# Various content types (base64-encoded binary data in JSON)
# ---------------------------------------------------------------------------

def test_png_payload():
    """PNG content type payload is accepted and echoed."""
    server = _make_content_type_echo_agent()
    client = TestClient(server)
    fake_png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    with client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({
            "action": "invoke",
            "payload": {
                "content_type": "image/png",
                "data_base64": base64.b64encode(fake_png).decode(),
            },
        })
        resp = ws.receive_json()
    assert resp["type"] == "result"
    assert resp["payload"]["received_content_type"] == "image/png"
    assert base64.b64decode(resp["payload"]["echo"]["data_base64"]) == fake_png


def test_jpeg_payload():
    """JPEG content type payload is accepted."""
    server = _make_content_type_echo_agent()
    client = TestClient(server)
    fake_jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 100
    with client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({
            "action": "invoke",
            "payload": {
                "content_type": "image/jpeg",
                "data_base64": base64.b64encode(fake_jpeg).decode(),
            },
        })
        resp = ws.receive_json()
    assert resp["type"] == "result"
    assert resp["payload"]["received_content_type"] == "image/jpeg"


def test_wav_payload():
    """WAV audio content type payload is accepted."""
    server = _make_content_type_echo_agent()
    client = TestClient(server)
    fake_wav = b"RIFF" + b"\x00" * 100
    with client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({
            "action": "invoke",
            "payload": {
                "content_type": "audio/wav",
                "data_base64": base64.b64encode(fake_wav).decode(),
            },
        })
        resp = ws.receive_json()
    assert resp["type"] == "result"
    assert resp["payload"]["received_content_type"] == "audio/wav"


def test_text_plain_payload():
    """text/plain content type payload is accepted."""
    server = _make_content_type_echo_agent()
    client = TestClient(server)
    with client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({
            "action": "invoke",
            "payload": {
                "content_type": "text/plain",
                "data": "Hello, world!",
            },
        })
        resp = ws.receive_json()
    assert resp["type"] == "result"
    assert resp["payload"]["echo"]["data"] == "Hello, world!"


# ---------------------------------------------------------------------------
# Query-like parameters in payload
# ---------------------------------------------------------------------------

def test_params_in_payload():
    """Arbitrary parameters are accessible in the handler payload."""
    app = WebsocketAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {"name": payload.get("name", "unknown")}

    client = TestClient(app)
    with client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {"name": "Alice"}})
        resp = ws.receive_json()
    assert resp["type"] == "result"
    assert resp["payload"]["name"] == "Alice"


# ---------------------------------------------------------------------------
# Streaming
# ---------------------------------------------------------------------------

def test_streaming_chunks():
    """Streaming response sends multiple chunks."""
    server = _make_sse_agent()
    client = TestClient(server)
    with client.websocket_connect("/websocket/ws") as ws:
        ws.send_json({"action": "invoke", "payload": {}})
        chunks = []
        while True:
            resp = ws.receive_json()
            if resp["type"] == "stream_chunk":
                chunks.append(resp["payload"])
            elif resp["type"] == "stream_end":
                break
    assert len(chunks) == 3
    for i, chunk in enumerate(chunks):
        assert chunk == {"event": i}


# ---------------------------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------------------------

def test_health_endpoint_returns_200():
    """GET /readiness returns 200 with healthy status."""
    app = WebsocketAgentServerHost()

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {"ok": True}

    client = TestClient(app)
    resp = client.get("/readiness")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}
