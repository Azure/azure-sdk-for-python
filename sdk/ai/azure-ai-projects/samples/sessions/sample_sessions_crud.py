# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to perform CRUD operations on agent Sessions
    using the synchronous AIProjectClient.

    Sessions are currently a preview feature. In the Python SDK, you access
    these operations via `project_client.beta.agents`.

USAGE:
    python sample_session_crud.py

    Before running the sample:

    pip install "azure-ai-projects>=2.1.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import HostedAgentDefinition, VersionRefIndicator, ProtocolVersionRecord

import uuid

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]
image = os.environ["FOUNDRY_AGENT_IMAGE"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential, api_version="2025-11-15-preview") as project_client,
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
                ProtocolVersionRecord(protocol="responses", version="v1"),
            ],
        ),
        metadata={"enableVnextExperience": "true"},
    )
    print(f"Agent created (name: {agent.name}, version: {agent.version})")

    # Poll until agent version is active
    import time
    for attempt in range(60):
        time.sleep(10)
        version_details = project_client.agents.get_version(
            agent_name=agent_name, agent_version=agent.version
        )
        status = version_details["status"]
        print(f"Agent version status: {status} (attempt {attempt + 1})")
        if status == "active":
            break
        if status == "failed":
            raise RuntimeError(f"Agent version provisioning failed: {dict(version_details)}")
    else:
        raise RuntimeError("Timed out waiting for agent version to become active")

    isolation_key = "sample-isolation-key"
    session_id = uuid.uuid4().hex[:16]

    # Create a session for the agent
    session = project_client.beta.agents.create_session(
        agent_name=agent_name,
        isolation_key=isolation_key,
        agent_session_id=session_id,
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
    sessions = project_client.beta.agents.list_sessions(agent_name=agent_name, limit=5)
    for item in sessions:
        print(f"  - {item.agent_session_id} (status: {item.status})")

    # Delete the session
    project_client.beta.agents.delete_session(
        agent_name=agent_name,
        session_id=session.agent_session_id,
        isolation_key=isolation_key,
    )
    print("Session deleted")

    # Clean up: delete the agent version
    project_client.agents.delete_version(agent_name=agent_name, agent_version=agent.version)
    print("Agent deleted")
