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
    python sample_sessions_files_upload_download.py

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
from hosted_agents_util import create_agent_and_session

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
image = os.environ["FOUNDRY_AGENT_CONTAINER_IMAGE"]

# Construct the paths to the data folder and data file used in this sample
script_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(script_dir, "assets")
data_file1 = os.path.join(data_folder, "data_file1.txt")
data_file2 = os.path.join(data_folder, "data_file2.txt")
remote_file_path1 = "/remote/data_file1.txt"
remote_file_path2 = "/remote/data_file2.txt"


with (
    DefaultAzureCredential() as credential,
    AIProjectClient(
        endpoint=endpoint,
        credential=credential,
        allow_preview=True,
    ) as project_client,
):
    agent_name = "MySessionHostedAgent"

    with create_agent_and_session(project_client, agent_name, image) as (_, session):

        # Upload and list session files
        project_client.beta.agents.upload_session_file(
            agent_name=agent_name,
            session_id=session.agent_session_id,
            content_or_file_path=data_file1,
            path=remote_file_path1,
        )

        print(f"Uploading session file: {data_file2} -> {remote_file_path2}")
        project_client.beta.agents.upload_session_file(
            agent_name=agent_name,
            session_id=session.agent_session_id,
            content_or_file_path=data_file2,
            path=remote_file_path2,
        )

        print("Listing session files for the session at path '.'...")
        files = project_client.beta.agents.get_session_files(
            agent_name=agent_name,
            session_id=session.agent_session_id,
            path="/remote",
        )
        for entry in files.entries:
            print(f"  - name={entry.name}, size={entry.size}, is_directory={entry.is_directory}")

        print(f"Downloading and printing content from '{remote_file_path1}'")
        content_bytes = b"".join(
            project_client.beta.agents.download_session_file(
                agent_name=agent_name,
                session_id=session.agent_session_id,
                path=remote_file_path1,
            )
        )
        file_content = content_bytes.decode("utf-8", errors="replace")
        print(f"Session file content ({remote_file_path1}):\n{file_content}")

        print(f"Deleting session file at path: {remote_file_path1}...")
        project_client.beta.agents.delete_session_file(
            agent_name=agent_name,
            session_id=session.agent_session_id,
            path=remote_file_path1,
        )

        print(f"Deleting session file at path: {remote_file_path2}...")
        project_client.beta.agents.delete_session_file(
            agent_name=agent_name,
            session_id=session.agent_session_id,
            path=remote_file_path2,
        )
