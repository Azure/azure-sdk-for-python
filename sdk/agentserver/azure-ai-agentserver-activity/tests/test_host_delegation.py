# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the host delegating to the underlying M365 AgentApplication."""

import pytest
from starlette.responses import JSONResponse

from azure.ai.agentserver.activity import ActivityAgentServerHost


class _StubAgentApp:
    """Minimal stand-in for the M365 AgentApplication (avoids a real build)."""

    def __init__(self):
        self.adapter = object()
        self.registered = []

    def activity(self, activity_type):
        def decorator(fn):
            self.registered.append(("activity", activity_type, fn))
            return fn
        return decorator

    def error(self, fn):
        self.registered.append(("error", None, fn))
        return fn


def test_register_handler_directly_on_host():
    """The host delegates unknown attributes to the AgentApplication, so
    handlers can be registered directly on the host (app.activity / app.error)."""
    stub = _StubAgentApp()
    app = ActivityAgentServerHost.from_agent_application(stub, configure_observability=None)

    @app.activity("message")
    async def on_message(context, state):
        pass

    @app.error
    async def on_error(context, error):
        pass

    assert ("activity", "message", on_message) in stub.registered
    assert ("error", None, on_error) in stub.registered


def test_no_public_agent_app_attribute():
    """The host no longer exposes an ``agent_app`` accessor; delegation to the
    AgentApplication (which has no ``agent_app``) raises AttributeError."""
    stub = _StubAgentApp()
    app = ActivityAgentServerHost.from_agent_application(stub, configure_observability=None)

    with pytest.raises(AttributeError):
        _ = app.agent_app


def test_delegation_raises_when_custom_handler():
    """With a custom handler, M365 is not initialized, so delegated attribute
    access on the host raises AttributeError."""
    async def handler(request):
        return JSONResponse({})

    app = ActivityAgentServerHost.from_request_handler(handler, configure_observability=None)
    with pytest.raises(AttributeError):
        _ = app.activity


def test_custom_handler_is_used():
    """A custom handler bypasses M365 init and is used as the request handler."""
    async def handler(request):
        return JSONResponse({})

    app = ActivityAgentServerHost.from_request_handler(handler, configure_observability=None)

    assert app._handler is handler


def test_from_request_handler_rejects_sync_handler():
    """from_request_handler requires an async handler."""
    def sync_handler(request):
        return JSONResponse({})

    with pytest.raises(TypeError, match="async function"):
        ActivityAgentServerHost.from_request_handler(sync_handler, configure_observability=None)


def test_from_request_handler_does_not_seed_connection_env(monkeypatch):
    """Custom-handler mode must not mutate CONNECTIONS__* env (M365 is not built)."""
    import os

    for key in list(os.environ):
        if key.startswith("CONNECTIONS"):
            monkeypatch.delenv(key, raising=False)

    async def handler(request):
        return JSONResponse({})

    ActivityAgentServerHost.from_request_handler(handler, configure_observability=None)

    seeded = [k for k in os.environ if k.startswith("CONNECTIONS")]
    assert seeded == []


def test_from_agent_application_uses_injected_app_and_adapter():
    """from_agent_application hosts the injected app and exposes its adapter."""
    stub = _StubAgentApp()
    app = ActivityAgentServerHost.from_agent_application(stub, configure_observability=None)

    assert app._agent_app is stub
    assert app.adapter is stub.adapter


def test_from_agent_application_requires_app_with_adapter():
    """An injected app without an adapter raises a clear ValueError."""
    class _NoAdapterApp:
        @property
        def adapter(self):
            raise RuntimeError("adapter not configured")

    with pytest.raises(ValueError, match="no adapter"):
        ActivityAgentServerHost.from_agent_application(_NoAdapterApp(), configure_observability=None)
