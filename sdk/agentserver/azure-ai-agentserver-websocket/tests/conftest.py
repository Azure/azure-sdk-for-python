# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures and factory functions for websocket WebSocket tests."""
from typing import Any

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.websocket import (
    WebsocketAgentServerHost,
    WebsocketContext,
    WebsocketError,
)


# ---------------------------------------------------------------------------
# Sample OpenAPI spec used by several tests
# ---------------------------------------------------------------------------

SAMPLE_OPENAPI_SPEC: dict[str, Any] = {
    "openapi": "3.0.0",
    "info": {"title": "Echo Agent", "version": "1.0.0"},
    "paths": {
        "/websocket": {
            "post": {
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["message"],
                                "properties": {
                                    "message": {"type": "string"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "reply": {"type": "string"},
                                    },
                                }
                            }
                        },
                    }
                },
            }
        }
    },
}


# ---------------------------------------------------------------------------
# Factory functions
# ---------------------------------------------------------------------------


def _make_echo_agent(**kwargs: Any) -> WebsocketAgentServerHost:
    """Create an WebsocketAgentServerHost whose invoke handler echoes the payload."""
    app = WebsocketAgentServerHost(**kwargs)

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {"echo": payload, "websocket_id": context.websocket_id}

    return app


def _make_streaming_agent(**kwargs: Any) -> WebsocketAgentServerHost:
    """Create an WebsocketAgentServerHost whose invoke handler yields 3 JSON chunks."""
    app = WebsocketAgentServerHost(**kwargs)

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext):
        for i in range(3):
            yield {"chunk": i}

    return app


def _make_async_storage_agent(**kwargs: Any) -> WebsocketAgentServerHost:
    """Create an WebsocketAgentServerHost with get/cancel handlers and in-memory store."""
    app = WebsocketAgentServerHost(**kwargs)
    store: dict[str, dict] = {}

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        store[context.websocket_id] = payload
        return {"stored": True, "websocket_id": context.websocket_id}

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

    return app


def _make_validated_agent() -> WebsocketAgentServerHost:
    """Create an WebsocketAgentServerHost with OpenAPI spec."""
    app = WebsocketAgentServerHost(openapi_spec=SAMPLE_OPENAPI_SPEC)

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        return {"reply": f"echo: {payload['message']}"}

    return app


def _make_failing_agent(**kwargs: Any) -> WebsocketAgentServerHost:
    """Create an WebsocketAgentServerHost whose handler raises ValueError."""
    app = WebsocketAgentServerHost(**kwargs)

    @app.invoke_handler
    async def handle(payload: dict, context: WebsocketContext) -> dict:
        raise ValueError("something went wrong")

    return app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def echo_app():
    return _make_echo_agent()


@pytest.fixture()
def echo_client(echo_app):
    return TestClient(echo_app)


@pytest.fixture()
def streaming_app():
    return _make_streaming_agent()


@pytest.fixture()
def streaming_client(streaming_app):
    return TestClient(streaming_app)


@pytest.fixture()
def async_storage_app():
    return _make_async_storage_agent()


@pytest.fixture()
def async_storage_client(async_storage_app):
    return TestClient(async_storage_app)


@pytest.fixture()
def validated_client():
    app = _make_validated_agent()
    return TestClient(app)


@pytest.fixture()
def no_spec_client():
    app = _make_echo_agent()
    return TestClient(app)


@pytest.fixture()
def failing_app():
    return _make_failing_agent()


@pytest.fixture()
def failing_client(failing_app):
    return TestClient(failing_app)
