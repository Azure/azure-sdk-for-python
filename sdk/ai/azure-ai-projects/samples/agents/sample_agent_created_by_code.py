# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates upload and download for a code-based Hosted Agent
    using the `.beta.agents` sub-client of the synchronous `AIProjectClient`.

    Upload (create new version):
    1) Zips a local folder containing the agent source code in-memory.
    2) Computes the SHA-256 hex digest of the resulting zip
       (passed via the `code_zip_sha256` keyword argument; the service uses it
       for change detection / dedup and integrity verification).
    3) Calls `beta.agents.create_agent_version_from_code()` to upload the zip
       and create a new agent version backed by a code-based
       `HostedAgentDefinition` (with a `CodeConfiguration`).
    4) Polls until the new version becomes `active`.

    Download:
    5) Downloads the code zip for the new version with
       `beta.agents.download_agent_version_code()` and verifies its SHA-256
       digest matches what was uploaded (and the version's
       `code_configuration.content_hash`).
    6) Also downloads the latest version's code zip with
       `beta.agents.download_agent_code()` (no version required).

    The agent must already exist before calling
    `create_agent_version_from_code()`. You can create it with
    `samples/hosted_agents/sample_hosted_agent_create.py`.

USAGE:
    python sample_agent_created_by_code.py

    Before running the sample:

    pip install "azure-ai-projects>=2.2.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_HOSTED_AGENT_NAME - The Hosted Agent name. The agent must already exist.

    The source folder uploaded by this sample is
    `samples/hosted_agents/assets/responses-echo-agent`. Before the new version
    can become `active`, uncomment the agent code in that folder's `main.py`
    (see its README.md for details). The zip itself is built in-memory by this
    sample - there is no pre-built zip on disk.
"""

import hashlib
import io
import os
import time
import zipfile
from pathlib import Path

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeConfiguration,
    CodeDependencyResolution,
    CreateAgentVersionFromCodeContent,
    CreateAgentVersionFromCodeMetadata,
    HostedAgentDefinition,
    ProtocolVersionRecord,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ["FOUNDRY_HOSTED_AGENT_NAME"]  # Must already exist. Create it with sample_hosted_agent_create.py.

# Folder containing the agent source code (entry-point file plus any dependency
# manifest such as `requirements.txt` for `remote_build`).
code_folder = (Path(__file__).parent.parent / "hosted_agents" / "assets" / "responses-echo-agent").resolve()


def zip_folder_to_bytes(folder: Path) -> bytes:
    """Zip the contents of `folder` into an in-memory archive and return its bytes."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(folder.rglob("*")):
            if path.is_file():
                zf.write(path, arcname=path.relative_to(folder).as_posix())
    return buffer.getvalue()


def wait_for_agent_version_terminal(
    project_client: AIProjectClient,
    agent_name: str,
    agent_version: str,
    max_attempts: int = 60,
    poll_interval_seconds: int = 10,
) -> str:
    """Poll until the version reaches a terminal status (``active`` or ``failed``).

    Returns the final status string. The sample intentionally does not raise on ``failed``
    because the cause of provisioning failure (e.g. dependency resolution from a private
    package feed) is unrelated to the SDK upload/download APIs being demonstrated.
    """
    last_status = "unknown"
    for attempt in range(max_attempts):
        time.sleep(poll_interval_seconds)
        version_details = project_client.agents.get_version(agent_name=agent_name, agent_version=agent_version)
        last_status = str(version_details.status).split(".")[-1].lower()
        print(f"Agent version status: {last_status} (attempt {attempt + 1})")

        if last_status in ("active", "failed"):
            return last_status

    return last_status


# Build the zip in-memory and compute its SHA-256 hex digest.
code_zip_bytes = zip_folder_to_bytes(code_folder)
code_zip_sha256 = hashlib.sha256(code_zip_bytes).hexdigest()
print(f"Built code zip from {code_folder}: {len(code_zip_bytes)} bytes, sha256={code_zip_sha256}")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=endpoint,
        credential=credential,
        allow_preview=True,
    ) as project_client,
):
    # The multipart request body has two parts:
    #   * `metadata` - JSON describing the hosted agent definition (CPU/memory,
    #     code runtime, entry-point, dependency resolution, protocol versions).
    #   * `code`     - the zipped source code as `(filename, bytes, content_type)`.
    content = CreateAgentVersionFromCodeContent(
        metadata=CreateAgentVersionFromCodeMetadata(
            description="Code-based hosted agent created from a local source folder.",
            definition=HostedAgentDefinition(
                cpu="0.5",
                memory="1Gi",
                code_configuration=CodeConfiguration(
                    runtime="python_3_12",
                    entry_point=["python", "main.py"],
                    dependency_resolution=CodeDependencyResolution.REMOTE_BUILD,
                ),
                protocol_versions=[
                    ProtocolVersionRecord(protocol="responses", version="1.0.0"),
                ],
            ),
        ),
        code=("code.zip", code_zip_bytes, "application/zip"),
    )

    created = project_client.beta.agents.create_agent_version_from_code(
        agent_name=agent_name,
        content=content,
        code_zip_sha256=code_zip_sha256,
    )
    print(f"Created code-based hosted agent version: {created.version}")

    # Download the code zip for the specific version we just created. The service stores the
    # uploaded zip immediately, so this works even before the version finishes provisioning.
    downloaded_version_zip = b"".join(
        project_client.beta.agents.download_agent_version_code(
            agent_name=agent_name,
            agent_version=created.version,
        )
    )
    downloaded_version_sha256 = hashlib.sha256(downloaded_version_zip).hexdigest()
    print(
        f"Downloaded version code zip: {len(downloaded_version_zip)} bytes, "
        f"sha256={downloaded_version_sha256} (matches uploaded: {downloaded_version_sha256 == code_zip_sha256})"
    )

    # Download the code zip for the latest version of the agent (no version required).
    downloaded_latest_zip = b"".join(
        project_client.beta.agents.download_agent_code(agent_name=agent_name)
    )
    downloaded_latest_sha256 = hashlib.sha256(downloaded_latest_zip).hexdigest()
    print(f"Downloaded latest code zip: {len(downloaded_latest_zip)} bytes, sha256={downloaded_latest_sha256}")

    # Poll for the new version to reach a terminal status. This may take a while if the
    # service performs a remote build of the uploaded code's dependencies.
    final_status = wait_for_agent_version_terminal(
        project_client=project_client,
        agent_name=agent_name,
        agent_version=created.version,
    )
    print(f"Final agent version status: {final_status}")

    fetched = project_client.agents.get_version(agent_name=agent_name, agent_version=created.version)
    print(f"Fetched code-based hosted agent version: {fetched.version}, status: {fetched.status}")
    if isinstance(fetched.definition, HostedAgentDefinition) and fetched.definition.code_configuration:
        print(f"Service-reported content hash: {fetched.definition.code_configuration.content_hash}")
