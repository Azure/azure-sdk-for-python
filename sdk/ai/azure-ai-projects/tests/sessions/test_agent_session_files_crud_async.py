# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable
import os
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async
from azure.ai.projects.models import VersionRefIndicator


class TestAgentSessionFilesCrudAsync(TestBase):
    """
    Test CRUD operations for Agent Session Files (Async).

    These tests require a Hosted Agent to be deployed and available.
    Sessions only work with Hosted Agents.

    Prerequisites:
    - A Hosted Agent must be deployed and active.
    - Environment variable FOUNDRY_HOSTED_AGENT_NAME must be set.
    """

    async def _get_latest_active_agent_version_async(self, project_client, agent_name):
        """Get the latest active agent version for a hosted agent (async)."""
        async for version in project_client.agents.list_versions(agent_name=agent_name, order="desc"):
            if version.status == "active":
                return version
        raise RuntimeError(
            f"No active version found for hosted agent '{agent_name}'. "
            "Create or activate a version before running this test."
        )

    # To run this test:
    # pytest tests\sessions\test_agent_session_files_crud_async.py::TestAgentSessionFilesCrudAsync::test_agent_session_files_crud_async -s
    @servicePreparer()
    @recorded_by_proxy_async()
    async def test_agent_session_files_crud_async(self, **kwargs):
        """
        Test CRUD operations for Agent Session Files (Async).

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
        project_client = self.create_async_client(**kwargs)

        # Construct paths to test data files
        test_dir = os.path.dirname(os.path.abspath(__file__))
        test_data_folder = os.path.join(test_dir, "..", "test_data", "sessions")
        data_file1 = os.path.join(test_data_folder, "data_file1.txt")
        data_file2 = os.path.join(test_data_folder, "data_file2.txt")
        data_file3 = os.path.join(test_data_folder, "data_file3.txt")
        remote_file_path1 = "/remote/data_file1.txt"
        remote_file_path2 = "/remote/data_file2.txt"
        remote_file_path3 = "/remote/data_file3.txt"

        # Verify test data files exist
        assert os.path.exists(data_file1), f"Test data file not found: {data_file1}"
        assert os.path.exists(data_file2), f"Test data file not found: {data_file2}"
        assert os.path.exists(data_file3), f"Test data file not found: {data_file3}"

        async with project_client:
            # Get the latest active agent version
            agent = await self._get_latest_active_agent_version_async(project_client, agent_name)
            assert agent is not None, "Failed to get agent version"
            assert agent.version is not None, "Agent version should not be None"
            print(f"Using agent: {agent_name}, version: {agent.version}")

            # Create a session
            session = await project_client.agents.create_session(
                agent_name=agent_name,
                version_indicator=VersionRefIndicator(agent_version=agent.version),
            )
            assert session is not None, "Session creation returned None"
            assert session.agent_session_id is not None, "Session ID should not be None"
            assert session.status is not None, "Session status should not be None"
            print(f"Session created (id: {session.agent_session_id}, status: {session.status})")

            # --------------------------------------------------------------------------------------------------

            try:
                # Upload first file
                print(f"Uploading session file: {data_file1} -> {remote_file_path1}")
                with open(data_file1, "rb") as f:
                    file1_content = f.read()
                await project_client.agents.upload_session_file(
                    agent_name=agent_name,
                    agent_session_id=session.agent_session_id,
                    content=file1_content,
                    remote_path=remote_file_path1,
                )
                print(f"Successfully uploaded file to {remote_file_path1}")

                # Upload second file
                print(f"Uploading session file: {data_file2} -> {remote_file_path2}")
                with open(data_file2, "rb") as f:
                    file2_content = f.read()
                await project_client.agents.upload_session_file(
                    agent_name=agent_name,
                    agent_session_id=session.agent_session_id,
                    content=file2_content,
                    remote_path=remote_file_path2,
                )
                print(f"Successfully uploaded file to {remote_file_path2}")

                # Upload third file
                print(f"Uploading session file: {data_file3} -> {remote_file_path3}")
                with open(data_file3, "rb") as f:
                    file3_content = f.read()
                await project_client.agents.upload_session_file(
                    agent_name=agent_name,
                    agent_session_id=session.agent_session_id,
                    content=file3_content,
                    remote_path=remote_file_path3,
                )
                print(f"Successfully uploaded file to {remote_file_path3}")

                # --------------------------------------------------------------------------------------------------

                # List session files and verify uploaded files are present
                print("Listing session files at path '/remote'...")
                files_list = []
                async for entry in project_client.agents.list_session_files(
                    agent_name=agent_name,
                    agent_session_id=session.agent_session_id,
                    remote_path="/remote",
                ):
                    files_list.append(entry)

                assert len(files_list) >= 3, f"Expected at least 3 files, got {len(files_list)}"

                # Verify file entries
                file_names = [entry.name for entry in files_list]
                print(f"Files found: {file_names}")
                assert "data_file1.txt" in file_names, "data_file1.txt not found in listed files"
                assert "data_file2.txt" in file_names, "data_file2.txt not found in listed files"
                assert "data_file3.txt" in file_names, "data_file3.txt not found in listed files"

                # Verify file properties
                for entry in files_list:
                    print(f"  - name={entry.name}, size={entry.size}, is_directory={entry.is_directory}")
                    assert entry.name is not None, "File name should not be None"
                    assert entry.size is not None, "File size should not be None"
                    assert entry.is_directory is not None, "is_directory should not be None"

                # --------------------------------------------------------------------------------------------------

                # Download and verify content of first file
                print(f"Downloading and verifying content from '{remote_file_path1}'")
                content_chunks = []
                download_iterator = await project_client.agents.download_session_file(
                    agent_name=agent_name,
                    agent_session_id=session.agent_session_id,
                    remote_path=remote_file_path1,
                )
                async for chunk in download_iterator:
                    content_chunks.append(chunk)
                content_bytes = b"".join(content_chunks)

                assert content_bytes is not None, "Downloaded content should not be None"
                assert len(content_bytes) > 0, "Downloaded content should not be empty"

                file_content = content_bytes.decode("utf-8", errors="replace")
                print(f"Downloaded content: {file_content.strip()}")

                # Verify content matches expected
                expected_content = "This is sample file 1"
                assert (
                    expected_content in file_content
                ), f"Expected content '{expected_content}' not found in downloaded file"
                print("Content verification passed!")

                # Download and verify content of second file
                print(f"Downloading and verifying content from '{remote_file_path2}'")
                content_chunks = []
                download_iterator = await project_client.agents.download_session_file(
                    agent_name=agent_name,
                    agent_session_id=session.agent_session_id,
                    remote_path=remote_file_path2,
                )
                async for chunk in download_iterator:
                    content_chunks.append(chunk)
                content_bytes = b"".join(content_chunks)

                assert content_bytes is not None, "Downloaded content should not be None"
                assert len(content_bytes) > 0, "Downloaded content should not be empty"

                file_content = content_bytes.decode("utf-8", errors="replace")
                print(f"Downloaded content: {file_content.strip()}")

                # Verify content matches expected
                expected_content = "This is sample file 2"
                assert (
                    expected_content in file_content
                ), f"Expected content '{expected_content}' not found in downloaded file"
                print("Content verification passed!")

                # Download and verify content of third file
                print(f"Downloading and verifying content from '{remote_file_path3}'")
                content_chunks = []
                download_iterator = await project_client.agents.download_session_file(
                    agent_name=agent_name,
                    agent_session_id=session.agent_session_id,
                    remote_path=remote_file_path3,
                )
                async for chunk in download_iterator:
                    content_chunks.append(chunk)
                content_bytes = b"".join(content_chunks)

                assert content_bytes is not None, "Downloaded content should not be None"
                assert len(content_bytes) > 0, "Downloaded content should not be empty"

                file_content = content_bytes.decode("utf-8", errors="replace")
                print(f"Downloaded content: {file_content.strip()}")

                # Verify content matches expected
                expected_content = "This is sample file 3"
                assert (
                    expected_content in file_content
                ), f"Expected content '{expected_content}' not found in downloaded file"
                print("Content verification passed!")

                # --------------------------------------------------------------------------------------------------

                # Delete first file
                print(f"Deleting session file at path: {remote_file_path1}...")
                await project_client.agents.delete_session_file(
                    agent_name=agent_name,
                    agent_session_id=session.agent_session_id,
                    remote_path=remote_file_path1,
                )
                print(f"Successfully deleted {remote_file_path1}")

                # Delete second file
                print(f"Deleting session file at path: {remote_file_path2}...")
                await project_client.agents.delete_session_file(
                    agent_name=agent_name,
                    agent_session_id=session.agent_session_id,
                    remote_path=remote_file_path2,
                )
                print(f"Successfully deleted {remote_file_path2}")

                # Delete third file
                print(f"Deleting session file at path: {remote_file_path3}...")
                await project_client.agents.delete_session_file(
                    agent_name=agent_name,
                    agent_session_id=session.agent_session_id,
                    remote_path=remote_file_path3,
                )
                print(f"Successfully deleted {remote_file_path3}")

                print("All session file CRUD operations completed successfully!")

            finally:
                # Clean up: delete the session
                await project_client.agents.delete_session(
                    agent_name=agent_name,
                    session_id=session.agent_session_id,
                )
                print(f"Session deleted (id: {session.agent_session_id})")
