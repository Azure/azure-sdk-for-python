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
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, VersionRefIndicator

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_name = os.environ["FOUNDRY_MODEL_NAME"]

# Construct the paths to the data folder and data file used in this sample
script_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(script_dir, "data_folder")
data_file = os.path.join(data_folder, "data_file1.txt")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    agent_name = "MySessionAgent"

    # Create an agent version to back the session
    agent = project_client.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=model_name,
            instructions="You are a helpful assistant.",
        ),
    )
    print(f"Agent created (name: {agent.name}, version: {agent.version})")

    isolation_key = "sample-isolation-key"

    # Create a session for the agent
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
    sessions = list(project_client.beta.agents.list_sessions(agent_name=agent_name))
    print(f"Found {len(sessions)} session(s) for agent '{agent_name}'")
    for item in sessions:
        print(f"  - {item.agent_session_id} (status: {item.status})")

    print(f"Uploading file {data_file} to the session")
    project_client.beta.agents.upload_session_file(
        agent_name=agent_name,
        session_id=session.agent_session_id,
        content_or_file_path=data_file,
        path="data_file1.txt",
    )
    print("Session file uploaded")

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
