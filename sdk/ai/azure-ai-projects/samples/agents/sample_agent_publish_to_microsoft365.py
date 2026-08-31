# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create a Prompt Agent and publish it to
    Microsoft 365 / Microsoft Teams using the synchronous AIProjectClient.

USAGE:
    python sample_agent_publish_to_microsoft365.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FOUNDRY_BOT_SERVICE_ARM_ID - The ARM resource ID of the Azure Bot Service that fronts the
       agent in Microsoft Teams.
    4) FOUNDRY_AGENT_NAME - Optional. The name of the AI agent. If not set, defaults to
       "MyMicrosoft365Agent".
"""

import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentEndpointConfig,
    FixedRatioVersionSelectionRule,
    Microsoft365PublishScope,
    PromptAgentDefinition,
    ProtocolConfiguration,
    ResponsesProtocolConfiguration,
    VersionSelector,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model = os.environ["FOUNDRY_MODEL_NAME"]
bot_service_arm_id = os.environ["FOUNDRY_BOT_SERVICE_ARM_ID"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME") or "MyMicrosoft365Agent"

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    created_version = project_client.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=model,
            instructions="You are a helpful assistant for Microsoft Teams users.",
        ),
    )
    print(
        f"Agent created (id: {created_version.id}, name: {created_version.name}, "
        f"version: {created_version.version})"
    )

    endpoint_config = AgentEndpointConfig(
        version_selector=VersionSelector(
            version_selection_rules=[
                FixedRatioVersionSelectionRule(
                    agent_version=created_version.version,
                    traffic_percentage=100,
                )
            ]
        ),
        protocol_configuration=ProtocolConfiguration(responses=ResponsesProtocolConfiguration()),
    )
    project_client.agents.update_details(agent_name=agent_name, agent_endpoint=endpoint_config)
    print(f"Agent endpoint configured for version {created_version.version}")

    publish_result = project_client.agents.publish_to_microsoft365(
        agent_name=agent_name,
        publish_scope=Microsoft365PublishScope.PERSONAL,
        bot_service_arm_id=bot_service_arm_id,
        agent_display_name=agent_name,
    )
    print(
        f"Agent published to Microsoft 365 (title id: {publish_result.title_id}, "
        f"Teams app id: {publish_result.teams_app_id})"
    )
