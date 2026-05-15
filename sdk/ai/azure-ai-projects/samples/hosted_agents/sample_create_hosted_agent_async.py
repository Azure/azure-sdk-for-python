# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Async variant of `sample_create_hosted_agent.py`. Demonstrates CRUD
    operations for Hosted Agent versions using the asynchronous AIProjectClient.

    This is the only hosted_agents async sample that sets up agent identity
    RBAC via `ensure_agent_identity_rbac_async`.

USAGE:
    python sample_create_hosted_agent_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.1.0" aiohttp azure-mgmt-authorization azure-mgmt-resource python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_HOSTED_AGENT_NAME - The Hosted Agent name.
    3) FOUNDRY_AGENT_CONTAINER_IMAGE - The Hosted Agent container image in the format
       '<registry>/<repository>[:<tag>|@<digest>]'.
       You can build a sample image from the `samples/hosted_agents/assets/echo-agent` folder.
    4) AZURE_SUBSCRIPTION_ID - Azure subscription ID where the
       Azure AI account and project are deployed.
"""

import asyncio
import os

from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import HostedAgentDefinition, ProtocolVersionRecord
from hosted_agents_util import wait_for_agent_version_active_async
from rbac_util import ensure_agent_identity_rbac_async


async def main() -> None:
    load_dotenv()

    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.environ["FOUNDRY_HOSTED_AGENT_NAME"]
    image = os.environ["FOUNDRY_AGENT_CONTAINER_IMAGE"]
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(
            endpoint=endpoint,
            credential=credential,
            allow_preview=True,
        ) as project_client,
    ):
        created = await project_client.agents.create_version(
            agent_name=agent_name,
            definition=HostedAgentDefinition(
                cpu="0.5",
                memory="1Gi",
                image=image,
                container_protocol_versions=[
                    ProtocolVersionRecord(protocol="responses", version="1.0.0"),
                ],
            ),
            metadata={"enableVnextExperience": "true"},
        )
        print(f"Created hosted agent version: {created.version}")

        await wait_for_agent_version_active_async(
            project_client=project_client,
            agent_name=agent_name,
            agent_version=created.version,
        )

        await ensure_agent_identity_rbac_async(
            agent=created,
            credential=credential,
            subscription_id=subscription_id,
            foundry_project_endpoint=endpoint,
        )

        fetched = await project_client.agents.get_version(agent_name=agent_name, agent_version=created.version)
        print(f"Fetched hosted agent version: {fetched.version}, status: {fetched.status}")


if __name__ == "__main__":
    asyncio.run(main())
