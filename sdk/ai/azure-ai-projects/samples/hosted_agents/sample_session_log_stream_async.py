# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to stream hosted agent session logs
    using `project_client.beta.agents.get_session_log_stream` with the
    asynchronous AIProjectClient.

    Sessions only work with Hosted Agents.

    Session and log stream operations are currently preview features.
    In the Python SDK, you access these operations via
    `project_client.beta.agents`.

USAGE:
    python sample_session_log_stream_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.1.0" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_HOSTED_AGENT_NAME - The name of an existing Hosted Agent.

    If you don't have a Hosted Agent, run `sample_hosted_agent_create.py` first
    to create one as a prerequisite.

    NOTE: This sample assumes the Foundry project and Azure AI account are in the
    same resource group.

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


def _iter_sse_frames(stream, max_log_events: int):
    event_count = 0
    buffer = ""

    for chunk in stream:
        buffer += chunk.decode("utf-8", errors="replace")

        while "\n\n" in buffer:
            frame, buffer = buffer.split("\n\n", 1)
            event_name = None
            data_lines = []

            for line in frame.splitlines():
                if line.startswith("event: "):
                    event_name = line[7:]
                elif line.startswith("data: "):
                    data_lines.append(line[6:])

            if data_lines or event_name:
                event_count += 1
                yield {
                    "event": event_name,
                    "data": "\n".join(data_lines),
                }

                if event_count >= max_log_events:
                    return


async def _iter_sse_frames_async(stream, max_log_events: int):
    event_count = 0
    buffer = ""

    async for chunk in stream:
        buffer += chunk.decode("utf-8", errors="replace")

        while "\n\n" in buffer:
            frame, buffer = buffer.split("\n\n", 1)
            event_name = None
            data_lines = []

            for line in frame.splitlines():
                if line.startswith("event: "):
                    event_name = line[7:]
                elif line.startswith("data: "):
                    data_lines.append(line[6:])

            if data_lines or event_name:
                event_count += 1
                yield {
                    "event": event_name,
                    "data": "\n".join(data_lines),
                }

                if event_count >= max_log_events:
                    return


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
            version_indicator=VersionRefIndicator(agent_version=agent.version),
        )
        print(f"Session created (id: {session.agent_session_id}, status: {session.status})")
        try:
            endpoint_config = AgentEndpointConfig(
                version_selector=VersionSelector(
                    version_selection_rules=[
                        FixedRatioVersionSelectionRule(agent_version=agent.version, traffic_percentage=100),
                    ]
                ),
                protocols=[AgentEndpointProtocol.RESPONSES],
            )

            await project_client.beta.agents.patch_agent_details(
                agent_name=agent_name,
                agent_endpoint=endpoint_config,
            )

            print(f"Agent endpoint configured for agent: {agent_name}")
            input_text = "Say hello in one short sentence."

            openai_client = project_client.get_openai_client(agent_name=agent_name)
            response = await openai_client.responses.create(
                input=input_text,
                extra_body={
                    "agent_session_id": session.agent_session_id,
                },
            )
            print(f"Response output: {response.output_text}")

            print("Streaming session logs...")
            raw_stream = await project_client.beta.agents.get_session_log_stream(
                agent_name=agent_name,
                agent_version=agent.version,
                session_id=session.agent_session_id,
            )
            async for frame in _iter_sse_frames_async(raw_stream, max_log_events=30):
                print(f"SSE event: {frame.get('event')}")
                print(f"SSE data: {frame.get('data')}\n")
        finally:
            await project_client.beta.agents.delete_session(
                agent_name=agent_name,
                session_id=session.agent_session_id,
            )
            print(f"Session deleted (id: {session.agent_session_id})")


if __name__ == "__main__":
    asyncio.run(main())
