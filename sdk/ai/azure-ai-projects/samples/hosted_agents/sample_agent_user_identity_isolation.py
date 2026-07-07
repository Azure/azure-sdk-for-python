# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates per-user Hosted Agent isolation while sending
    delegated end-user identities in the `x-ms-user-identity` header.

    It packages the basic hosted-agent source folder as a new Hosted Agent
    version, routes the `MyHostedAgent` endpoint to that version, and then
    invokes the same Hosted Agent as two different delegated users. The sample
    shows that a follow-up request can continue a prior response chain only
    when the delegated user identity matches the user who started it:

    * First delegated user: "1 + 1 = ?" then "then + 10" -> 12
    * Second delegated user: attempting "then + 10" against the first user's
      response chain is expected to fail with `404 NotFound`, confirming the
      response history is isolated per delegated user.

USAGE:
    python sample_agent_user_identity_isolation.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model.
    3) AZURE_SUBSCRIPTION_ID - Azure subscription ID where the Azure AI account
    and project are deployed.
    4) DELEGATED_USER_IDENTITY - Optional fixed delegated user identity to use
        for the first request chain. If omitted, a random UUID is generated.
    5) DELEGATED_USER_IDENTITY_2 - Optional fixed delegated user identity to
        use for the second user. If omitted, a random UUID is generated.
"""

import os
import sys
import time
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from openai import NotFoundError

from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentEndpointConfig,
    CodeConfiguration,
    CodeDependencyResolution,
    FixedRatioVersionSelectionRule,
    HostedAgentDefinition,
    ProtocolConfiguration,
    ProtocolVersionRecord,
    ResponsesProtocolConfiguration,
    VersionSelector,
)

_SAMPLES_DIR = Path(__file__).resolve().parents[1]
if str(_SAMPLES_DIR) not in sys.path:
    sys.path.insert(0, str(_SAMPLES_DIR))

from rbac_util import ensure_agent_identity_rbac
from util import zip

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
agent_name = "MyHostedAgent"
delegated_user_identity = os.environ.get("DELEGATED_USER_IDENTITY", str(uuid4()))
delegated_user_identity_2 = os.environ.get("DELEGATED_USER_IDENTITY_2", str(uuid4()))
hosted_agent_source_dir = Path(__file__).parent / "assets" / "basic-agent"

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    created_version = None
    original_agent_endpoint = None

    try:
        zip_filename = "basic-agent.zip"
        zip_path = zip(hosted_agent_source_dir, zip_filename)[2]

        with zip_path.open("rb") as code_stream:
            created_version = project_client.agents.create_version_from_code(
                agent_name=agent_name,
                description="Hosted agent version for delegated user identity isolation.",
                definition=HostedAgentDefinition(
                    cpu="0.5",
                    memory="1Gi",
                    code_configuration=CodeConfiguration(
                        runtime="python_3_14",
                        entry_point=["python", "main.py"],
                        dependency_resolution=CodeDependencyResolution.REMOTE_BUILD,
                    ),
                    environment_variables={
                        "FOUNDRY_PROJECT_ENDPOINT": endpoint,
                        "FOUNDRY_MODEL_NAME": model_name,
                        "AGENT_INSTRUCTIONS": (
                            "You are a helpful assistant that answers arithmetic questions. "
                            "Use the prior response context to resolve follow-up math questions like 'then + 10'."
                        ),
                    },
                    protocol_versions=[ProtocolVersionRecord(protocol="responses", version="2.0.0")],
                ),
                code=code_stream,
            )
        print(
            f"Hosted agent version created (id: {created_version.id}, name: {created_version.name}, "
            f"version: {created_version.version})"
        )

        for attempt in range(60):
            time.sleep(10)
            version_details = project_client.agents.get_version(
                agent_name=agent_name, agent_version=created_version.version
            )
            print(f"Hosted agent status: {version_details.status} (attempt {attempt + 1}/60)")
            if version_details.status == "active":
                break
            if version_details.status == "failed":
                raise RuntimeError(f"Hosted agent provisioning failed: {dict(version_details)}")
        else:
            raise RuntimeError("Timed out waiting for the hosted agent version to become active")

        ensure_agent_identity_rbac(
            agent=created_version,
            credential=credential,
            subscription_id=subscription_id,
            foundry_project_endpoint=endpoint,
        )

        original_agent_endpoint = project_client.agents.get(agent_name=agent_name).agent_endpoint
        endpoint_config = AgentEndpointConfig(
            version_selector=VersionSelector(
                version_selection_rules=[
                    FixedRatioVersionSelectionRule(agent_version=created_version.version, traffic_percentage=100),
                ]
            ),
            protocol_configuration=ProtocolConfiguration(responses=ResponsesProtocolConfiguration()),
        )
        project_client.agents.update_details(agent_name=agent_name, agent_endpoint=endpoint_config)
        print(f"Agent endpoint configured for version {created_version.version}")

        with project_client.get_openai_client(agent_name=agent_name) as openai_client:
            print("User 1 input: 1 + 1 = ?")
            response = openai_client.responses.create(
                input="1 + 1 = ?",
                extra_headers={"x-ms-user-identity": delegated_user_identity},
            )
            print(f"Agent: {response.output_text}")

            print(
                "User 2 input: then + 10.  Check out if the agent can continue the previous response chain from User 1."
            )
            try:
                openai_client.responses.create(
                    input="then + 10",
                    previous_response_id=response.id,
                    extra_headers={"x-ms-user-identity": delegated_user_identity_2},
                )
                print(f"Agent: {response.output_text}")
            except NotFoundError as e:
                print(
                    "Agent: Expected isolation behavior confirmed. "
                    "A different delegated user cannot continue the previous response chain and must start a new conversation."
                )

            print("User 1 input: then + 10")
            response = openai_client.responses.create(
                input="then + 10",
                previous_response_id=response.id,
                extra_headers={"x-ms-user-identity": delegated_user_identity},
            )
            print(f"Agent: {response.output_text}")
    finally:
        if original_agent_endpoint is not None:
            project_client.agents.update_details(agent_name=agent_name, agent_endpoint=original_agent_endpoint)
            print("Agent endpoint restored")

        if created_version is not None:
            project_client.agents.delete_version(
                agent_name=agent_name, agent_version=created_version.version, force=True
            )
            print(f"Hosted agent version {created_version.version} deleted")
