# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create an AI agent with WorkIQ capabilities
    using the WorkIQPreviewTool and synchronous Azure AI Projects client. The agent can
    access Microsoft 365 data through WorkIQ to provide insights from emails, calendar events,
    Teams messages, and other Microsoft 365 content.

    This non-streaming version waits for the complete response before returning.

    The sample shows:
    - Creating an agent with WorkIQPreviewTool configured for Microsoft 365 data access
    - Making requests that leverage WorkIQ to search and retrieve relevant information
    - Processing responses with insights from Microsoft 365 content

USAGE:
    python sample_agent_work_iq_preview_non_streaming.py

    Before running the sample:

    pip install "azure-ai-projects>=2.1.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) WORK_IQ_PROJECT_CONNECTION_ID - The WorkIQ project connection ID,
       as found in the "Connections" tab in your Microsoft Foundry project.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    WorkIQPreviewTool,
    WorkIQPreviewToolParameters,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    tool = WorkIQPreviewTool(
        work_iq_preview=WorkIQPreviewToolParameters(
            project_connection_id=os.environ["WORK_IQ_PROJECT_CONNECTION_ID"]
        )
    )

    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            instructions="""You are a helpful assistant that can access Microsoft 365 data through WorkIQ.
            Use the WorkIQ tool to search and retrieve information from emails, calendar events,
            Teams messages, and other Microsoft 365 content to assist users with their questions.""",
            tools=[tool],
        ),
        description="Agent with WorkIQ capabilities for Microsoft 365 data access.",
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    # Send a request that will trigger the WorkIQ tool (non-streaming)
    user_input = "What meetings do I have scheduled today?"
    response = openai_client.responses.create(
        input=user_input,
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )

    print(f"Response output: {response.output_text}")
