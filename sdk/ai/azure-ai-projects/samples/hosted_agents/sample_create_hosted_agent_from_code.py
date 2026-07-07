# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Upload a code zip as a new version of a code-based Hosted Agent,
    temporarily route the agent endpoint to that version, send a test prompt,
    and download the code back to verify the round-trip. This sample shows the
    explicit `create_version_from_code`, `update_details`, endpoint restore,
    and version cleanup calls inline.

    The dependency resolution mode is selected via the
    `FOUNDRY_HOSTED_AGENT_REMOTE_BUILD` environment variable (default: `true`):

    * `false` (BUNDLED) — uploads `assets/echo-agent-prebuilt.zip`, which
      bundles the agent source plus a `packages/` folder with Linux-built
      dependencies, so the service skips pip entirely.
    * `true` (REMOTE_BUILD) — zips and uploads `assets/echo-agent/`, which
      contains only the agent source plus `requirements.txt`; the service
      resolves dependencies remotely from the public package index.

USAGE:
    python sample_create_hosted_agent_from_code.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the
       Overview page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model.
    3) FOUNDRY_HOSTED_AGENT_NAME - Optional. The Hosted Agent name. Defaults to
        `MyHostedAgent`.
    4) FOUNDRY_HOSTED_AGENT_REMOTE_BUILD - Optional. Set to `false` to use
    BUNDLED; defaults to `true` (REMOTE_BUILD).
"""

import os
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentEndpointConfig,
    CodeConfiguration,
    FixedRatioVersionSelectionRule,
    HostedAgentDefinition,
    ProtocolConfiguration,
    ProtocolVersionRecord,
    ResponsesProtocolConfiguration,
    VersionSelector,
)

from hosted_agents_util import select_basic_agent_code_zip, wait_for_agent_version_active

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
use_remote_build = os.environ.get("FOUNDRY_HOSTED_AGENT_REMOTE_BUILD", "true").strip().lower() == "true"
agent_name = os.environ.get("FOUNDRY_HOSTED_AGENT_NAME", "MyHostedAgent")

dependency_resolution, code_zip_stream = select_basic_agent_code_zip(use_remote_build)
original_agent_endpoint = None
created = None

with (
    code_zip_stream,
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    try:
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
                environment_variables={
                    "FOUNDRY_PROJECT_ENDPOINT": endpoint,
                    "FOUNDRY_MODEL_NAME": model_name,
                },
                protocol_versions=[ProtocolVersionRecord(protocol="responses", version="2.0.0")],
            ),
            code=code_zip_stream,
        )
        print(f"Hosted agent version created (id: {created.id}, name: {created.name}, version: {created.version})")

        wait_for_agent_version_active(
            project_client=project_client,
            agent_name=agent_name,
            agent_version=created.version,
        )

        original_agent_endpoint = project_client.agents.get(agent_name=agent_name).agent_endpoint
        endpoint_config = AgentEndpointConfig(
            version_selector=VersionSelector(
                version_selection_rules=[
                    FixedRatioVersionSelectionRule(agent_version=created.version, traffic_percentage=100),
                ]
            ),
            protocol_configuration=ProtocolConfiguration(responses=ResponsesProtocolConfiguration()),
        )

        project_client.agents.update_details(agent_name=agent_name, agent_endpoint=endpoint_config)
        print(f"Agent endpoint configured for version {created.version}")

        with project_client.get_openai_client(agent_name=agent_name) as openai_client:
            user_input = "Good morning!"
            print(f"Sent: {user_input}")
            response = openai_client.responses.create(
                input=user_input,
            )
        print(f"Response output: {response.output_text}")

        # Download the zip for the version we just created, and write to disk.
        downloaded_zip_path = Path(tempfile.gettempdir()) / f"{agent_name}-{created.version}.zip"

        downloaded_bytes = b"".join(
            project_client.agents.download_code(
                agent_name=agent_name,
                agent_version=created.version,
            )
        )

        downloaded_zip_path.write_bytes(downloaded_bytes)

        print(f"Downloaded version code zip to {downloaded_zip_path}: {downloaded_zip_path.stat().st_size} bytes")
    finally:
        if original_agent_endpoint is not None:
            project_client.agents.update_details(agent_name=agent_name, agent_endpoint=original_agent_endpoint)
            print("Agent endpoint restored")
        if created is not None:
            project_client.agents.delete_version(agent_name=agent_name, agent_version=created.version, force=True)
            print(f"Hosted agent version {created.version} deleted")
