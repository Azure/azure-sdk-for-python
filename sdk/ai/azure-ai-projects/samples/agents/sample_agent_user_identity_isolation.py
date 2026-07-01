# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates per-user Prompt Agent isolation while sending
    delegated end-user identities in the `x-ms-user-identity` header.

    It invokes the same Prompt Agent as two different delegated users. Each
    user gets a separate response chain, and the sample shows
    that each follow-up request continues only that user's own prior math
    context:

    * First delegated user: "1 + 1 = ?" then "+ 10" -> 12
    * Second delegated user: "2 + 2 = ?" then "+ 10" -> 14

USAGE:
    python sample_agent_user_identity_isolation.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model.
"""

import os
from uuid import uuid4

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
delegated_user_identity = str(uuid4())
delegated_user_identity_2 = str(uuid4())

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):
    agent = project_client.agents.create_version(
        agent_name="DelegatedUserAgent",
        definition=PromptAgentDefinition(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            instructions=(
                "You are a helpful assistant that answers arithmetic questions. "
                "Use the prior response context to resolve follow-up math questions like 'then + 10'."
            ),
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
    print(f"User 1: {delegated_user_identity}")
    print(f"User 2: {delegated_user_identity_2}")

    print("User 1 input: 1 + 1 = ?")
    response = openai_client.responses.create(
        input="1 + 1 = ?",
        extra_headers={"x-ms-user-identity": delegated_user_identity},
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )
    print(f"Agent: {response.output_text}")

    print("User 2 input: 2 + 2 = ?")
    response_2 = openai_client.responses.create(
        input="2 + 2 = ?",
        extra_headers={"x-ms-user-identity": delegated_user_identity_2},
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )
    print(f"Agent: {response_2.output_text}")

    print("User 1 input: then + 10")
    response = openai_client.responses.create(
        input="then + 10",
        previous_response_id=response.id,
        extra_headers={"x-ms-user-identity": delegated_user_identity},
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )
    print(f"Agent: {response.output_text}")

    print("User 2 input: then + 10")
    response_2 = openai_client.responses.create(
        input="then + 10",
        previous_response_id=response_2.id,
        extra_headers={"x-ms-user-identity": delegated_user_identity_2},
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )
    print(f"Agent: {response_2.output_text}")

    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
