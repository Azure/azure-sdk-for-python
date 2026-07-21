# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for the host exposing the underlying M365 AgentApplication."""

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


def test_register_handler_on_agent_app():
    """The host exposes the AgentApplication via the ``agent_app`` property, so
    handlers register on it (app = host.agent_app; @app.activity / @app.error)."""
    stub = _StubAgentApp()
    host = ActivityAgentServerHost(agent_app=stub, configure_observability=None)
    app = host.agent_app

    @app.activity("message")
    async def on_message(context, state):
        pass

    @app.error
    async def on_error(context, error):
        pass

    assert ("activity", "message", on_message) in stub.registered
    assert ("error", None, on_error) in stub.registered


def test_agent_app_property_exposes_injected_app():
    """The ``agent_app`` property returns the injected AgentApplication."""
    stub = _StubAgentApp()
    app = ActivityAgentServerHost(agent_app=stub, configure_observability=None)

    assert app.agent_app is stub


def test_host_is_the_runnable_server_entrypoint():
    """The web server is started via ``host.run()`` (inherited from
    ``AgentServerHost``), NOT via the M365 ``agent_app``.

    Guards against regressing the container entrypoint to ``app.run()``: the
    M365 ``AgentApplication`` has no ``run`` method, so ``app.run()`` raises
    ``AttributeError`` at startup, binds no port, and silently drops every
    inbound activity. ``host`` is the runnable object; ``host.agent_app`` is only
    for handler registration.
    """
    from azure.ai.agentserver.core import AgentServerHost

    host = ActivityAgentServerHost(agent_app=_StubAgentApp(), configure_observability=None)

    # The host is the runnable server object, and run() comes from the core host.
    assert callable(getattr(host, "run", None))
    assert isinstance(host, AgentServerHost)
    assert "run" in dir(AgentServerHost)


def test_agent_app_raises_when_custom_handler():
    """With a custom handler, M365 is not initialized, so accessing agent_app
    raises AttributeError."""

    async def handler(request):
        return JSONResponse({})

    app = ActivityAgentServerHost(request_handler=handler, configure_observability=None)
    with pytest.raises(AttributeError):
        _ = app.agent_app


def test_custom_handler_is_used():
    """A custom handler bypasses M365 init and is used as the request handler."""

    async def handler(request):
        return JSONResponse({})

    app = ActivityAgentServerHost(request_handler=handler, configure_observability=None)

    assert app._handler is handler


def test_request_handler_rejects_sync_handler():
    """request_handler mode requires an async handler."""

    def sync_handler(request):
        return JSONResponse({})

    with pytest.raises(TypeError, match="async function"):
        ActivityAgentServerHost(request_handler=sync_handler, configure_observability=None)


def test_request_handler_does_not_seed_connection_env(monkeypatch):
    """Custom-handler mode must not mutate CONNECTIONS__* env (M365 is not built)."""
    import os

    for key in list(os.environ):
        if key.startswith("CONNECTIONS"):
            monkeypatch.delenv(key, raising=False)

    async def handler(request):
        return JSONResponse({})

    ActivityAgentServerHost(request_handler=handler, configure_observability=None)

    seeded = [k for k in os.environ if k.startswith("CONNECTIONS")]
    assert seeded == []


def test_agent_app_uses_injected_app_and_adapter():
    """agent_app mode hosts the injected app and exposes its adapter."""
    stub = _StubAgentApp()
    app = ActivityAgentServerHost(agent_app=stub, configure_observability=None)

    assert app.agent_app is stub
    assert app.adapter is stub.adapter


def test_agent_app_requires_app_with_adapter():
    """An injected app without an adapter surfaces the app's own adapter error."""

    class _NoAdapterApp:
        @property
        def adapter(self):
            raise RuntimeError("adapter not configured")

    with pytest.raises(RuntimeError, match="adapter not configured"):
        ActivityAgentServerHost(agent_app=_NoAdapterApp(), configure_observability=None)


def test_agent_app_and_request_handler_are_mutually_exclusive():
    """Passing both agent_app and request_handler raises ValueError."""

    async def handler(request):
        return JSONResponse({})

    with pytest.raises(ValueError, match="not both"):
        ActivityAgentServerHost(
            agent_app=_StubAgentApp(),
            request_handler=handler,
            configure_observability=None,
        )


def test_request_handler_rejects_build_overrides():
    """request_handler mode does not build the M365 stack, so build overrides
    (e.g. storage) are rejected rather than silently ignored."""

    async def handler(request):
        return JSONResponse({})

    with pytest.raises(ValueError, match="does not build the M365 stack"):
        ActivityAgentServerHost(
            request_handler=handler,
            storage=object(),
            configure_observability=None,
        )


def test_agent_app_rejects_build_overrides():
    """agent_app is hosted as-is, so build overrides would be ignored -> ValueError."""
    with pytest.raises(ValueError, match="would be ignored"):
        ActivityAgentServerHost(
            agent_app=_StubAgentApp(),
            storage=object(),
            configure_observability=None,
        )
