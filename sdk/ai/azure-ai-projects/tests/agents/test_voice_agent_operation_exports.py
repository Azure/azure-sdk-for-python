# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for public sync and async voice-agent operation exports."""

from importlib import import_module
import inspect
from typing import get_type_hints
from unittest.mock import MagicMock

import pytest


@pytest.mark.parametrize("namespace", ["azure.ai.projects.operations", "azure.ai.projects.aio.operations"])
def test_live_conversations_operation_export(namespace):
    operations = import_module(namespace)
    generated = import_module(f"{namespace}._operations")
    operation_name = "BetaVoiceAgentsLiveConversationsOperations"
    operation_type = getattr(operations, operation_name)

    assert operation_name in operations.__all__
    assert operation_type is getattr(generated, operation_name)
    assert get_type_hints(operations.BetaVoiceAgentsOperations)["live_conversations"] is operation_type

    voice_agents = operations.BetaVoiceAgentsOperations(MagicMock(), MagicMock(), MagicMock(), MagicMock())
    assert isinstance(voice_agents.live_conversations, operation_type)
    assert inspect.iscoroutinefunction(operation_type.get) == (".aio." in namespace)


@pytest.mark.parametrize("namespace", ["azure.ai.projects.operations", "azure.ai.projects.aio.operations"])
@pytest.mark.parametrize("property_name", ["conversations", "telephony"])
def test_ga_voice_operation_exports(namespace, property_name):
    operations = import_module(namespace)
    generated = import_module(f"{namespace}._operations")
    operation_name = f"VoiceAgents{property_name.title()}Operations"
    operation_type = getattr(operations, operation_name)

    assert operation_name in operations.__all__
    assert operation_type is getattr(generated, operation_name)
    assert get_type_hints(operations.VoiceAgentsOperations)[property_name] is operation_type

    config = MagicMock(allow_preview=False)
    voice_agents = operations.VoiceAgentsOperations(MagicMock(), config, MagicMock(), MagicMock())
    assert isinstance(getattr(voice_agents, property_name), operation_type)
    assert not hasattr(voice_agents, "live_conversations")
    assert not hasattr(voice_agents, "campaigns")


@pytest.mark.parametrize("namespace", ["azure.ai.projects", "azure.ai.projects.aio"])
@pytest.mark.parametrize("allow_preview", [False, True])
def test_ga_voice_client_surface(namespace, allow_preview):
    client_type = import_module(namespace).AIProjectClient
    client = client_type("https://example.test", MagicMock(), allow_preview=allow_preview)

    assert callable(client.agents.create_from_prompt)
    assert not hasattr(client.beta, "agents")
    assert not hasattr(client.beta.voice_agents, "conversations")
    assert not hasattr(client.beta.voice_agents, "campaigns")
    assert not hasattr(client.beta.voice_agents, "realtime")
    assert client.beta.voice_agents.live is not None
    assert client.beta.voice_agents.live_conversations is not None
    assert client.beta.voice_agents.telephony is not None
    manager = client.voice_agents.realtime.connect(agent_name="voice-agent")
    assert manager._allow_preview is allow_preview


@pytest.mark.parametrize("namespace", ["azure.ai.projects.operations", "azure.ai.projects.aio.operations"])
def test_beta_telephony_operation_export(namespace):
    operations = import_module(namespace)
    generated = import_module(f"{namespace}._operations")
    operation_name = "BetaVoiceAgentsTelephonyOperations"
    operation_type = getattr(operations, operation_name)

    assert operation_name in operations.__all__
    assert "BetaVoiceAgentsCampaignsOperations" not in operations.__all__
    assert issubclass(operation_type, getattr(generated, operation_name))
    assert get_type_hints(operations.BetaVoiceAgentsOperations)["telephony"] is operation_type

    voice_agents = operations.BetaVoiceAgentsOperations(MagicMock(), MagicMock(), MagicMock(), MagicMock())
    assert isinstance(voice_agents.telephony, operation_type)
    assert not hasattr(voice_agents, "campaigns")
    assert {name for name, method in inspect.getmembers(operation_type, callable) if not name.startswith("_")} == {
        "begin_create",
        "get",
        "list",
        "begin_cancel",
        "begin_delete",
        "list_validation_errors",
        "get_operation",
    }
