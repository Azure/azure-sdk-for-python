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
    app = ActivityAgentServerHost(configure_observability=None, agent_app=stub)

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
    app = ActivityAgentServerHost(configure_observability=None, agent_app=stub)

    with pytest.raises(AttributeError):
        _ = app.agent_app


def test_delegation_raises_when_custom_handler():
    """With a custom handler, M365 is not initialized, so delegated attribute
    access on the host raises AttributeError."""
    async def handler(request):
        return JSONResponse({})

    app = ActivityAgentServerHost(configure_observability=None, handler=handler)
    with pytest.raises(AttributeError):
        _ = app.activity


def test_custom_handler_is_used():
    """A custom handler bypasses M365 init and is used as the request handler."""
    async def handler(request):
        return JSONResponse({})

    app = ActivityAgentServerHost(configure_observability=None, handler=handler)

    assert app._handler is handler
