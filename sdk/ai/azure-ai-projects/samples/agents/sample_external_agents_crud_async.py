# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to perform CRUD operations on External Agents
    using the asynchronous AIProjectClient.

    External Agents are a preview feature. They register third-party agents hosted
    outside Microsoft Foundry. Registration is metadata-only: Foundry uses the
    OpenTelemetry agent identifier to light up traces and evaluations for spans
    emitted by your external agent.

USAGE:
    python sample_external_agents_crud_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
"""

import asyncio
import os

from dotenv import load_dotenv

from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    ExternalAgentDefinition,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]


async def main() -> None:
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    ):
        agent_name = "sample-external-agent"
        otel_agent_id = "sample-external-agent"

        try:
            await project_client.agents.delete(agent_name, force=True)
            print(f"External agent `{agent_name}` deleted")
        except ResourceNotFoundError:
            pass

        created = await project_client.agents.create_version(
            agent_name=agent_name,
            definition=ExternalAgentDefinition(otel_agent_id=otel_agent_id),
            description="External agent registered by the azure-ai-projects sample.",
            metadata={"sample": "external_agents_crud", "status": "created"},
        )
        print(f"Created external agent: {created.name} version={created.version} otel_agent_id={otel_agent_id}")

        fetched_agent = await project_client.agents.get(agent_name)
        print(f"Retrieved external agent: {fetched_agent.name} latest_version={fetched_agent.versions.latest.version}")

        fetched_version = await project_client.agents.get_version(agent_name=agent_name, agent_version=created.version)
        print(f"Retrieved external agent version: {fetched_version.name} version={fetched_version.version}")

        external_agents = []
        async for external_agent in project_client.agents.list(kind="external", limit=10):
            external_agents.append(external_agent)
        print(f"Found {len(external_agents)} external agents or more")
        for external_agent in external_agents:
            print(f"  - {external_agent.name} ({external_agent.id})")

        deleted = await project_client.agents.delete(agent_name, force=True)
        print(f"Deleted external agent: {deleted.name} deleted={deleted.deleted}")


if __name__ == "__main__":
    asyncio.run(main())
