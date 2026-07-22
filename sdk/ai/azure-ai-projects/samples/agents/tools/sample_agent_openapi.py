# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create an AI agent with OpenAPI tool capabilities
    using the OpenApiTool and synchronous Azure AI Projects client. The agent can
    call external APIs defined by OpenAPI specifications.

USAGE:
    python sample_agent_openapi.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv jsonref

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FOUNDRY_AGENT_NAME - Optional. The name of the AI agent. If not set, defaults to "MyAgent".
"""

import os
from typing import Any, cast
from pathlib import Path
import jsonref
from dotenv import load_dotenv
from util import create_version_with_endpoint
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    OpenApiTool,
    OpenApiFunctionDefinition,
    OpenApiAnonymousAuthDetails,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")
weather_asset_file_path = Path(__file__).resolve().parent / "../assets/weather_openapi.json"
openapi_weather = cast(dict[str, Any], jsonref.loads(weather_asset_file_path.read_text(encoding="utf-8")))

tool = OpenApiTool(
    openapi=OpenApiFunctionDefinition(
        name="get_weather",
        spec=openapi_weather,
        description="Retrieve weather information for a location.",
        auth=OpenApiAnonymousAuthDetails(),
    )
)

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
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
    response = openai_client.responses.create(
        input="Use the OpenAPI tool to print out, what is the weather in Seattle today.",
    )
    print(f"Agent response: {response.output_text}")
