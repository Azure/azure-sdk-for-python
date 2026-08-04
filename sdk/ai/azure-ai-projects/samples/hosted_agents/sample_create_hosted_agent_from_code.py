# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Upload a code zip as a new version of a code-based Hosted Agent,
    poll for provisioning, and verify functionality by sending user input.

    The dependency resolution mode is selected via the
    `FOUNDRY_HOSTED_AGENT_REMOTE_BUILD` environment variable (default: `false`):

    * `false` (BUNDLED) — uploads `assets/echo-agent-prebuilt.zip`, which
      includes the agent source plus prebuilt dependencies.
    * `true` (REMOTE_BUILD) — zips and uploads `assets/echo-agent/`, which
      contains only the agent source plus `requirements.txt`.

    The agent must already exist; create it with
    `samples/hosted_agents/sample_create_hosted_agent.py`.

USAGE:
    python sample_create_hosted_agent_from_code.py

PREREQUISITES:
    pip install "azure-ai-projects>=2.3.0" python-dotenv

    Set the following environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT: The Azure AI Project endpoint found in the 
       Foundry portal Overview page.
    2) FOUNDRY_HOSTED_AGENT_NAME: The Hosted Agent name (must already exist).
    3) AZURE_SUBSCRIPTION_ID: The Azure subscription ID deployed to Azure AI.
    4) FOUNDRY_HOSTED_AGENT_REMOTE_BUILD: Optional, defaults to `false`.
"""

import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeConfiguration,
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

dependency_resolution, code_zip_stream = select_echo_agent_code_zip(use_remote_build)

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    created = project_client.agents.create_version_from_code(
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

    user_input = "Good morning!"
    with project_client.get_openai_client(agent_name=agent_name) as openai_client:
        response = openai_client.responses.create(
            input=user_input,
        )
    print(f"Sent: {user_input}")
    print(f"Response output: {response.output_text}")

    downloaded_zip_path = Path(tempfile.gettempdir()) / f"{agent_name}-{created.version}.zip"
    downloaded_zip_path.write_bytes(
        b"".join(
            project_client.agents.download_code(
                agent_name=agent_name,
                agent_version=created.version,
            )
        )
    )
    print(
        f"Downloaded version code zip to {downloaded_zip_path}: {downloaded_zip_path.stat().st_size} bytes."
    )