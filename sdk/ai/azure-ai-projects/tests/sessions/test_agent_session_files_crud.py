# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable
import os
import tempfile
from pathlib import Path
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
            # Upload first file using file_path (str)
            print(f"Uploading session file: {data_file1} -> {remote_file_path1}")
            project_client.agents.upload_session_file(
                agent_name=agent_name,
                session_id=session.agent_session_id,
                file_path=data_file1,
                remote_path=remote_file_path1,
            )
            print(f"Successfully uploaded file to {remote_file_path1}")

            # Upload second file using file_path (PathLike[str])
            print(f"Uploading session file using PathLike: {data_file2} -> {remote_file_path2}")
            project_client.agents.upload_session_file(
                agent_name=agent_name,
                session_id=session.agent_session_id,
                file_path=Path(data_file2),
                remote_path=remote_file_path2,
            )
            print(f"Successfully uploaded file to {remote_file_path2}")

            # Upload third file using content (bytes)
            print(f"Uploading session file using content: {data_file3} -> {remote_file_path3}")
            with open(data_file3, "rb") as f:
                file3_content = f.read()
            project_client.agents.upload_session_file(
                agent_name=agent_name,
                session_id=session.agent_session_id,
                content=file3_content,
                remote_path=remote_file_path3,
            )
            print(f"Successfully uploaded file to {remote_file_path3}")

            # List session files and verify uploaded files are present
            print("Listing session files at path '/remote'...")
            files = project_client.agents.list_session_files(
                agent_name=agent_name,
                agent_session_id=session.agent_session_id,
                remote_path="/remote",
            )

            # Convert to list for verification
            files_list = list(files)
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
            content_bytes = b"".join(
                project_client.agents.download_session_file_as_bytes(
                    agent_name=agent_name,
                    agent_session_id=session.agent_session_id,
                    remote_path=remote_file_path1,
                )
            )
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

            # Download second file to disk using download_session_file_to_path with str file_path
            temp_dir = tempfile.gettempdir()
            download_path = os.path.join(temp_dir, "downloaded_data_file2_sync_test.txt")
            print(f"Downloading session file to disk: {remote_file_path2} -> {download_path}")

            project_client.agents.download_session_file_to_path(
                agent_name=agent_name,
                session_id=session.agent_session_id,
                file_path=download_path,  # str type
                remote_path=remote_file_path2,
                overwrite=True,
            )
            print(f"Successfully downloaded file to {download_path}")

            # Verify the downloaded file exists and has expected content
            assert os.path.exists(download_path), f"Downloaded file not found: {download_path}"
            with open(download_path, "r", encoding="utf-8") as f:
                downloaded_content = f.read()

            print(f"Downloaded content from disk: {downloaded_content.strip()}")
            expected_content2 = "This is sample file 2"
            assert (
                expected_content2 in downloaded_content
            ), f"Expected content '{expected_content2}' not found in downloaded file"
            print("download_session_file_to_path content verification passed!")

            # Clean up local temp file
            if os.path.exists(download_path):
                os.remove(download_path)
                print(f"Cleaned up temp file: {download_path}")

            # --------------------------------------------------------------------------------------------------

            # Download third file to disk using download_session_file_to_path with PathLike file_path
            download_path3 = Path(tempfile.gettempdir()) / "downloaded_data_file3_sync_test.txt"
            print(f"Downloading session file to disk using PathLike: {remote_file_path3} -> {download_path3}")

            project_client.agents.download_session_file_to_path(
                agent_name=agent_name,
                session_id=session.agent_session_id,
                file_path=download_path3,  # PathLike[str] type
                remote_path=remote_file_path3,
                overwrite=True,
            )
            print(f"Successfully downloaded file to {download_path3}")

            # Verify the downloaded file exists and has expected content
            assert download_path3.exists(), f"Downloaded file not found: {download_path3}"
            with open(download_path3, "r", encoding="utf-8") as f:
                downloaded_content3 = f.read()

            print(f"Downloaded content from disk: {downloaded_content3.strip()}")
            expected_content3 = "This is sample file 3"
            assert (
                expected_content3 in downloaded_content3
            ), f"Expected content '{expected_content3}' not found in downloaded file"
            print("download_session_file_to_path with PathLike content verification passed!")

            # Clean up local temp file
            if download_path3.exists():
                download_path3.unlink()
                print(f"Cleaned up temp file: {download_path3}")

            # Delete first file
            print(f"Deleting session file at path: {remote_file_path1}...")
            project_client.agents.delete_session_file(
                agent_name=agent_name,
                agent_session_id=session.agent_session_id,
                remote_path=remote_file_path1,
            )
            print(f"Successfully deleted {remote_file_path1}")

            # Delete second file
            print(f"Deleting session file at path: {remote_file_path2}...")
            project_client.agents.delete_session_file(
                agent_name=agent_name,
                agent_session_id=session.agent_session_id,
                remote_path=remote_file_path2,
            )
            print(f"Successfully deleted {remote_file_path2}")

            # Delete third file
            print(f"Deleting session file at path: {remote_file_path3}...")
            project_client.agents.delete_session_file(
                agent_name=agent_name,
                agent_session_id=session.agent_session_id,
                remote_path=remote_file_path3,
            )
            print(f"Successfully deleted {remote_file_path3}")

            print("All session file CRUD operations completed successfully!")

        finally:
            # Clean up: delete the session
            project_client.agents.delete_session(
                agent_name=agent_name,
                session_id=session.agent_session_id,
            )
            print(f"Session deleted (id: {session.agent_session_id})")

    # To run this test:
    # pytest tests\sessions\test_agent_session_files_crud.py::TestAgentSessionFilesCrud::test_agent_session_files_invalid_input -s
    # These are unit-tests that do not make network calls.
    @servicePreparer()
    def test_agent_session_files_invalid_input(self, **kwargs):
        """
        Test that upload_session_file and download_session_file_to_path raise appropriate
        errors when given invalid input (non-existing files, folder paths).

        These are client-side validations that occur before any API call is made.
        """
        print("\n")

        foundry_project_endpoint = "https://fake-endpoint"
        agent_name = "fake-agent-name"
        session_id = "fake-session-id"

        project_client = self.create_client(agent_name=agent_name, foundry_project_endpoint=foundry_project_endpoint)

        try:
            # --------------------------------------------------------------------------------------------------
            # Test upload_session_file with invalid inputs
            # --------------------------------------------------------------------------------------------------

            # Test that upload_session_file raises FileNotFoundError when file_path is a non-existing file (str type)
            non_existing_file_str = os.path.join(tempfile.gettempdir(), "non_existing_file_12345.txt")
            print(f"Testing upload_session_file with non-existing file (str): {non_existing_file_str}")
            try:
                project_client.agents.upload_session_file(
                    agent_name=agent_name,
                    session_id=session_id,
                    file_path=non_existing_file_str,  # str type pointing to non-existing file
                    remote_path="/remote/non_existing.txt",
                )
                assert False, "Expected FileNotFoundError when file_path is a non-existing file (str type)"
            except FileNotFoundError as e:
                print(f"Got expected FileNotFoundError for non-existing file (str): {e}")
                assert "does not exist" in str(e).lower(), f"Error message should mention 'does not exist': {e}"

            # Test that upload_session_file raises FileNotFoundError when file_path is a non-existing file (PathLike type)
            non_existing_file_pathlike = Path(tempfile.gettempdir()) / "non_existing_file_12345.txt"
            print(f"Testing upload_session_file with non-existing file (PathLike): {non_existing_file_pathlike}")
            try:
                project_client.agents.upload_session_file(
                    agent_name=agent_name,
                    session_id=session_id,
                    file_path=non_existing_file_pathlike,  # PathLike[str] type pointing to non-existing file
                    remote_path="/remote/non_existing.txt",
                )
                assert False, "Expected FileNotFoundError when file_path is a non-existing file (PathLike type)"
            except FileNotFoundError as e:
                print(f"Got expected FileNotFoundError for non-existing file (PathLike): {e}")
                assert "does not exist" in str(e).lower(), f"Error message should mention 'does not exist': {e}"

            # Test that upload_session_file raises ValueError when file_path is a folder (str type)
            upload_folder_path_str = tempfile.gettempdir()  # This is a folder, not a file
            print(f"Testing upload_session_file with folder path (str): {upload_folder_path_str}")
            try:
                project_client.agents.upload_session_file(
                    agent_name=agent_name,
                    session_id=session_id,
                    file_path=upload_folder_path_str,  # str type pointing to a folder
                    remote_path="/remote/folder_upload.txt",
                )
                assert False, "Expected ValueError when file_path is a folder (str type)"
            except ValueError as e:
                print(f"Got expected ValueError for folder path (str): {e}")
                assert "folder" in str(e).lower(), f"Error message should mention 'folder': {e}"

            # Test that upload_session_file raises ValueError when file_path is a folder (PathLike type)
            upload_folder_path_pathlike = Path(tempfile.gettempdir())  # This is a folder, not a file
            print(f"Testing upload_session_file with folder path (PathLike): {upload_folder_path_pathlike}")
            try:
                project_client.agents.upload_session_file(
                    agent_name=agent_name,
                    session_id=session_id,
                    file_path=upload_folder_path_pathlike,  # PathLike[str] type pointing to a folder
                    remote_path="/remote/folder_upload.txt",
                )
                assert False, "Expected ValueError when file_path is a folder (PathLike type)"
            except ValueError as e:
                print(f"Got expected ValueError for folder path (PathLike): {e}")
                assert "folder" in str(e).lower(), f"Error message should mention 'folder': {e}"

            print("upload_session_file error handling tests passed!")

            # --------------------------------------------------------------------------------------------------
            # Test download_session_file_to_path with invalid inputs
            # --------------------------------------------------------------------------------------------------

            # Test that download_session_file_to_path raises ValueError when file_path is a folder (str type)
            folder_path_str = tempfile.gettempdir()  # This is a folder, not a file
            print(f"Testing download_session_file_to_path with folder path (str): {folder_path_str}")
            try:
                project_client.agents.download_session_file_to_path(
                    agent_name=agent_name,
                    session_id=session_id,
                    file_path=folder_path_str,  # str type pointing to a folder
                    remote_path="/remote/some_file.txt",
                )
                assert False, "Expected ValueError when file_path is a folder (str type)"
            except ValueError as e:
                print(f"Got expected ValueError for folder path (str): {e}")
                assert "folder" in str(e).lower(), f"Error message should mention 'folder': {e}"

            # Test that download_session_file_to_path raises ValueError when file_path is a folder (PathLike type)
            folder_path_pathlike = Path(tempfile.gettempdir())  # This is a folder, not a file
            print(f"Testing download_session_file_to_path with folder path (PathLike): {folder_path_pathlike}")
            try:
                project_client.agents.download_session_file_to_path(
                    agent_name=agent_name,
                    session_id=session_id,
                    file_path=folder_path_pathlike,  # PathLike[str] type pointing to a folder
                    remote_path="/remote/some_file.txt",
                )
                assert False, "Expected ValueError when file_path is a folder (PathLike type)"
            except ValueError as e:
                print(f"Got expected ValueError for folder path (PathLike): {e}")
                assert "folder" in str(e).lower(), f"Error message should mention 'folder': {e}"

            print("download_session_file_to_path folder path validation tests passed!")

            # --------------------------------------------------------------------------------------------------
            # Test download_session_file_to_path with existing file (overwrite behavior)
            # --------------------------------------------------------------------------------------------------

            # Create a temporary file that already exists
            existing_file_path = os.path.join(tempfile.gettempdir(), "existing_file_for_overwrite_sync_test.txt")
            with open(existing_file_path, "w", encoding="utf-8") as f:
                f.write("This file already exists")

            try:
                # Test that download_session_file_to_path raises FileExistsError when file exists (default overwrite=False)
                print(
                    f"Testing download_session_file_to_path with existing file (default overwrite): {existing_file_path}"
                )
                try:
                    project_client.agents.download_session_file_to_path(
                        agent_name=agent_name,
                        session_id=session_id,
                        file_path=existing_file_path,
                        remote_path="/remote/some_file.txt",
                    )
                    assert False, "Expected FileExistsError when file already exists (default overwrite=False)"
                except FileExistsError as e:
                    print(f"Got expected FileExistsError (default overwrite): {e}")
                    assert "already exists" in str(e).lower(), f"Error message should mention 'already exists': {e}"
                    assert "overwrite=True" in str(e), f"Error message should mention 'overwrite=True': {e}"

                # Test that download_session_file_to_path raises FileExistsError when file exists with explicit overwrite=False
                print(
                    f"Testing download_session_file_to_path with existing file (explicit overwrite=False): {existing_file_path}"
                )
                try:
                    project_client.agents.download_session_file_to_path(
                        agent_name=agent_name,
                        session_id=session_id,
                        file_path=existing_file_path,
                        overwrite=False,
                        remote_path="/remote/some_file.txt",
                    )
                    assert False, "Expected FileExistsError when file already exists (explicit overwrite=False)"
                except FileExistsError as e:
                    print(f"Got expected FileExistsError (explicit overwrite=False): {e}")
                    assert "already exists" in str(e).lower(), f"Error message should mention 'already exists': {e}"
                    assert "overwrite=True" in str(e), f"Error message should mention 'overwrite=True': {e}"

                print("download_session_file_to_path overwrite validation tests passed!")

            finally:
                # Clean up the temporary file
                if os.path.exists(existing_file_path):
                    os.remove(existing_file_path)
                    print(f"Cleaned up temp file: {existing_file_path}")

            print("All invalid input tests passed!")

        finally:
            # Add any cleanup here
            ...
