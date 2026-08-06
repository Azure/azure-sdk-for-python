# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live management tests for voice agents.

These tests exercise operations whose current service status codes match the
TypeSpec-generated client. Agent deletion is cleanup only because the service
currently returns 200 while the generated client expects 204.
"""
import os
import uuid

import pytest
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential

from azure.ai.voiceagents import VoiceAgentsClient
from azure.ai.voiceagents.models import (
    AgentDefinitionOptInKeys,
    AzureStandardVoice,
    VoiceAgentDefinition,
    VoiceAgentType,
    VoiceAgentUseCase,
    VoiceAudioConfig,
    VoiceAudioOutputConfig,
    VoiceModelType,
    VoiceOutputModality,
)

PREVIEW = AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW

pytestmark = [
    pytest.mark.live_test_only,
    pytest.mark.skipif(
        os.environ.get("AZURE_TEST_RUN_LIVE", "false").lower() != "true",
        reason="Live tests only run when AZURE_TEST_RUN_LIVE=true.",
    ),
]


def _endpoint() -> str:
    return os.environ.get("AZURE_VOICE_AGENTS_ENDPOINT") or os.environ["AI_SERVICES_ENDPOINT"]


def _definition(model: str, instructions: str) -> VoiceAgentDefinition:
    return VoiceAgentDefinition(
        model_type=VoiceModelType.MANAGED,
        model=model,
        instructions=instructions,
        audio=VoiceAudioConfig(output=VoiceAudioOutputConfig(voice=AzureStandardVoice(name="en-US-AvaNeural"))),
        output_modalities=[VoiceOutputModality.AUDIO],
        store=False,
    )


def _delete_agent_for_cleanup(client: VoiceAgentsClient, agent_name: str) -> None:
    try:
        client.voice_agents.delete_voice_agent(agent_name, foundry_features=PREVIEW)
    except HttpResponseError as exc:
        if exc.response is None or exc.response.status_code not in (200, 404):
            raise


def test_generate_get_list_update_enable_disable_voice_agent():
    """Exercise supported voice agent management operations against a live project."""
    model = os.environ.get("AZURE_VOICE_AGENTS_MODEL", "gpt-realtime")
    agent_name = f"test-voice-management-{uuid.uuid4().hex[:8]}"

    with DefaultAzureCredential() as credential, VoiceAgentsClient(endpoint=_endpoint(), credential=credential) as client:
        try:
            generated = client.voice_agents.generate_voice_agent(
                name=agent_name,
                model_type=VoiceModelType.MANAGED,
                model=model,
                agent_type=VoiceAgentType.BUSINESS,
                use_case=VoiceAgentUseCase.CUSTOMER_SUPPORT,
                goal="Answer questions in a friendly voice. Keep replies short and natural.",
                foundry_features=PREVIEW,
            )
            assert generated["name"] == agent_name

            fetched = client.voice_agents.get_voice_agent(agent_name, foundry_features=PREVIEW)
            assert fetched["state"] == "enabled"
            assert any(item["name"] == agent_name for item in client.voice_agents.list_voice_agents(foundry_features=PREVIEW))

            updated = client.voice_agents.update_voice_agent(
                agent_name,
                definition=_definition(model, "Greet callers warmly and keep replies concise."),
                description="Updated by a live management test.",
                foundry_features=PREVIEW,
            )
            assert updated["name"] == agent_name

            client.voice_agents.disable_voice_agent(agent_name, foundry_features=PREVIEW)
            assert client.voice_agents.get_voice_agent(agent_name, foundry_features=PREVIEW)["state"] == "disabled"

            client.voice_agents.enable_voice_agent(agent_name, foundry_features=PREVIEW)
            assert client.voice_agents.get_voice_agent(agent_name, foundry_features=PREVIEW)["state"] == "enabled"
        finally:
            _delete_agent_for_cleanup(client, agent_name)