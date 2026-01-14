# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run basic Prompt Agent operations
    using the asynchronous AIProjectClient, while defining a desired
    JSON schema for the response ("structured output").

    The Responses and Conversations calls in this sample are made using
    the OpenAI client from the `openai` package. See https://platform.openai.com/docs/api-reference
    for more information.

    This sample is inspired by the OpenAI example here:
    https://platform.openai.com/docs/guides/structured-outputs/supported-schemas

USAGE:
    python sample_agent_structured_output_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv aiohttp  pydantic

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import asyncio
import os
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    PromptAgentDefinitionText,
    TextResponseFormatJsonSchema,
    ResponseFormatJsonSchemaSchema,
)
from pydantic import BaseModel, Field

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]


class CalendarEvent(BaseModel):
    model_config = {"extra": "forbid"}
    name: str
    date: str = Field(description="Date in YYYY-MM-DD format")
    participants: list[str]


async def main() -> None:
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        agent = await project_client.agents.create_version(
            agent_name="MyAgent",
            definition=PromptAgentDefinition(
                model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                text=PromptAgentDefinitionText(
                    format=TextResponseFormatJsonSchema(
                        name="CalendarEvent", schema=ResponseFormatJsonSchemaSchema(CalendarEvent.model_json_schema())
                    )
                ),
                instructions="""
                    You are a helpful assistant that extracts calendar event information from the input user messages,
                    and returns it in the desired structured output format.
                """,
            ),
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

        conversation = await openai_client.conversations.create(
            items=[
                {
                    "type": "message",
                    "role": "user",
                    "content": "Alice and Bob are going to a science fair this Friday, November 7, 2025.",
                }
            ],
        )
        print(f"Created conversation with initial user message (id: {conversation.id})")

        response = await openai_client.responses.create(
            conversation=conversation.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            input="",
        )
        print(f"Response output: {response.output_text}")

        await openai_client.conversations.delete(conversation_id=conversation.id)
        print("Conversation deleted")

        await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        print("Agent deleted")


if __name__ == "__main__":
    asyncio.run(main())
