# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Recorded functional tests for the async VoiceAgentsClient.

See test_voice_agents_client.py for why this suite is limited to GET/LIST
operations.
"""
from devtools_testutils import AzureRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from azure.ai.voiceagents.aio import VoiceAgentsClient

from _preparer import PREVIEW, VoiceAgentsPreparer


class TestVoiceAgentsClientAsync(AzureRecordedTestCase):
    def create_client(self, endpoint: str) -> VoiceAgentsClient:
        credential = self.get_credential(VoiceAgentsClient, is_async=True)
        return self.create_client_from_credential(VoiceAgentsClient, credential=credential, endpoint=endpoint)

    @VoiceAgentsPreparer()
    @recorded_by_proxy_async
    async def test_get_voice_agent(self, azure_voice_agents_endpoint, azure_voice_agents_agent_name):
        async with self.create_client(azure_voice_agents_endpoint) as client:
            agent = await client.voice_agents.get_voice_agent(azure_voice_agents_agent_name, foundry_features=PREVIEW)

        # NOTE: don't assert agent["name"]/["id"] against azure_voice_agents_agent_name --
        # the test-proxy's built-in default sanitizers always redact "id"/"name" body
        # fields to a generic value in playback, regardless of our own sanitizers.
        assert agent["object"] == "agent"
        assert agent["state"] in ("enabled", "disabled")

    # NOTE: list_voice_agents is intentionally not recorded here -- see the
    # comment in test_voice_agents_client.py for why.

    @VoiceAgentsPreparer()
    @recorded_by_proxy_async
    async def test_get_agent_conversation(
        self, azure_voice_agents_endpoint, azure_voice_agents_agent_name, azure_voice_agents_conversation_id
    ):
        async with self.create_client(azure_voice_agents_endpoint) as client:
            conversation = await client.agent_endpoint_conversations.get_agent_conversation(
                azure_voice_agents_agent_name, azure_voice_agents_conversation_id, foundry_features=PREVIEW
            )

        # See the note in test_get_voice_agent about not asserting on "id"/"name".
        assert conversation["object"] == "voice.conversation"
        assert conversation["status"] is not None
