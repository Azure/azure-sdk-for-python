# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run a Prompt Agent that uses the
    Fabric IQ preview tool with a synchronous client.

USAGE:
    python sample_agent_fabric_iq.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FOUNDRY_AGENT_NAME - Optional. The name of the AI agent. If not set, defaults to "MyAgent".
    4) FABRIC_IQ_PROJECT_CONNECTION_ID - The fully-qualified resource id of the Fabric IQ project connection.
    5) FABRIC_IQ_USER_INPUT - The natural-language question to send to the agent.
"""

import os
from dotenv import load_dotenv
from util import create_version_with_endpoint
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, FabricIQPreviewTool

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")

tool_payload = FabricIQPreviewTool(
    project_connection_id=os.environ["FABRIC_IQ_PROJECT_CONNECTION_ID"],
    require_approval="never",
)

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    create_version_with_endpoint(
        project_client=project_client,
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            instructions="Use the available Fabric IQ tools to answer questions and perform tasks.",
            tools=[tool_payload],
        ),
    ),
    project_client.get_openai_client(agent_name=agent_name) as openai_client,
):
    user_input = os.environ.get("FABRIC_IQ_USER_INPUT") or input("Enter your question:\n")

    response = openai_client.responses.create(
        input=user_input,
    )

    print(f"Agent response: {response.output_text}")

    # The helper restores the endpoint and deletes the temporary version automatically.
