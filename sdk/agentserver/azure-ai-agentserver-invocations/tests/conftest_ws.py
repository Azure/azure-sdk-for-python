# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures and factory functions for WebSocket invocation tests."""
from typing import Any

import pytest
from starlette.testclient import TestClient

from azure.ai.agentserver.invocations import (
    InvocationWSAgentServerHost,
    InvocationWSContext,
    InvocationWSError,
)


# ---------------------------------------------------------------------------
# Sample OpenAPI spec used by several tests
# ---------------------------------------------------------------------------

WS_SAMPLE_OPENAPI_SPEC: dict[str, Any] = {
    "openapi": "3.0.0",
    "info": {"title": "Echo Agent", "version": "1.0.0"},
    "paths": {
        "/invocations_ws": {
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


def _make_ws_echo_agent(**kwargs: Any) -> InvocationWSAgentServerHost:
    """Create an InvocationWSAgentServerHost whose invoke handler echoes the payload."""
    app = InvocationWSAgentServerHost(**kwargs)

    @app.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext) -> dict:
        return {"echo": payload, "invocation_id": context.invocation_id}

    return app


def _make_ws_streaming_agent(**kwargs: Any) -> InvocationWSAgentServerHost:
    """Create an InvocationWSAgentServerHost whose invoke handler yields 3 JSON chunks."""
    app = InvocationWSAgentServerHost(**kwargs)

    @app.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext):
        for i in range(3):
            yield {"chunk": i}

    return app


def _make_ws_async_storage_agent(**kwargs: Any) -> InvocationWSAgentServerHost:
    """Create an InvocationWSAgentServerHost with get/cancel handlers and in-memory store."""
    app = InvocationWSAgentServerHost(**kwargs)
    store: dict[str, dict] = {}

    @app.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext) -> dict:
        store[context.invocation_id] = payload
        return {"stored": True, "invocation_id": context.invocation_id}

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

    return app


def _make_ws_validated_agent() -> InvocationWSAgentServerHost:
    """Create an InvocationWSAgentServerHost with OpenAPI spec."""
    app = InvocationWSAgentServerHost(openapi_spec=WS_SAMPLE_OPENAPI_SPEC)

    @app.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext) -> dict:
        return {"reply": f"echo: {payload['message']}"}

    return app


def _make_ws_failing_agent(**kwargs: Any) -> InvocationWSAgentServerHost:
    """Create an InvocationWSAgentServerHost whose handler raises ValueError."""
    app = InvocationWSAgentServerHost(**kwargs)

    @app.ws_invoke_handler
    async def handle(payload: dict, context: InvocationWSContext) -> dict:
        raise ValueError("something went wrong")

    return app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def ws_echo_app():
    return _make_ws_echo_agent()


@pytest.fixture()
def ws_echo_client(ws_echo_app):
    return TestClient(ws_echo_app)


@pytest.fixture()
def ws_streaming_app():
    return _make_ws_streaming_agent()


@pytest.fixture()
def ws_streaming_client(ws_streaming_app):
    return TestClient(ws_streaming_app)


@pytest.fixture()
def ws_async_storage_app():
    return _make_ws_async_storage_agent()


@pytest.fixture()
def ws_async_storage_client(ws_async_storage_app):
    return TestClient(ws_async_storage_app)


@pytest.fixture()
def ws_validated_client():
    app = _make_ws_validated_agent()
    return TestClient(app)


@pytest.fixture()
def ws_no_spec_client():
    app = _make_ws_echo_agent()
    return TestClient(app)


@pytest.fixture()
def ws_failing_app():
    return _make_ws_failing_agent()


@pytest.fixture()
def ws_failing_client(ws_failing_app):
    return TestClient(ws_failing_app)
