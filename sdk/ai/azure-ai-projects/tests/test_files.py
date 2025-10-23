# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from pathlib import Path
from azure.ai.projects import AIProjectClient
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, is_live_and_not_recording


class TestFiles(TestBase):

    # To run this test, use the following command in the \sdk\ai\azure-ai-projects folder:
    # cls & pytest tests\test_files.py::TestFiles::test_files -s
    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with AOAI client",
    )
    @recorded_by_proxy
    def test_files(self, **kwargs):

        endpoint = kwargs.pop("azure_ai_projects_tests_project_endpoint")
        print("\n=====> Endpoint:", endpoint)

        file_purpose = self.test_files_params["file_purpose"]
        test_file_name = self.test_files_params["test_file_name"]

        # Get the path to the test file in test_data/files
        test_data_dir = Path(__file__).parent / "test_data" / "files"
        test_file_path = test_data_dir / test_file_name
        
        assert test_file_path.exists(), f"Test file not found: {test_file_path}"

        with AIProjectClient(
            endpoint=endpoint,
            credential=self.get_credential(AIProjectClient, is_async=False),
        ) as project_client:

            # Get OpenAI client from project client
            with project_client.get_openai_client(api_version="2025-04-01-preview") as open_ai_client:

                # Create (upload) a file
                print(f"[test_files] Create (upload) a file with purpose '{file_purpose}'")
                with open(test_file_path, "rb") as f:
                    uploaded_file = open_ai_client.files.create(file=f, purpose=file_purpose)
                
                TestBase.validate_file(uploaded_file, expected_purpose=file_purpose)
                file_id = uploaded_file.id
                print(f"[test_files] Uploaded file with ID: {file_id}")

                # Retrieve file metadata by ID
                print(f"[test_files] Retrieve file metadata by ID: {file_id}")
                retrieved_file = open_ai_client.files.retrieve(file_id)
                TestBase.validate_file(
                    retrieved_file, expected_file_id=file_id, expected_purpose=file_purpose
                )
                print(f"[test_files] Retrieved file: {retrieved_file.filename}")

                # Retrieve file content
                print(f"[test_files] Retrieve file content for ID: {file_id}")
                file_content = open_ai_client.files.content(file_id)
                assert file_content is not None
                assert file_content.content is not None
                assert len(file_content.content) > 0
                print(f"[test_files] File content retrieved ({len(file_content.content)} bytes)")

                # List all files
                print("[test_files] List all files")
                found_uploaded_file = False
                for file in open_ai_client.files.list():
                    TestBase.validate_file(file)
                    if file.id == file_id:
                        found_uploaded_file = True
                        print(f"[test_files] Found uploaded file in list: {file.id}")
                assert found_uploaded_file, "Uploaded file not found in list"

                # Delete the file
                print(f"[test_files] Delete file with ID: {file_id}")
                deleted_file = open_ai_client.files.delete(file_id)
                assert deleted_file is not None
                assert deleted_file.id == file_id
                assert deleted_file.deleted is True
                print(f"[test_files] Successfully deleted file: {deleted_file.id}")

                # Verify file is deleted (should not be in list)
                print("[test_files] Verify file is deleted from list")
                file_still_exists = False
                for file in open_ai_client.files.list():
                    if file.id == file_id:
                        file_still_exists = True
                        break
                assert not file_still_exists, "Deleted file still appears in list"
                print("[test_files] Confirmed file is no longer in list")
