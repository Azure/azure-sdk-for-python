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
     3) FOUNDRY_PROJECTS_AZURE_SUBSCRIPTION_ID - Azure subscription ID where the
         Azure AI account and project are deployed.

    You can build and push an example image from
    `samples/hosted_agents/assets/responses-echo-agent` and use that image value
    for `FOUNDRY_AGENT_CONTAINER_IMAGE`.

SDK FUNCTIONS:
    - project_client.agents.create_version: creates an agent version (via create_agent context manager).
    - ensure_agent_identity_rbac: sets up RBAC for the agent's managed identity (context manager).
    - project_client.beta.agents.create_session: creates a session for the agent (via create_session context manager).
    - project_client.beta.agents.get_session: retrieves a session by ID.
    - project_client.beta.agents.list_sessions: lists sessions for an agent.

CLEANUP FUNCTIONS (called on context manager exit in reverse order):
    - project_client.beta.agents.delete_session: deletes the session.
    - authorization_client.role_assignments.delete: removes the RBAC role assignment (only if this sample created it).
    - project_client.agents.delete_version: deletes the agent version.
"""

import os

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from hosted_agents_util import create_agent, create_session
from rbac_util import ensure_agent_identity_rbac

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
image = os.environ["FOUNDRY_AGENT_CONTAINER_IMAGE"]
subscription_id = os.environ["FOUNDRY_PROJECTS_AZURE_SUBSCRIPTION_ID"]
agent_name = "MySessionHostedAgent"
isolation_key = "sample-isolation-key"

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=endpoint,
        credential=credential,
        allow_preview=True,
    ) as project_client,
    create_agent(project_client, agent_name, image) as agent,
    ensure_agent_identity_rbac(
        agent=agent,
        credential=credential,
        subscription_id=subscription_id,
        foundry_project_endpoint=endpoint,
    ),
    create_session(project_client, agent_name, agent.version, isolation_key=isolation_key) as session,
):
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
