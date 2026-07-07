# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to perform CRUD operations on agent Sessions
    using the synchronous AIProjectClient.

    Sessions only work with Hosted Agents.

USAGE:
    python sample_sessions_crud.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model.
    3) FOUNDRY_HOSTED_AGENT_NAME - Optional. The Hosted Agent name. Defaults to
        `MyHostedAgent`.

SDK FUNCTIONS:
    - project_client.agents.create_version_from_code: creates a temporary hosted agent version.
    - project_client.agents.create_session: creates a session for the agent.
    - project_client.agents.get_session: retrieves a session by ID.
    - project_client.agents.list_sessions: lists sessions for an agent.
    - project_client.agents.delete_session: deletes a session by ID.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeConfiguration,
    CodeDependencyResolution,
    HostedAgentDefinition,
    ProtocolVersionRecord,
    VersionRefIndicator,
)
from hosted_agents_util import create_version_from_code
from util import zip_directory

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_HOSTED_AGENT_NAME", "MyHostedAgent")
model_name = os.environ["FOUNDRY_MODEL_NAME"]
hosted_agent_source_dir = Path(__file__).parent / "assets" / "basic-agent"

zip_path = zip_directory(hosted_agent_source_dir, "basic-agent.zip")[2]

with (
    zip_path.open("rb") as code_stream,
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=endpoint,
        credential=credential,
    ) as project_client,
    create_version_from_code(
        project_client=project_client,
        agent_name=agent_name,
        description="Sessions CRUD hosted agent uploaded from assets/basic-agent.",
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
            },
            protocol_versions=[ProtocolVersionRecord(protocol="responses", version="2.0.0")],
        ),
        code=code_stream,
    ) as created,
):
    session = project_client.agents.create_session(
        agent_name=agent_name,
        version_indicator=VersionRefIndicator(agent_version=created.version),
    )
    print(f"Created session (id: {session.agent_session_id}, status: {session.status})")

    # Retrieve the session by its ID
    fetched = project_client.agents.get_session(
        agent_name=agent_name,
        session_id=session.agent_session_id,
    )
    print(f"Retrieved session (id: {fetched.agent_session_id}, status: {fetched.status})")

    # List sessions for the agent
    print("Listing sessions for the agent...")
    sessions = project_client.agents.list_sessions(agent_name=agent_name)
    print("Sessions:")
    for item in sessions:
        print(f"  - {item.agent_session_id} (status: {item.status})")

    project_client.agents.delete_session(
        agent_name=agent_name,
        session_id=session.agent_session_id,
    )
    print(f"Deleted session (id: {session.agent_session_id})")
