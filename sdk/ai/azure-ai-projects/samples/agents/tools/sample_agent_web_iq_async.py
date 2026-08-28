# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run a Prompt Agent that uses the
    WebIQ preview tool with an asynchronous client.

USAGE:
    python sample_agent_web_iq_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.6.0" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FOUNDRY_AGENT_NAME - Optional. The name of the AI agent. If not set, defaults to "MyAgent".
    4) WEB_IQ_PROJECT_CONNECTION_ID - The fully-qualified resource ID of the WebIQ project connection.
    5) WEB_IQ_USER_INPUT - The natural-language question to send to the agent.
"""

import asyncio
import os

from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, WebIQPreviewTool

from util import create_version_with_endpoint_async

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME") or "MyAgent"


async def main() -> None:
    tool_payload = WebIQPreviewTool(
        project_connection_id=os.environ["WEB_IQ_PROJECT_CONNECTION_ID"],
    )

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        create_version_with_endpoint_async(
            project_client=project_client,
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=os.environ["FOUNDRY_MODEL_NAME"],
                instructions="Use the available WebIQ tools to answer questions and perform tasks.",
                tools=[tool_payload],
            ),
        ),
        project_client.get_openai_client(agent_name=agent_name) as openai_client,
    ):
        agent = await project_client.agents.get(agent_name=agent_name)
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.versions.latest.version})")

        user_input = os.environ.get("WEB_IQ_USER_INPUT") or input("Enter your question:\n")

        response = await openai_client.responses.create(
            input=user_input,
        )

        print(f"Agent response: {response.output_text}")


if __name__ == "__main__":
    asyncio.run(main())
