# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""A single, minimal, always-live smoke test.

Unlike the recorded suites, this test never plays back from a cassette -- it
always talks to the real service, to catch problems (auth, wire format,
serialization) that a recording could mask. It only exercises a safe,
side-effect-free read operation against a pre-existing voice agent so it can
be run repeatedly without needing cleanup.

Run explicitly:

    $env:AZURE_TEST_RUN_LIVE = "true"
    pytest tests/test_smoke_live.py -v
"""
import os

import pytest
from azure.identity import DefaultAzureCredential

from azure.ai.voiceagents import VoiceAgentsClient
from azure.ai.voiceagents.models import AgentDefinitionOptInKeys

PREVIEW = AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW

pytestmark = [
    pytest.mark.live_test_only,
    pytest.mark.skipif(
        os.environ.get("AZURE_TEST_RUN_LIVE", "false").lower() != "true",
        reason="Live smoke test only runs when AZURE_TEST_RUN_LIVE=true.",
    ),
]


def test_smoke_get_voice_agent():
    endpoint = os.environ["AZURE_VOICE_AGENTS_ENDPOINT"]
    agent_name = os.environ["AZURE_VOICE_AGENTS_AGENT_NAME"]

    with DefaultAzureCredential() as credential, VoiceAgentsClient(endpoint=endpoint, credential=credential) as client:
        agent = client.voice_agents.get_voice_agent(agent_name, foundry_features=PREVIEW)

    assert agent["name"] == agent_name
