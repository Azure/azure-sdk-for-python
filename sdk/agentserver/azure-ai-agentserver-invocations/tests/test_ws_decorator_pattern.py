# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for decorator-based handler registration on the ``ws_handler`` API.

Parity with :mod:`tests.test_decorator_pattern` — covers the ``@ws_handler``
decorator's behaviour, storage, and validation rules.
"""
import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from azure.ai.agentserver.invocations import InvocationAgentServerHost


# ---------------------------------------------------------------------------
# Decorator validation
# ---------------------------------------------------------------------------

def test_ws_handler_rejects_sync_function():
    """``@app.ws_handler`` must be applied to ``async def`` callables."""
    app = InvocationAgentServerHost()

    with pytest.raises(TypeError, match="async function"):
        @app.ws_handler  # type: ignore[arg-type]
        def sync_handler(websocket):  # noqa: ARG001
            pass


def test_ws_handler_returns_function_unchanged():
    """The decorator must return the original function unmodified."""
    app = InvocationAgentServerHost()

    async def handler(websocket: WebSocket) -> None:
        await websocket.accept()
        await websocket.close()

    result = app.ws_handler(handler)
    assert result is handler


# ---------------------------------------------------------------------------
# Decorator state — slot storage / defaults / re-registration
# ---------------------------------------------------------------------------

def test_ws_handler_stores_function():
    """``@app.ws_handler`` stores the registered function on the host."""
    app = InvocationAgentServerHost()

    @app.ws_handler
    async def handler(websocket: WebSocket) -> None:
        await websocket.send_text("ok")

    assert app._ws_fn is handler  # noqa: SLF001


def test_ws_handler_default_is_none():
    """Without ``@ws_handler`` the slot stays ``None``."""
    app = InvocationAgentServerHost()
    assert app._ws_fn is None  # noqa: SLF001


def test_ws_handler_last_registration_wins(caplog):
    """Re-applying ``@ws_handler`` replaces the previous function and warns."""
    import logging

    app = InvocationAgentServerHost()

    @app.ws_handler
    async def first(websocket: WebSocket) -> None:  # noqa: ARG001
        return

    with caplog.at_level(logging.WARNING, logger="azure.ai.agentserver"):
        @app.ws_handler
        async def second(websocket: WebSocket) -> None:  # noqa: ARG001
            return

    assert app._ws_fn is second  # noqa: SLF001
    assert any("overwriting previously registered handler" in r.message for r in caplog.records)


def test_ws_handler_rejects_zero_arg_coroutine():
    """A 0-arg coroutine cannot accept the WebSocket — fail at registration."""
    app = InvocationAgentServerHost()

    with pytest.raises(TypeError, match="exactly one positional argument"):
        @app.ws_handler
        async def bad() -> None:  # type: ignore[misc]
            return


def test_ws_handler_rejects_two_required_arg_coroutine():
    """A 2-required-arg coroutine cannot be bound with one positional."""
    app = InvocationAgentServerHost()

    with pytest.raises(TypeError, match="exactly one positional argument"):
        @app.ws_handler
        async def bad(websocket: WebSocket, extra: int) -> None:  # noqa: ARG001
            return


# ---------------------------------------------------------------------------
# Missing handler behaviour (parity with test_missing_invoke_handler_returns_501)
# ---------------------------------------------------------------------------

def test_ws_with_no_handler_registered_rejects_upgrade():
    """If no @ws_handler is registered the route is absent and the upgrade is rejected."""
    app = InvocationAgentServerHost()
    client = TestClient(app)

    # Starlette has no WebSocketRoute matching /invocations_ws — the upgrade
    # is rejected before any handler-level close code can be sent.
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/invocations_ws"):
            pass
