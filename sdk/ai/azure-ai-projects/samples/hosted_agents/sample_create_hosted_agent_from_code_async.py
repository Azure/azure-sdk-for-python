# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Async variant of `sample_create_hosted_agent_from_code.py`. Uploads a code
    zip as a new version of a code-based Hosted Agent, polls for provisioning,
    and downloads it back to verify the round-trip.

    The dependency resolution mode is selected via the
    `FOUNDRY_HOSTED_AGENT_REMOTE_BUILD` environment variable (default: `true`):

    * `false` (BUNDLED) — uploads `assets/echo-agent-prebuilt.zip`, which
      bundles the agent source plus a `packages/` folder with Linux-built
      dependencies, so the service skips pip entirely.
    * `true` (REMOTE_BUILD) — zips and uploads `assets/echo-agent/`, which
      contains only the agent source plus `requirements.txt`; the service
      resolves dependencies remotely from the public package index.

    The agent must already exist; create it with
    `samples/hosted_agents/sample_create_hosted_agent_async.py`.

USAGE:
    python sample_create_hosted_agent_from_code_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" aiohttp python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the
       Overview page of your Microsoft Foundry portal.
    2) FOUNDRY_HOSTED_AGENT_NAME - The Hosted Agent name. Must already exist.
    3) AZURE_SUBSCRIPTION_ID - Azure subscription ID where the Azure AI account
       and project are deployed.
     4) FOUNDRY_HOSTED_AGENT_REMOTE_BUILD - Optional. Set to `false` to use
         BUNDLED; defaults to `true` (REMOTE_BUILD).
"""

import asyncio
import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    CodeConfiguration,
    HostedAgentDefinition,
    ProtocolVersionRecord,
)

from hosted_agents_util import select_echo_agent_code_zip, wait_for_agent_version_active_async
from rbac_util import ensure_agent_identity_rbac_async


async def main() -> None:
    load_dotenv()

    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.environ["FOUNDRY_HOSTED_AGENT_NAME"]
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    use_remote_build = os.environ.get("FOUNDRY_HOSTED_AGENT_REMOTE_BUILD", "true").strip().lower() == "true"

    dependency_resolution, code_zip_stream = select_echo_agent_code_zip(use_remote_build)

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):
        created = await project_client.agents.create_version_from_code(
            agent_name=agent_name,
            description=f"Code-based hosted agent uploaded with dependency_resolution={dependency_resolution.value}.",
            definition=HostedAgentDefinition(
                cpu="0.5",
                memory="1Gi",
                code_configuration=CodeConfiguration(
                    runtime="python_3_14",
                    entry_point=["python", "main.py"],
                    dependency_resolution=dependency_resolution,
                ),
                protocol_versions=[ProtocolVersionRecord(protocol="responses", version="1.0.0")],
            ),
            code=code_zip_stream,
        )
        print(f"Created code-based hosted agent version: {created.version}")

        await wait_for_agent_version_active_async(
            project_client=project_client,
            agent_name=agent_name,
            agent_version=created.version,
        )

        # ensure_agent_identity_rbac_async uses async ARM management clients with the
        # same async credential.
        await ensure_agent_identity_rbac_async(
            agent=created,
            credential=credential,
            subscription_id=subscription_id,
            foundry_project_endpoint=endpoint,
        )

        user_input = "Good morning!"
        async with project_client.get_openai_client(agent_name=agent_name) as openai_client:
            response = await openai_client.responses.create(
                input=user_input,
            )
        print(f"Sent: {user_input}")
        print(f"Response output: {response.output_text}")

        # Download the zip for the version we just created, and write to disk.
        downloaded_zip_path = Path(tempfile.gettempdir()) / f"{agent_name}-{created.version}.zip"

        downloaded_bytes = b"".join(
            [
                chunk
                async for chunk in await project_client.agents.download_code(
                    agent_name=agent_name,
                    agent_version=created.version,
                )
            ]
        )

        downloaded_zip_path.write_bytes(downloaded_bytes)

        print(f"Downloaded version code zip to {downloaded_zip_path}: {downloaded_zip_path.stat().st_size} bytes, ")


if __name__ == "__main__":
    asyncio.run(main())
