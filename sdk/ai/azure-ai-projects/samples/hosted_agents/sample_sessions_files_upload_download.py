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
    python sample_sessions_files_upload_download.py

    Before running the sample:

    pip install "azure-ai-projects>=2.3.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model.
    3) FOUNDRY_HOSTED_AGENT_NAME - Optional. The Hosted Agent name. Defaults to
        `MyHostedAgent`.
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

# Construct the paths to the data folder and data file used in this sample
script_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(script_dir, "assets")
data_file1 = os.path.join(data_folder, "data_file1.txt")
data_file2 = os.path.join(data_folder, "data_file2.txt")
remote_file_path1 = "/remote/data_file1.txt"
remote_file_path2 = "/remote/data_file2.txt"


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
        description="Session files hosted agent uploaded from assets/basic-agent.",
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
    print(f"Session created (id: {session.agent_session_id}, status: {session.status})")
    try:
        print(f"Uploading session file: {data_file1} -> {remote_file_path1}")
        with open(data_file1, "rb") as f:
            content1 = f.read()
        project_client.agents.upload_session_file(
            agent_name=agent_name,
            session_id=session.agent_session_id,
            content=content1,
            path=remote_file_path1,
        )

        print(f"Uploading session file: {data_file2} -> {remote_file_path2}")
        with open(data_file2, "rb") as f:
            content2 = f.read()
        project_client.agents.upload_session_file(
            agent_name=agent_name,
            session_id=session.agent_session_id,
            content=content2,
            path=remote_file_path2,
        )

        print("Listing session files for the session at path '.'...")
        files = project_client.agents.list_session_files(
            agent_name=agent_name,
            session_id=session.agent_session_id,
            path="/remote",
        )
        for entry in files:
            print(f"  - name={entry.name}, size={entry.size}, is_directory={entry.is_directory}")

        print(f"Downloading and printing content from '{remote_file_path1}'")
        content_bytes = b"".join(
            project_client.agents.download_session_file(
                agent_name=agent_name,
                session_id=session.agent_session_id,
                path=remote_file_path1,
            )
        )
        file_content = content_bytes.decode("utf-8", errors="replace")
        print(f"Session file content ({remote_file_path1}):\n{file_content}")

        print(f"Deleting session file at path: {remote_file_path1}...")
        project_client.agents.delete_session_file(
            agent_name=agent_name,
            session_id=session.agent_session_id,
            path=remote_file_path1,
        )

        print(f"Deleting session file at path: {remote_file_path2}...")
        project_client.agents.delete_session_file(
            agent_name=agent_name,
            session_id=session.agent_session_id,
            path=remote_file_path2,
        )
    finally:
        project_client.agents.delete_session(
            agent_name=agent_name,
            session_id=session.agent_session_id,
        )
        print(f"Session deleted (id: {session.agent_session_id})")
