# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run a Prompt Agent that uses the
    Fabric IQ preview tool with an asynchronous client.

USAGE:
    python sample_agent_fabric_iq_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FABRIC_IQ_PROJECT_CONNECTION_ID - The fully-qualified resource id of the Fabric IQ project connection.
    4) FABRIC_IQ_USER_INPUT - The natural-language question to send to the agent.
"""

import os
import asyncio
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, FabricIQPreviewTool

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]


async def main():
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        tool_payload = FabricIQPreviewTool(
            project_connection_id=os.environ["FABRIC_IQ_PROJECT_CONNECTION_ID"],
            require_approval="never",
        )

        agent = await project_client.agents.create_version(
            agent_name="MyAgent",
            definition=PromptAgentDefinition(
                model=os.environ["FOUNDRY_MODEL_NAME"],
                instructions=(
                    "You are a helpful agent that can use Fabric IQ tools to query data and "
                    "assist users. Use the available Fabric IQ tools to answer questions and "
                    "perform tasks."
                ),
                tools=[tool_payload],
            ),
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

        user_input = os.environ.get("FABRIC_IQ_USER_INPUT") or input("Enter your question:\n")

        response = await openai_client.responses.create(
            input=user_input,
            extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        )

        print(f"Agent response: {response.output_text}")

        # Clean up the agent version so unused versions don't accumulate in the project.
        await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        print("Agent deleted")


if __name__ == "__main__":
    asyncio.run(main())
