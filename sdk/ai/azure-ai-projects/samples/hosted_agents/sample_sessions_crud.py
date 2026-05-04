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
    2) FOUNDRY_HOSTED_AGENT_NAME - The name of an existing Hosted Agent.

    If you don't have a Hosted Agent, run `sample_hosted_agent_create.py` first
    to create one as a prerequisite.

SDK FUNCTIONS:
    - project_client.agents.list_versions: resolves the active version for the existing hosted agent.
    - project_client.beta.agents.create_session: creates a session for the agent.
    - project_client.beta.agents.get_session: retrieves a session by ID.
    - project_client.beta.agents.list_sessions: lists sessions for an agent.
    - project_client.beta.agents.delete_session: deletes a session by ID.
"""

import os

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import VersionRefIndicator
from hosted_agents_util import get_latest_active_agent_version

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ["FOUNDRY_HOSTED_AGENT_NAME"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=endpoint,
        credential=credential,
        allow_preview=True,
    ) as project_client,
):
    agent = get_latest_active_agent_version(project_client, agent_name)
    session = project_client.beta.agents.create_session(
        agent_name=agent_name,
        version_indicator=VersionRefIndicator(agent_version=agent.version),
    )
    print(f"Created session (id: {session.agent_session_id}, status: {session.status})")

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

    project_client.beta.agents.delete_session(
        agent_name=agent_name,
        session_id=session.agent_session_id,
    )
    print(f"Deleted session (id: {session.agent_session_id})")
