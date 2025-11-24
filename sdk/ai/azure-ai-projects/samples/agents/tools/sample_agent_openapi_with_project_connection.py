# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create an AI agent with OpenAPI tool capabilities
    using the OpenApiAgentTool with project connection authentication. The agent can
    call external APIs defined by OpenAPI specifications, using credentials stored in
    an Azure AI Project connection.

USAGE:
    python sample_agent_openapi_with_project_connection.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv jsonref

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) OPENAPI_PROJECT_CONNECTION_ID - The OpenAPI project connection ID,
       as found in the "Connections" tab in your Microsoft Foundry project.
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
    OpenApiManagedAuthDetails,
    OpenApiProjectConnectionAuthDetails,
    OpenApiProjectConnectionSecurityScheme,
)

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    tripadvisor_asset_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../assets/tripadvisor_openapi.json")
    )

    # [START tool_declaration]
    with open(tripadvisor_asset_file_path, "r") as f:
        openapi_tripadvisor = jsonref.loads(f.read())

    tool = OpenApiAgentTool(
        openapi=OpenApiFunctionDefinition(
            name="tripadvisor",
            spec=openapi_tripadvisor,
            description="Trip Advisor API to get travel information",
            auth=OpenApiProjectConnectionAuthDetails(
                security_scheme=OpenApiProjectConnectionSecurityScheme(
                    project_connection_id=os.environ["OPENAPI_PROJECT_CONNECTION_ID"]
                )
            ),
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
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    response = openai_client.responses.create(
        input="Recommend me 5 top hotels in paris, France",
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )
    print(f"Response created: {response.output_text}")

    print("\nCleaning up...")
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
