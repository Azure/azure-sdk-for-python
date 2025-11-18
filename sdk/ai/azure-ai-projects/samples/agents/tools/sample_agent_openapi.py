# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create an AI agent with OpenAPI tool capabilities
    using the OpenApiAgentTool and synchronous Azure AI Projects client. The agent can
    call external APIs defined by OpenAPI specifications.

USAGE:
    python sample_agent_openapi.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity openai python-dotenv jsonref

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
import jsonref
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    OpenApiAgentTool,
    OpenApiFunctionDefinition,
    OpenApiAnonymousAuthDetails,
)

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    weather_asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/weather_openapi.json"))

    # [START tool_declaration]
    with open(weather_asset_file_path, "r") as f:
        openapi_weather = jsonref.loads(f.read())

    tool = OpenApiAgentTool(
        openapi=OpenApiFunctionDefinition(
            name="get_weather",
            spec=openapi_weather,
            description="Retrieve weather information for a location",
            auth=OpenApiAnonymousAuthDetails(),
        )
    )
    # [END tool_declaration]

    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="You are a helpful assistant.",
            tools=[tool],
        ),
        description="You are a helpful assistant.",
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    response = openai_client.responses.create(
        input="What is the name and population of the country that uses currency with abbreviation THB?",
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )
    print(f"Response created: {response.output_text}")

    print("\nCleaning up...")
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
