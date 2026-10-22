# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Async variant of `sample_create_hosted_agent_from_image.py`. Demonstrates CRUD
    operations for Hosted Agent versions using the asynchronous AIProjectClient.
    It also routes the agent endpoint to the created version, invokes the
    hosted agent via `responses.create`, and deletes the created version.

USAGE:
    python sample_create_hosted_agent_from_image_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.1.0" aiohttp azure-mgmt-authorization azure-mgmt-resource python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_HOSTED_AGENT_NAME - Optional. The Hosted Agent name. Defaults to
        `MyHostedAgent`.
    3) FOUNDRY_AGENT_CONTAINER_IMAGE - The Hosted Agent container image in the format
       '<registry>/<repository>[:<tag>|@<digest>]'.
       You can build a sample image from the `samples/hosted_agents/assets/echo-agent` folder.
"""

import asyncio
import os

from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    AgentEndpointConfig,
    ContainerConfiguration,
    FixedRatioVersionSelectionRule,
    HostedAgentDefinition,
    ProtocolConfiguration,
    ProtocolVersionRecord,
    ResponsesProtocolConfiguration,
    VersionSelector,
)
from hosted_agents_util import wait_for_agent_version_active_async


async def main() -> None:
    load_dotenv()

    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.environ.get("FOUNDRY_HOSTED_AGENT_NAME", "MyHostedAgent")
    image = os.environ["FOUNDRY_AGENT_CONTAINER_IMAGE"]

    created = None
    original_agent_endpoint = None

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(
            endpoint=endpoint,
            credential=credential,
        ) as project_client,
    ):
        try:
            created = await project_client.agents.create_version(
                agent_name=agent_name,
                definition=HostedAgentDefinition(
                    cpu="0.5",
                    memory="1Gi",
                    container_configuration=ContainerConfiguration(image=image),
                    protocol_versions=[
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

            endpoint_config = AgentEndpointConfig(
                version_selector=VersionSelector(
                    version_selection_rules=[
                        FixedRatioVersionSelectionRule(agent_version=created.version, traffic_percentage=100),
                    ]
                ),
                protocol_configuration=ProtocolConfiguration(responses=ResponsesProtocolConfiguration()),
            )
            original_agent_endpoint = (await project_client.agents.get(agent_name=agent_name)).agent_endpoint
            await project_client.agents.update_details(agent_name=agent_name, agent_endpoint=endpoint_config)
            print(f"Agent endpoint configured for version {created.version}")

            fetched = await project_client.agents.get_version(agent_name=agent_name, agent_version=created.version)
            print(f"Fetched hosted agent version: {fetched.version}, status: {fetched.status}")

            user_input = "Good morning!"
            async with project_client.get_openai_client(agent_name=agent_name) as openai_client:
                response = await openai_client.responses.create(
                    input=user_input,
                )
            print(f"Sent: {user_input}")
            print(f"Response output: {response.output_text}")
        finally:
            if original_agent_endpoint is not None:
                await project_client.agents.update_details(
                    agent_name=agent_name,
                    agent_endpoint=original_agent_endpoint,
                )
                print("Agent endpoint restored")
            if created is not None:
                await project_client.agents.delete_version(
                    agent_name=agent_name,
                    agent_version=created.version,
                    force=True,
                )
                print(f"Hosted agent version {created.version} deleted")


if __name__ == "__main__":
    asyncio.run(main())
