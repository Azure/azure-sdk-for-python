# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures and factory functions for conversations WebSocket tests."""
from typing import Any

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.conversations import (
    ConversationAgentServerHost,
    ConversationContext,
    ConversationError,
)


# ---------------------------------------------------------------------------
# Sample OpenAPI spec used by several tests
# ---------------------------------------------------------------------------

SAMPLE_OPENAPI_SPEC: dict[str, Any] = {
    "openapi": "3.0.0",
    "info": {"title": "Echo Agent", "version": "1.0.0"},
    "paths": {
        "/conversations": {
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


def _make_echo_agent(**kwargs: Any) -> ConversationAgentServerHost:
    """Create an ConversationAgentServerHost whose invoke handler echoes the payload."""
    app = ConversationAgentServerHost(**kwargs)

    @app.invoke_handler
    async def handle(payload: dict, context: ConversationContext) -> dict:
        return {"echo": payload, "conversation_id": context.conversation_id}

    return app


def _make_streaming_agent(**kwargs: Any) -> ConversationAgentServerHost:
    """Create an ConversationAgentServerHost whose invoke handler yields 3 JSON chunks."""
    app = ConversationAgentServerHost(**kwargs)

    @app.invoke_handler
    async def handle(payload: dict, context: ConversationContext):
        for i in range(3):
            yield {"chunk": i}

    return app


def _make_async_storage_agent(**kwargs: Any) -> ConversationAgentServerHost:
    """Create an ConversationAgentServerHost with get/cancel handlers and in-memory store."""
    app = ConversationAgentServerHost(**kwargs)
    store: dict[str, dict] = {}

    @app.invoke_handler
    async def handle(payload: dict, context: ConversationContext) -> dict:
        store[context.conversation_id] = payload
        return {"stored": True, "conversation_id": context.conversation_id}

    @app.get_conversation_handler
    async def get_handler(context: ConversationContext) -> dict:
        if context.conversation_id not in store:
            raise ConversationError("not_found", "Not found")
        return {"data": store[context.conversation_id]}

    @app.cancel_conversation_handler
    async def cancel_handler(context: ConversationContext) -> dict:
        if context.conversation_id not in store:
            raise ConversationError("not_found", "Not found")
        del store[context.conversation_id]
        return {"status": "cancelled"}

    return app


def _make_validated_agent() -> ConversationAgentServerHost:
    """Create an ConversationAgentServerHost with OpenAPI spec."""
    app = ConversationAgentServerHost(openapi_spec=SAMPLE_OPENAPI_SPEC)

    @app.invoke_handler
    async def handle(payload: dict, context: ConversationContext) -> dict:
        return {"reply": f"echo: {payload['message']}"}

    return app


def _make_failing_agent(**kwargs: Any) -> ConversationAgentServerHost:
    """Create an ConversationAgentServerHost whose handler raises ValueError."""
    app = ConversationAgentServerHost(**kwargs)

    @app.invoke_handler
    async def handle(payload: dict, context: ConversationContext) -> dict:
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
