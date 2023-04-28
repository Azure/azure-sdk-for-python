# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import pytest
import re


@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestListMaterializationJobRequest:
    # ---------------------------------------------------------
    # Ensure tEt the list_materialization_jobs request is a POST request
    # Regenerating the rest client will fail this test
    # To fix manuallay update the _featureset_versions_operations.py file in rest client
    # Upate: request.method = "POST" in list_materialization_jobs function
    # ---------------------------------------------------------
    def test_list_materialization_job_request(self) -> None:
        test_path = "azure/ai/ml/_restclient/v2023_04_01_preview/operations/_featureset_versions_operations.py"
        with open(test_path, "r") as f:
            file_contents = f.read()
        start = "def list_materialization_jobs"
        end = "return request"
        pattern = re.compile(start + r"(.*?)" + end, re.DOTALL)
        match = pattern.search(file_contents)

        assert match is not None
        assert len(match.groups()) == 1
        content = match.group(1)
        expectedPostRequest = 'request.method = "POST"'
        assert expectedPostRequest in content
