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

    Sessions are currently a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.agents`.

USAGE:
    python sample_sessions_crud.py

    Before running the sample:

    pip install "azure-ai-projects>=2.1.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_AGENT_CONTAINER_IMAGE - The Hosted Agent container image in the format '<registry>/<repository>[:<tag>|@<digest>]'

    You can build and push an example image from
    `samples/hosted_agents/assets/responses-echo-agent` and use that image value
    for `FOUNDRY_AGENT_CONTAINER_IMAGE`.
"""

import os

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import HostedAgentDefinition, VersionRefIndicator, ProtocolVersionRecord
from hosted_agents_util import wait_for_agent_version_active

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
image = os.environ["FOUNDRY_AGENT_CONTAINER_IMAGE"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=endpoint,
        credential=credential,
        allow_preview=True,
    ) as project_client,
):
    agent_name = "MySessionHostedAgent"

    # Create an agent version to back the session
    agent = project_client.agents.create_version(
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
    print(f"Agent created (name: {agent.name}, version: {agent.version})")

    wait_for_agent_version_active(
        project_client=project_client,
        agent_name=agent_name,
        agent_version=agent.version,
    )

    isolation_key = "sample-isolation-key"

    # Create a session for the agent
    print(f"Creating {3} sessions for the agent...")
    session = project_client.beta.agents.create_session(
        agent_name=agent_name,
        isolation_key=isolation_key,
        version_indicator=VersionRefIndicator(agent_version=agent.version),
    )
    print(f"Session created (id: {session.agent_session_id}, status: {session.status})")

    # Retrieve the session by its ID
    fetched = project_client.beta.agents.get_session(
        agent_name=agent_name,
        session_id=session.agent_session_id,
    )
    print(f"Retrieved session (id: {fetched.agent_session_id}, status: {fetched.status})")

    # List sessions for the agent
    print("Listing sessions for the agent...")
    sessions = project_client.beta.agents.list_sessions(agent_name=agent_name)
    print("Sessions:")
    for item in sessions:
        print(f"  - {item.agent_session_id} (status: {item.status})")

    # Delete the session
    print(f"Deleting session with id: {session.agent_session_id}...")
    project_client.beta.agents.delete_session(
        agent_name=agent_name,
        session_id=session.agent_session_id,
        isolation_key=isolation_key,
    )
    print(f"Session with id: {session.agent_session_id} deleted.")
