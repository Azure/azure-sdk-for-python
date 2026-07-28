# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run basic Prompt Agent operations
    using the synchronous AIProjectClient, while defining a desired
    JSON schema for the response ("structured output").

    The Responses and Conversations calls in this sample are made using
    the OpenAI client from the `openai` package. See https://platform.openai.com/docs/api-reference
    for more information.

    This sample is inspired by the OpenAI example here:
    https://platform.openai.com/docs/guides/structured-outputs/supported-schemas

USAGE:
    python sample_agent_structured_output.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv pydantic

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FOUNDRY_AGENT_NAME - Optional. The name of the AI agent. If not set, defaults to "MyAgent".
"""

import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from util import create_version_with_endpoint
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    PromptAgentDefinitionTextOptions,
    TextResponseFormatJsonSchema,
)

load_dotenv()


class CalendarEvent(BaseModel):
    model_config = {"extra": "forbid"}
    name: str
    date: str = Field(description="Date in YYYY-MM-DD format")
    participants: list[str]


endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    create_version_with_endpoint(
        project_client=project_client,
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            text=PromptAgentDefinitionTextOptions(
                format=TextResponseFormatJsonSchema(name="CalendarEvent", schema=CalendarEvent.model_json_schema())
            ),
            instructions="""
                You are a helpful assistant that extracts calendar event information from the input user messages,
                and returns it in the desired structured output format.
            """,
        ),
    ),
    project_client.get_openai_client(agent_name=agent_name) as openai_client,
):

    conversation = openai_client.conversations.create(
        items=[
            {
                "type": "message",
                "role": "user",
                "content": "Alice and Bob are going to a science fair this Friday, November 7, 2025.",
            }
        ],
    )
    print(f"Created conversation with initial user message (id: {conversation.id})")

    response = openai_client.responses.create(
        conversation=conversation.id,
    )
    print(f"Response output: {response.output_text}")

    openai_client.conversations.delete(conversation_id=conversation.id)
    print("Conversation deleted")
