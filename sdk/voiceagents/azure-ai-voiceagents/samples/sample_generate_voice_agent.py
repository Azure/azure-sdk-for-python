# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: sample_generate_voice_agent.py

DESCRIPTION:
    This sample demonstrates guided authoring: generating and creating a voice
    agent from a few high-level inputs plus a natural-language goal. The service
    expands the goal into a full, editable definition, creates the agent, and
    returns it. Every generated field can be refined afterward through the normal
    update/version flow.

USAGE:
    python sample_generate_voice_agent.py

    Set the environment variable before running the sample:
    1) AZURE_VOICE_AGENTS_ENDPOINT - the Foundry project endpoint, in the form
       https://<account>.services.ai.azure.com/api/projects/<project>

    Optional:
    2) AZURE_VOICE_AGENTS_MODEL - the realtime model deployment to use.
       Defaults to "gpt-realtime".

    The sample authenticates with DefaultAzureCredential, so sign in first
    (for example, with `az login`).
"""

import os

from azure.identity import DefaultAzureCredential

from azure.ai.voiceagents import VoiceAgentsClient
from azure.ai.voiceagents.models import AgentDefinitionOptInKeys, VoiceAgentType, VoiceAgentUseCase


def generate_voice_agent() -> None:
    endpoint = os.environ["AZURE_VOICE_AGENTS_ENDPOINT"]
    model = os.environ.get("AZURE_VOICE_AGENTS_MODEL", "gpt-realtime")
    preview = AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW

    with VoiceAgentsClient(endpoint=endpoint, credential=DefaultAzureCredential()) as client:
        agent = client.voice_agents.generate_voice_agent(
            name="sample-generated-agent",
            model_type="managed",
            model=model,
            agent_type=VoiceAgentType.BUSINESS,
            use_case=VoiceAgentUseCase.CUSTOMER_SUPPORT,
            goal="Help callers troubleshoot their internet connection and open a support ticket if needed.",
            foundry_features=preview,
        )
        print(f"Generated voice agent: {agent.name}")
        print(f"Instructions:\n{agent.versions.latest.definition.instructions}")

        client.voice_agents.delete_voice_agent(agent.name, foundry_features=preview)
        print(f"Deleted voice agent: {agent.name}")


if __name__ == "__main__":
    generate_voice_agent()
