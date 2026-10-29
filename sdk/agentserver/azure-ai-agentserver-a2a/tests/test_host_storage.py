# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Defaults, overrides, and ownership for host-built native handlers."""

from unittest.mock import AsyncMock, patch

import pytest
from a2a.server.agent_execution import AgentExecutor
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard

from azure.ai.agentserver.a2a import A2AAgentServerHost, FoundryTaskStore


@pytest.mark.parametrize("public_api", [A2AAgentServerHost, FoundryTaskStore])
def test_public_classes_are_marked_experimental(public_api):
    assert "This is an experimental class" in public_api.__doc__
    assert "https://aka.ms/azure-ai-agentserver-experimental" in public_api.__doc__


class _Executor(AgentExecutor):
    async def execute(self, context, event_queue):
        raise NotImplementedError

    async def cancel(self, context, event_queue):
        raise NotImplementedError


@pytest.fixture(autouse=True)
def local_host(monkeypatch):
    monkeypatch.delenv("FOUNDRY_HOSTING_ENVIRONMENT", raising=False)


def _host(**kwargs):
    return A2AAgentServerHost(
        agent_card=AgentCard(name="test", version="1.0.0"),
        configure_observability=None,
        **kwargs,
    )


def test_local_executor_defaults_to_native_memory():
    with patch("azure.ai.agentserver.a2a._host.DefaultRequestHandler", wraps=DefaultRequestHandler) as factory:
        host = _host(agent_executor=_Executor())
    assert isinstance(factory.call_args.kwargs["task_store"], InMemoryTaskStore)
    assert host._owned_task_store is None


def test_hosted_executor_defaults_to_agent_scoped_foundry_store(monkeypatch):
    monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "hosted")
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "my-agent")
    monkeypatch.setenv("FOUNDRY_AGENT_ID", "stable-agent-guid")
    with patch("azure.ai.agentserver.a2a._host.DefaultRequestHandler", wraps=DefaultRequestHandler) as factory:
        host = _host(agent_executor=_Executor())
    assert isinstance(factory.call_args.kwargs["task_store"], FoundryTaskStore)
    assert host._owned_task_store._name == "a2a/tasks/stable-agent-guid"


@pytest.mark.parametrize("hosted", [False, True])
def test_explicit_store_is_preserved(monkeypatch, hosted):
    if hosted:
        monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "hosted")
    store = InMemoryTaskStore()
    with patch("azure.ai.agentserver.a2a._host.DefaultRequestHandler", wraps=DefaultRequestHandler) as factory:
        host = _host(agent_executor=_Executor(), task_store=store)
    assert factory.call_args.kwargs["task_store"] is store
    assert host._owned_task_store is None


def test_hosted_default_requires_an_agent_namespace(monkeypatch):
    monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "hosted")
    monkeypatch.delenv("FOUNDRY_AGENT_NAME", raising=False)
    monkeypatch.delenv("FOUNDRY_AGENT_ID", raising=False)
    with pytest.raises(ValueError, match="agent identity"):
        _host(agent_executor=_Executor())


def test_existing_handler_is_preserved():
    handler = DefaultRequestHandler(
        agent_executor=_Executor(), task_store=InMemoryTaskStore(), agent_card=AgentCard(name="test")
    )
    assert _host(request_handler=handler).request_handler is handler


@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"request_handler": object(), "agent_executor": _Executor()},
        {"request_handler": object(), "task_store": InMemoryTaskStore()},
    ],
)
def test_ambiguous_or_missing_configuration_is_rejected(kwargs):
    with pytest.raises(ValueError):
        _host(**kwargs)


@pytest.mark.asyncio
async def test_shutdown_closes_host_owned_store_even_when_user_callback_fails(monkeypatch):
    monkeypatch.setenv("FOUNDRY_HOSTING_ENVIRONMENT", "hosted")
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "my-agent")
    host = _host(agent_executor=_Executor())
    close = AsyncMock()
    monkeypatch.setattr(host._owned_task_store, "aclose", close)

    @host.shutdown_handler
    async def fail():
        raise RuntimeError("shutdown callback failed")

    with pytest.raises(RuntimeError, match="shutdown callback failed"):
        await host._dispatch_shutdown()
    close.assert_awaited_once()


@pytest.mark.asyncio
async def test_shutdown_does_not_close_caller_owned_store():
    store = FoundryTaskStore("caller-owned")
    with patch.object(store, "aclose", new_callable=AsyncMock) as close:
        host = _host(agent_executor=_Executor(), task_store=store)
        await host._dispatch_shutdown()
    close.assert_not_awaited()


@pytest.mark.asyncio
async def test_owned_handler_drains_before_user_shutdown_callback():
    host = _host(agent_executor=_Executor())
    order = []

    async def drain():
        order.append("handler")

    @host.shutdown_handler
    async def close_resources():
        order.append("user")

    with patch.object(host._owned_request_handler, "aclose", side_effect=drain):
        await host._dispatch_shutdown()
    assert order == ["handler", "user"]
