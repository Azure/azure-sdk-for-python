# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create an AI agent with OpenAPI tool capabilities
    using the OpenApiTool with project connection authentication. The agent can
    call external APIs defined by OpenAPI specifications, using credentials stored in
    an Azure AI Project connection.

USAGE:
    python sample_agent_openapi_with_project_connection.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv jsonref

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) OPENAPI_PROJECT_CONNECTION_ID - The OpenAPI project connection ID,
       as found in the "Connections" tab in your Microsoft Foundry project.
"""

import os
from typing import Any, cast
import jsonref
from dotenv import load_dotenv
from util import create_version_with_endpoint
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    OpenApiTool,
    OpenApiFunctionDefinition,
    OpenApiProjectConnectionAuthDetails,
    OpenApiProjectConnectionSecurityScheme,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = "MyAgent"

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    tripadvisor_asset_file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../assets/tripadvisor_openapi.json")
    )

    with open(tripadvisor_asset_file_path, "r", encoding="utf-8") as f:
        openapi_tripadvisor = cast(dict[str, Any], jsonref.loads(f.read()))

    tool = OpenApiTool(
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

    with (
        create_version_with_endpoint(
            project_client=project_client,
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=os.environ["FOUNDRY_MODEL_NAME"],
                instructions="You are a helpful assistant.",
                tools=[tool],
            ),
        ),
        project_client.get_openai_client(agent_name=agent_name) as openai_client,
    ):
        agent = project_client.agents.get(agent_name=agent_name)
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.versions.latest.version})")

        response = openai_client.responses.create(
            input="Recommend me 5 top hotels in the United States",
        )
        # The response to the question may contain non ASCII letters. To avoid error, encode and re decode them.
        print(f"Response created: {response.output_text.encode().decode('ascii', errors='ignore')}")
