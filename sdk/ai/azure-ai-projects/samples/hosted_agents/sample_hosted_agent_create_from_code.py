# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Upload a code zip as a new version of a code-based Hosted Agent,
    poll for provisioning, and download it back to verify the round-trip.

    The dependency resolution mode is selected via the
    `FOUNDRY_HOSTED_AGENT_REMOTE_BUILD` environment variable (default: `false`):

    * `false` (BUNDLED) — uploads `assets/echo-agent-prebuilt.zip`, which
      bundles the agent source plus a `packages/` folder with Linux-built
      dependencies, so the service skips pip entirely.
    * `true` (REMOTE_BUILD) — uploads `assets/echo-agent.zip`, which contains
      only the agent source plus `requirements.txt`; the service resolves
      dependencies remotely from the public package index.

    The agent must already exist; create it with
    `samples/hosted_agents/sample_hosted_agent_create.py`.

USAGE:
    python sample_hosted_agent_create_from_code.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the
       Overview page of your Microsoft Foundry portal.
    2) FOUNDRY_HOSTED_AGENT_NAME - The Hosted Agent name. Must already exist.
    3) AZURE_SUBSCRIPTION_ID - Azure subscription ID where the Azure AI account
       and project are deployed.
    4) FOUNDRY_HOSTED_AGENT_REMOTE_BUILD - Optional. Set to `true` to use
       REMOTE_BUILD; defaults to `false` (BUNDLED).
"""

import hashlib
import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeConfiguration,
    CreateAgentVersionFromCodeContent,
    CreateAgentVersionFromCodeMetadata,
    HostedAgentDefinition,
    ProtocolVersionRecord,
)

from hosted_agents_util import select_echo_agent_code_zip, wait_for_agent_version_active
from rbac_util import ensure_agent_identity_rbac

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ["FOUNDRY_HOSTED_AGENT_NAME"]
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
use_remote_build = os.environ.get("FOUNDRY_HOSTED_AGENT_REMOTE_BUILD", "false").strip().lower() == "true"

dependency_resolution, zip_filename, code_zip_bytes, code_zip_sha256 = select_echo_agent_code_zip(use_remote_build)

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
):
    content = CreateAgentVersionFromCodeContent(
        metadata=CreateAgentVersionFromCodeMetadata(
            description=f"Code-based hosted agent uploaded with dependency_resolution={dependency_resolution.value}.",
            definition=HostedAgentDefinition(
                cpu="0.5",
                memory="1Gi",
                code_configuration=CodeConfiguration(
                    runtime="python_3_12",
                    entry_point=["python", "main.py"],
                    dependency_resolution=dependency_resolution,
                ),
                protocol_versions=[ProtocolVersionRecord(protocol="responses", version="1.0.0")],
            ),
        ),
        code=(zip_filename, code_zip_bytes, "application/zip"),
    )

    created = project_client.beta.agents.create_agent_version_from_code(
        agent_name=agent_name,
        content=content,
        code_zip_sha256=code_zip_sha256,
    )
    print(f"Created code-based hosted agent version: {created.version}")

    wait_for_agent_version_active(
        project_client=project_client,
        agent_name=agent_name,
        agent_version=created.version,
    )

    ensure_agent_identity_rbac(
        agent=created,
        credential=credential,
        subscription_id=subscription_id,
        foundry_project_endpoint=endpoint,
    )

    # Download the zip for the version we just created, streaming to a temp file.
    version_zip_path = Path(tempfile.gettempdir()) / f"{agent_name}-{created.version}.zip"
    sha = hashlib.sha256()
    with open(version_zip_path, "wb") as f:
        for chunk in project_client.beta.agents.download_agent_version_code(
            agent_name=agent_name,
            agent_version=created.version,
        ):
            f.write(chunk)
            sha.update(chunk)
    downloaded_version_sha256 = sha.hexdigest()
    print(
        f"Downloaded version code zip to {version_zip_path}: {version_zip_path.stat().st_size} bytes, "
        f"sha256={downloaded_version_sha256} (matches uploaded: {downloaded_version_sha256 == code_zip_sha256})"
    )
