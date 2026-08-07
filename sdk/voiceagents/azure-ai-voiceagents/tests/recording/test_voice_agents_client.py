# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Recorded functional tests for the sync VoiceAgentsClient.

These exercise only read-only (GET/LIST) operations against a pre-existing
voice agent and a pre-existing, persisted conversation -- both supplied via
environment variables (see ../../samples/README.md). Agent/conversation creation
and deletion are intentionally out of scope: at the time this suite was
written, the create (expects 201) and delete (expects 204) operations did not
match what the live test service actually returns (200), so recording those
calls would bake an unrelated, known service issue into the checked-in
cassette. See /memories/repo notes for details.
"""
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from azure.ai.voiceagents import VoiceAgentsClient

from _preparer import PREVIEW, VoiceAgentsPreparer


class TestVoiceAgentsClient(AzureRecordedTestCase):
    def create_client(self, endpoint: str) -> VoiceAgentsClient:
        credential = self.get_credential(VoiceAgentsClient)
        return self.create_client_from_credential(VoiceAgentsClient, credential=credential, endpoint=endpoint)

    @VoiceAgentsPreparer()
    @recorded_by_proxy
    def test_get_voice_agent(self, azure_voice_agents_endpoint, azure_voice_agents_agent_name):
        with self.create_client(azure_voice_agents_endpoint) as client:
            agent = client.voice_agents.get_voice_agent(azure_voice_agents_agent_name, foundry_features=PREVIEW)

        # NOTE: don't assert agent["name"]/["id"] against azure_voice_agents_agent_name --
        # the test-proxy's built-in default sanitizers always redact "id"/"name" body
        # fields to a generic value in playback, regardless of our own sanitizers.
        assert agent["object"] == "agent"
        assert agent["state"] in ("enabled", "disabled")

    # NOTE: list_voice_agents is intentionally not recorded here. Against a shared
    # test resource, it returns every agent's full definition (including real
    # subscription IDs, resource groups, connection IDs, and other agents'
    # instructions), which can't be generically sanitized. See the live smoke
    # test / manual testing for that operation instead.

    @VoiceAgentsPreparer()
    @recorded_by_proxy
    def test_get_agent_conversation(
        self, azure_voice_agents_endpoint, azure_voice_agents_agent_name, azure_voice_agents_conversation_id
    ):
        with self.create_client(azure_voice_agents_endpoint) as client:
            conversation = client.agent_endpoint_conversations.get_agent_conversation(
                azure_voice_agents_agent_name,
                azure_voice_agents_conversation_id,
                foundry_features=PREVIEW,
                headers={"Accept-Encoding": "identity"},
            )

        # See the note in test_get_voice_agent about not asserting on "id"/"name".
        assert conversation["object"] == "voice.conversation"
        assert conversation["status"] is not None

    @VoiceAgentsPreparer()
    @recorded_by_proxy
    def test_list_agent_conversation_items(
        self, azure_voice_agents_endpoint, azure_voice_agents_agent_name, azure_voice_agents_conversation_id
    ):
        with self.create_client(azure_voice_agents_endpoint) as client:
            items = list(
                client.agent_endpoint_conversations.list_agent_conversation_items(
                    azure_voice_agents_agent_name,
                    azure_voice_agents_conversation_id,
                    foundry_features=PREVIEW,
                    headers={"Accept-Encoding": "identity"},
                )
            )

        assert items

    @VoiceAgentsPreparer()
    @recorded_by_proxy
    def test_list_agent_conversation_responses(
        self, azure_voice_agents_endpoint, azure_voice_agents_agent_name, azure_voice_agents_conversation_id
    ):
        with self.create_client(azure_voice_agents_endpoint) as client:
            responses = list(
                client.agent_endpoint_conversations.list_agent_conversation_responses(
                    azure_voice_agents_agent_name,
                    azure_voice_agents_conversation_id,
                    foundry_features=PREVIEW,
                    headers={"Accept-Encoding": "identity"},
                )
            )

        assert responses
        assert responses[0]["object"] == "realtime.response"

    @VoiceAgentsPreparer()
    @recorded_by_proxy
    def test_get_agent_conversation_audio_metadata(
        self, azure_voice_agents_endpoint, azure_voice_agents_agent_name, azure_voice_agents_conversation_id
    ):
        with self.create_client(azure_voice_agents_endpoint) as client:
            recording = client.agent_endpoint_conversations.get_agent_conversation_audio(
                azure_voice_agents_agent_name,
                azure_voice_agents_conversation_id,
                foundry_features=PREVIEW,
                headers={"Accept-Encoding": "identity"},
            )

        assert recording["format"] is not None
        assert recording["sample_rate"] is not None
