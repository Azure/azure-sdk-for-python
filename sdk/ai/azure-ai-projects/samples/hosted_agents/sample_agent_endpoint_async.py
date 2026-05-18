# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create a Hosted Agent and Session,
    configure an Agent endpoint for Responses protocol, and invoke the
    OpenAI Responses API against that agent endpoint using the
    asynchronous AIProjectClient.

    Sessions only work with Hosted Agents.

    Session and Agent endpoint operations are currently preview features.
    In the Python SDK, you access these operations via
    `project_client.beta.agents`.

USAGE:
    python sample_agent_endpoint_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.1.0" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_AGENT_CONTAINER_IMAGE - The Hosted Agent container image in the format '<registry>/<repository>[:<tag>|@<digest>]'

    You can build and push an example image from
    `samples/hosted_agents/assets/responses-echo-agent` and use that image value
    for `FOUNDRY_AGENT_CONTAINER_IMAGE`.
"""

import asyncio
import os

from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    AgentEndpoint,
    AgentEndpointProtocol,
    FixedRatioVersionSelectionRule,
    VersionSelector,
)
from hosted_agents_util import create_agent_and_session_async

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
image = os.environ["FOUNDRY_AGENT_CONTAINER_IMAGE"]
agent_name = "MySessionHostedAgent"


async def main() -> None:
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(
            endpoint=endpoint,
            credential=credential,
            allow_preview=True,
        ) as project_client,
        create_agent_and_session_async(project_client, agent_name, image) as (agent_version, session_id),
    ):
        # Configure endpoint routing so this agent name serves the created version.
        # 100% of traffic is routed to the single created version.
        endpoint_config = AgentEndpoint(
            version_selector=VersionSelector(
                version_selection_rules=[
                    FixedRatioVersionSelectionRule(agent_version=agent_version, traffic_percentage=100),
                ]
            ),
            protocols=[AgentEndpointProtocol.RESPONSES],
        )

        patched_agent = await project_client.beta.agents.patch_agent_details(
            agent_name=agent_name,
            agent_endpoint=endpoint_config,
        )
        print(f"Agent endpoint configured for agent: {patched_agent.name}")

        # Create an OpenAI client bound to the agent endpoint.
        async with project_client.get_openai_client(agent_name=agent_name) as openai_client:
            # Call Responses API and bind the request to the created agent session.
            response = await openai_client.responses.create(
                input="What is the size of France in square miles?",
                extra_body={
                    "agent_session_id": session_id,
                },
            )
            print(f"Response output: {response.output_text}")


if __name__ == "__main__":
    asyncio.run(main())
