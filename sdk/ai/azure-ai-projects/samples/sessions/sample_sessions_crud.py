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
"""

import logging
import os

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.core.pipeline.policies import HttpLoggingPolicy

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import HostedAgentDefinition, VersionRefIndicator, ProtocolVersionRecord

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
image = os.environ["FOUNDRY_AGENT_CONTAINER_IMAGE"]

# Construct the paths to the data folder and data file used in this sample
script_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(script_dir, "data_folder")
data_file = os.path.join(data_folder, "data_file1.txt")

# Allow specific query parameters to appear unredacted in logs.
# By default, HttpLoggingPolicy redacts all query params not in its allowlist.
http_logging_policy = HttpLoggingPolicy()
http_logging_policy.allowed_query_params.update({"limit", "after", "api-version", "path"})

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=endpoint,
        credential=credential,
        allow_preview=True,
        http_logging_policy=http_logging_policy,
    ) as project_client,
):
    logger.info(f"Connecting to project at endpoint: {endpoint}")
    agent_name = "MySessionHostedAgent3"

    # Create an agent version to back the session
    logger.info(f"Creating agent version '{agent_name}'...")
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
    logger.info(f"Agent created (name: {agent.name}, version: {agent.version})")
    print(f"Agent created (name: {agent.name}, version: {agent.version})")

    # Poll until agent version is active
    logger.info("Waiting for agent version to become active...")
    import time

    for attempt in range(60):
        time.sleep(10)
        version_details = project_client.agents.get_version(agent_name=agent_name, agent_version=agent.version)
        status = version_details["status"]
        logger.debug(f"Agent version status: {status} (attempt {attempt + 1}/{60})")
        print(f"Agent version status: {status} (attempt {attempt + 1})")
        if status == "active":
            logger.info("Agent version is now active")
            break
        if status == "failed":
            logger.error(f"Agent version provisioning failed: {dict(version_details)}")
            raise RuntimeError(f"Agent version provisioning failed: {dict(version_details)}")
    else:
        logger.error("Timed out waiting for agent version to become active")
        raise RuntimeError("Timed out waiting for agent version to become active")

    isolation_key = "sample-isolation-key"

    # Create a session for the agent
    logger.info(f"Creating {3} sessions for the agent...")
    session = project_client.beta.agents.create_session(
        agent_name=agent_name,
        isolation_key=isolation_key,
        version_indicator=VersionRefIndicator(agent_version=agent.version),
    )
    logger.info(f"Session created (id: {session.agent_session_id}, status: {session.status})")
    print(f"Session created (id: {session.agent_session_id}, status: {session.status})")

    # Retrieve the session by its ID
    fetched = project_client.beta.agents.get_session(
        agent_name=agent_name,
        session_id=session.agent_session_id,
    )
    print(f"Retrieved session (id: {fetched.agent_session_id}, status: {fetched.status})")

    # List sessions for the agent
    logger.info("Listing sessions for the agent...")
    sessions = project_client.beta.agents.list_sessions(agent_name=agent_name)
    logger.info("Sessions:")
    for item in sessions:
        logger.info(f"  - {item.agent_session_id} (status: {item.status})")
        print(f"  - {item.agent_session_id} (status: {item.status})")

    # Delete file
    logger.info(f"Deleting session file at path: {data_file}...")
    project_client.beta.agents.delete_session_file(
        agent_name=agent_name,
        session_id=session.agent_session_id,
        path=data_file,
    )
    # Delete the session
    logger.info(f"Deleting session with id: {session.agent_session_id}...")
    project_client.beta.agents.delete_session(
        agent_name=agent_name,
        session_id=session.agent_session_id,
        isolation_key=isolation_key,
    )
    logger.info(f"Session with id: {session.agent_session_id} deleted.")