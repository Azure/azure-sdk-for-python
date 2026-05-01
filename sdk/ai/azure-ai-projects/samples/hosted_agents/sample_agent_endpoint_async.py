# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use an existing Hosted Agent and create a Session,
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
    2) FOUNDRY_HOSTED_AGENT_NAME - The name of an existing Hosted Agent.

    If you don't have a Hosted Agent, run `sample_hosted_agent_create.py` first
    to create one as a prerequisite.
"""

import asyncio
import os

from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    AgentEndpointConfig,
    AgentEndpointProtocol,
    FixedRatioVersionSelectionRule,
    VersionSelector,
)
from azure.ai.projects.models import VersionRefIndicator
from hosted_agents_util import get_latest_active_agent_version_async

load_dotenv()


async def main():
    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.environ["FOUNDRY_HOSTED_AGENT_NAME"]

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(
            endpoint=endpoint,
            credential=credential,
            allow_preview=True,
        ) as project_client,
    ):

        agent = await get_latest_active_agent_version_async(project_client, agent_name)

        session = await project_client.beta.agents.create_session(
            agent_name=agent_name,
            isolation_key="sample-isolation-key",
            version_indicator=VersionRefIndicator(agent_version=agent.version),
        )
        print(f"Session created (id: {session.agent_session_id}, status: {session.status})")
        try:
            # Configure endpoint routing so this agent name serves the created version.
            # 100% of traffic is routed to the single created version.
            endpoint_config = AgentEndpointConfig(
                version_selector=VersionSelector(
                    version_selection_rules=[
                        FixedRatioVersionSelectionRule(agent_version=agent.version, traffic_percentage=100),
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
            openai_client = project_client.get_openai_client(agent_name=agent_name)

            # Call Responses API and bind the request to the created agent session.
            response = await openai_client.responses.create(
                input="What is the size of France in square miles?",
                extra_body={
                    "agent_session_id": session.agent_session_id,
                },
            )
            print(f"Response output: {response.output_text}")
        finally:
            await project_client.beta.agents.delete_session(
                agent_name=agent_name,
                session_id=session.agent_session_id,
                isolation_key="sample-isolation-key",
            )
            print(f"Session deleted (id: {session.agent_session_id})")


if __name__ == "__main__":
    asyncio.run(main())
