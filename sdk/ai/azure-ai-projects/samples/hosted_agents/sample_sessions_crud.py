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

    Sessions are no longer a preview feature. In stable releases, Sessions
    operations are accessed via the `project_client.agents` subclient.

USAGE:
    python sample_sessions_crud.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_HOSTED_AGENT_NAME - The name of an existing Hosted Agent.

    If you don't have a Hosted Agent, run `sample_create_hosted_agent.py` or
    `sample_create_hosted_agent_from_code.py` first to create one as a prerequisite.

SDK FUNCTIONS:
    - project_client.agents.list_versions: resolves the active version for the existing hosted agent.
    - project_client.agents.create_session: creates a session for the agent.
    - project_client.agents.get_session: retrieves a session by ID.
    - project_client.agents.list_sessions: lists sessions for an agent.
    - project_client.agents.delete_session: deletes a session by ID.
"""

import os

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import VersionRefIndicator

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ["FOUNDRY_HOSTED_AGENT_NAME"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=endpoint,
        credential=credential,
    ) as project_client,
):
    # Get the latest active version of the hosted agent
    agent = next(
        version
        for version in project_client.agents.list_versions(agent_name=agent_name, order="desc")
        if version.status == "active"
    )

    # Create a session for the hosted agent
    session = project_client.agents.create_session(
        agent_name=agent_name,
        version_indicator=VersionRefIndicator(agent_version=agent.version),
    )
    print(f"Created session (id: {session.agent_session_id}, status: {session.status})")

    # Retrieve the session by its ID
    fetched_session = project_client.agents.get_session(
        agent_name=agent_name,
        session_id=session.agent_session_id,
    )
    print(f"Retrieved session (id: {fetched_session.agent_session_id}, status: {fetched_session.status})")

    # List sessions for the agent
    print("Listing sessions for the agent...")
    sessions = project_client.agents.list_sessions(agent_name=agent_name)
    for item in sessions:
        print(f"  - Session ID: {item.agent_session_id}, Status: {item.status}")

    # Delete the session
    project_client.agents.delete_session(
        agent_name=agent_name,
        session_id=session.agent_session_id,
    )
    print(f"Deleted session (id: {session.agent_session_id})")