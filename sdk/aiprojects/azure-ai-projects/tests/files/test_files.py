# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import re
import pytest
from pathlib import Path
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, RecordedTransport


class TestFiles(TestBase):

    # To run this test, use the following command in the \sdk\aiprojects\azure-ai-projects folder:
    # cls & pytest tests\test_files.py::TestFiles::test_files -s
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.HTTPX)
    def test_files(self, **kwargs):

        file_purpose = self.test_files_params["file_purpose"]
        test_file_name = self.test_files_params["test_file_name"]

        test_data_dir = Path(__file__).parent.parent / "test_data" / "files"
        test_file_path = test_data_dir / test_file_name

        assert test_file_path.exists(), f"Test file not found: {test_file_path}"

        with self.create_client(**kwargs) as project_client:

            with project_client.get_openai_client() as openai_client:

                print(f"[test_files] Create (upload) a file with purpose '{file_purpose}'")
                with open(test_file_path, "rb") as f:
                    uploaded_file = openai_client.files.create(file=f, purpose=file_purpose)
                TestBase.validate_file(uploaded_file, expected_purpose=file_purpose)
                file_id = uploaded_file.id
                print(f"[test_files] Uploaded file with ID: {file_id}")

                processed_file = openai_client.files.wait_for_processing(file_id)
                TestBase.assert_equal_or_not_none(processed_file.status, "processed")
                print(f"[test_files] File processed successfully with ID: {file_id}")

                print(f"[test_files] Retrieve file metadata by ID: {file_id}")
                retrieved_file = openai_client.files.retrieve(file_id)
                TestBase.validate_file(retrieved_file, expected_file_id=file_id, expected_purpose=file_purpose)
                print(f"[test_files] Retrieved file: {retrieved_file.filename}")

                print(f"[test_files] Retrieve file content for ID: {file_id}")
                file_content = openai_client.files.content(file_id)
                assert file_content is not None
                assert file_content.content is not None
                assert len(file_content.content) > 0
                print(f"[test_files] File content retrieved ({len(file_content.content)} bytes)")

                print("[test_files] List all files")
                found_uploaded_file = False
                for file in openai_client.files.list():
                    if file.id == file_id:
                        found_uploaded_file = True
                        TestBase.validate_file(file)
                        print(f"[test_files] Found uploaded file in list: {file.id}")
                        break
                assert found_uploaded_file, "Uploaded file not found in list"

                print(f"[test_files] Delete file with ID: {file_id}")
                deleted_file = openai_client.files.delete(file_id)
                TestBase.assert_equal_or_not_none(deleted_file.id, file_id)
                assert deleted_file.deleted is True
                print(f"[test_files] Successfully deleted file: {deleted_file.id}")
