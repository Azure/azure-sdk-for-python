import asyncio
import hashlib
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
    use_remote_build = os.environ.get("FOUNDRY_HOSTED_AGENT_REMOTE_BUILD", "false").strip().lower() == "true"

    dependency_resolution, zip_filename, code_zip_bytes, code_zip_sha256 = select_echo_agent_code_zip(use_remote_build)

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
    ):
        created = await project_client.beta.agents.create_code_version(
            agent_name=agent_name,
            description=f"Code-based hosted agent uploaded with dependency_resolution={dependency_resolution.value}.",
            code_zip=(zip_filename, code_zip_bytes, "application/zip"),
            code_zip_sha256=code_zip_sha256,
            definition=HostedAgentDefinition(
                cpu="0.5",
                memory="1Gi",
                code_configuration=CodeConfiguration(
                    runtime="python_3_12",
                    entry_point=["python", "main.py"],
                    dependency_resolution=dependency_resolution,
                ),
                protocol_versions=[
                    ProtocolVersionRecord(protocol="responses", version="1.0.0")
                ],
            ),
        )
        print(f"Created code-based hosted agent version: {created.version}")

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

        # Download the zip for the version we just created, streaming to a temp file.
        version_zip_path = Path(tempfile.gettempdir()) / f"{agent_name}-{created.version}.zip"
        sha = hashlib.sha256()
        version_stream = await project_client.beta.agents.get_code_zip(
            agent_name=agent_name,
            agent_version=created.version,
        )
        with open(version_zip_path, "wb") as f:
            async for chunk in version_stream:
                f.write(chunk)
                sha.update(chunk)
        downloaded_version_sha256 = sha.hexdigest()
        print(
            f"Downloaded version code zip to {version_zip_path}: {version_zip_path.stat().st_size} bytes, "
            f"sha256={downloaded_version_sha256} (matches uploaded: {downloaded_version_sha256 == code_zip_sha256})"
        )


if __name__ == "__main__":
    asyncio.run(main())