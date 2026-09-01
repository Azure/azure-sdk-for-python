# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable
import os
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy
from azure.ai.projects.models import VersionRefIndicator


class TestAgentSessionFilesCrud(TestBase):
    """
    Test CRUD operations for Agent Session Files.

    These tests require a Hosted Agent to be deployed and available.
    Sessions only work with Hosted Agents.

    Prerequisites:
    - A Hosted Agent must be deployed and active.
    - Environment variable FOUNDRY_HOSTED_AGENT_NAME must be set.
    """

    def _get_latest_active_agent_version(self, project_client, agent_name):
        """Get the latest active agent version for a hosted agent."""
        for version in project_client.agents.list_versions(agent_name=agent_name, order="desc"):
            if version.status == "active":
                return version
        raise RuntimeError(
            f"No active version found for hosted agent '{agent_name}'. "
            "Create or activate a version before running this test."
        )

    # To run this test:
    # pytest tests\sessions\test_agent_session_files_crud.py::TestAgentSessionFilesCrud::test_agent_session_files_crud -s
    @servicePreparer()
    @recorded_by_proxy()
    def test_agent_session_files_crud(self, **kwargs):
        """
        Test CRUD operations for Agent Session Files.

        This test:
        1. Creates a session for a hosted agent
        2. Uploads two files to the session
        3. Lists files in the session and verifies the uploaded files are present
        4. Downloads a file and verifies its content
        5. Deletes both files
        6. Cleans up by deleting the session

        Routes used in this test:

        Action  REST API Route                                                               Client Method
        ------+---------------------------------------------------------------------------+-------------------------------------------
        POST    /agents/{agent_name}/sessions                                               project_client.agents.create_session()
        POST    /agents/{agent_name}/sessions/{session_id}/files:upload                     project_client.agents.upload_session_file()
        GET     /agents/{agent_name}/sessions/{session_id}/files                            project_client.agents.list_session_files()
        GET     /agents/{agent_name}/sessions/{session_id}/files:download                   project_client.agents.download_session_file_as_bytes()
        DELETE  /agents/{agent_name}/sessions/{session_id}/files                            project_client.agents.delete_session_file()
        DELETE  /agents/{agent_name}/sessions/{session_id}                                  project_client.agents.delete_session()
        """
        print("\n")

        agent_name = kwargs["foundry_hosted_agent_name"]
        project_client = self.create_client(**kwargs)

        # Construct paths to test data files
        test_dir = os.path.dirname(os.path.abspath(__file__))
        test_data_folder = os.path.join(test_dir, "..", "test_data", "sessions")

        # Define test files: (local_path, remote_path, expected_content)
        test_files = [
            (os.path.join(test_data_folder, "data_file1.txt"), "/remote/data_file1.txt", "This is sample file 1"),
            (os.path.join(test_data_folder, "data_file2.txt"), "/remote/data_file2.txt", "This is sample file 2"),
            (os.path.join(test_data_folder, "data_file3.txt"), "/remote/data_file3.txt", "This is sample file 3"),
        ]

        # Verify test data files exist
        for local_path, _, _ in test_files:
            assert os.path.exists(local_path), f"Test data file not found: {local_path}"

        # Get the latest active agent version
        agent = self._get_latest_active_agent_version(project_client, agent_name)
        assert agent is not None, "Failed to get agent version"
        assert agent.version is not None, "Agent version should not be None"
        print(f"Using agent: {agent_name}, version: {agent.version}")

        # Create a session
        session = project_client.agents.create_session(
            agent_name=agent_name,
            version_indicator=VersionRefIndicator(agent_version=agent.version),
        )
        assert session is not None, "Session creation returned None"
        assert session.agent_session_id is not None, "Session ID should not be None"
        assert session.status is not None, "Session status should not be None"
        print(f"Session created (id: {session.agent_session_id}, status: {session.status})")

        try:
            # Upload all files
            for local_path, remote_path, _ in test_files:
                print(f"Uploading session file: {local_path} -> {remote_path}")
                with open(local_path, "rb") as f:
                    content = f.read()
                project_client.agents.upload_session_file(
                    agent_name=agent_name,
                    session_id=session.agent_session_id,
                    content=content,
                    path=remote_path,
                )
                print(f"Successfully uploaded file to {remote_path}")

            # --------------------------------------------------------------------------------------------------

            # List session files and verify uploaded files are present
            print("Listing session files at path '/remote'...")
            files = project_client.agents.list_session_files(
                agent_name=agent_name,
                session_id=session.agent_session_id,
                path="/remote",
            )

            # Convert to list for verification
            files_list = list(files)
            assert len(files_list) >= 3, f"Expected at least 3 files, got {len(files_list)}"

            # Verify file entries
            file_names = [entry.name for entry in files_list]
            print(f"Files found: {file_names}")
            for local_path, _, _ in test_files:
                expected_name = os.path.basename(local_path)
                assert expected_name in file_names, f"{expected_name} not found in listed files"

            # Verify file properties
            for entry in files_list:
                print(f"  - name={entry.name}, size={entry.size}, is_directory={entry.is_directory}")
                assert entry.name is not None, "File name should not be None"
                assert entry.size is not None, "File size should not be None"
                assert entry.is_directory is not None, "is_directory should not be None"

            # --------------------------------------------------------------------------------------------------

            # Download and verify content of all files
            for _, remote_path, expected_content in test_files:
                print(f"Downloading and verifying content from '{remote_path}'")
                content_bytes = b"".join(
                    project_client.agents.download_session_file(
                        agent_name=agent_name,
                        session_id=session.agent_session_id,
                        path=remote_path,
                    )
                )
                assert content_bytes is not None, "Downloaded content should not be None"
                assert len(content_bytes) > 0, "Downloaded content should not be empty"

                file_content = content_bytes.decode("utf-8", errors="replace")
                print(f"Downloaded content: {file_content.strip()}")

                assert (
                    expected_content in file_content
                ), f"Expected content '{expected_content}' not found in downloaded file"
                print("Content verification passed!")

            # --------------------------------------------------------------------------------------------------

            # Delete all files
            for _, remote_path, _ in test_files:
                print(f"Deleting session file at path: {remote_path}...")
                project_client.agents.delete_session_file(
                    agent_name=agent_name,
                    session_id=session.agent_session_id,
                    path=remote_path,
                )
                print(f"Successfully deleted {remote_path}")

            print("All session file CRUD operations completed successfully!")

        finally:
            # Clean up: delete the session
            project_client.agents.delete_session(
                agent_name=agent_name,
                session_id=session.agent_session_id,
            )
            print(f"Session deleted (id: {session.agent_session_id})")
