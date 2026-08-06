# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Live realtime WebSocket tests for voice agents."""
import asyncio
import os
import uuid

import pytest
from azure.core.exceptions import HttpResponseError
from azure.identity.aio import DefaultAzureCredential

from azure.ai.voiceagents.aio import VoiceAgentsClient
from azure.ai.voiceagents.models import (
    AgentDefinitionOptInKeys,
    RealtimeConversationItemMessageUser,
    RealtimeConversationItemMessageUserContent,
    VoiceAgentServerEventError,
    VoiceAgentServerEventResponseDone,
    VoiceAgentType,
    VoiceAgentUseCase,
    VoiceModelType,
)

PREVIEW = AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW

pytestmark = [
    pytest.mark.live_test_only,
    pytest.mark.skipif(
        os.environ.get("AZURE_TEST_RUN_LIVE", "false").lower() != "true",
        reason="Live tests only run when AZURE_TEST_RUN_LIVE=true.",
    ),
]


async def _delete_agent_for_cleanup(client: VoiceAgentsClient, agent_name: str) -> None:
    try:
        await client.voice_agents.delete_voice_agent(agent_name, foundry_features=PREVIEW)
    except HttpResponseError as exc:
        if exc.response is None or exc.response.status_code not in (200, 404):
            raise


@pytest.mark.asyncio
async def test_realtime_typed_turn():
    """Generate an agent, stream one typed turn, and receive a completed response."""
    endpoint = os.environ.get("AZURE_VOICE_AGENTS_ENDPOINT") or os.environ["AI_SERVICES_ENDPOINT"]
    model = os.environ.get("AZURE_VOICE_AGENTS_MODEL", "gpt-realtime")
    agent_name = f"test-voice-stream-{uuid.uuid4().hex[:8]}"

    async with DefaultAzureCredential() as credential, VoiceAgentsClient(endpoint=endpoint, credential=credential) as client:
        try:
            await client.voice_agents.generate_voice_agent(
                name=agent_name,
                model_type=VoiceModelType.MANAGED,
                model=model,
                agent_type=VoiceAgentType.BUSINESS,
                use_case=VoiceAgentUseCase.CUSTOMER_SUPPORT,
                goal="Reply with a short, friendly greeting.",
                foundry_features=PREVIEW,
            )

            async with client.realtime.connect(agent_name=agent_name) as connection:
                await connection.conversation.item.create(
                    item=RealtimeConversationItemMessageUser(
                        content=[RealtimeConversationItemMessageUserContent(type="input_text", text="Hello")]
                    )
                )
                await connection.response.create()

                async def wait_for_response_done():
                    async for event in connection:
                        if isinstance(event, VoiceAgentServerEventError):
                            raise AssertionError(f"Realtime service error: {event.error.message}")
                        if isinstance(event, VoiceAgentServerEventResponseDone):
                            return event
                    raise AssertionError("Realtime connection closed before the response completed.")

                response = await asyncio.wait_for(wait_for_response_done(), timeout=45)
                assert response.response["status"] == "completed"
        finally:
            await _delete_agent_for_cleanup(client, agent_name)