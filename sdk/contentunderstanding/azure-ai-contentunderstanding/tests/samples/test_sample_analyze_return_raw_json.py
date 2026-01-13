# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_analyze_return_raw_json.py

DESCRIPTION:
    These tests validate the sample_analyze_return_raw_json.py sample code.

    This sample demonstrates how to access the raw JSON response from analysis operations
    using the convenience method and then accessing the raw response. This is useful for:
    - Easy inspection: View the complete response structure in the exact format returned by the service
    - Debugging: Inspect the raw response to troubleshoot issues or verify service behavior
    - Advanced scenarios: Work with response structures that may include additional metadata

USAGE:
    pytest test_sample_analyze_return_raw_json.py
"""

import os
import json
from devtools_testutils import recorded_by_proxy
from testpreparer import ContentUnderstandingPreparer, ContentUnderstandingClientTestBase


class TestSampleAnalyzeReturnRawJson(ContentUnderstandingClientTestBase):
    """Tests for sample_analyze_return_raw_json.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_analyze_return_raw_json(self, contentunderstanding_endpoint: str) -> None:
        """Test analyzing a document and getting raw JSON response.

        This test validates:
        1. Document analysis using convenience method to get raw HTTP response
        2. Raw JSON response format for easy inspection and debugging
        3. JSON structure validation

        11_AnalyzeReturnRawJson.AnalyzeReturnRawJson()
        """
        client = self.create_client(endpoint=contentunderstanding_endpoint)

        # Read the sample file
        tests_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(tests_dir, "test_data", "sample_invoice.pdf")

        # Assertion: Verify file exists
        assert os.path.exists(file_path), f"Sample file not found at {file_path}"
        print(f"[PASS] Sample file exists: {file_path}")

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        # Assertion: Verify file is not empty
        assert len(file_bytes) > 0, "File should not be empty"
        print(f"[PASS] File loaded: {len(file_bytes)} bytes")

        # Use convenience method to analyze the document
        # The cls callback allows access to the complete response structure for easy inspection and debugging
        poller = client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=file_bytes,
            cls=lambda pipeline_response, deserialized_obj, response_headers: (
                deserialized_obj,
                pipeline_response.http_response,
            ),
        )

        # Wait for completion and get both model and raw HTTP response
        _, raw_http_response = poller.result()

        # Assertion: Verify analysis operation completed
        assert poller is not None, "Analysis operation should not be null"
        assert poller.done(), "Operation should be completed"
        assert poller.status() == "Succeeded", f"Operation status should be Succeeded, but was {poller.status()}"
        print("[PASS] Analysis operation completed successfully")

        # Assertion: Verify raw HTTP response
        assert raw_http_response is not None, "Raw HTTP response should not be null"
        print("[PASS] Raw HTTP response is not null")

        # Get the raw JSON response
        response_json = raw_http_response.json()

        # Assertion: Verify JSON is not empty
        assert response_json is not None, "Response JSON should not be null"
        print("[PASS] Response JSON parsed successfully")

        # Verify it's valid JSON by serializing
        json_str = json.dumps(response_json, indent=2, ensure_ascii=False)
        assert json_str is not None, "Response string should not be null"
        assert len(json_str) > 0, "Response string should not be empty"
        print(f"[PASS] Response converted to JSON string: {len(json_str)} characters")

        # Verify the response contains expected structure (matching C# sample validation)
        assert "result" in response_json, "Response should contain 'result' key"
        result_data = response_json["result"]
        print("[PASS] Response contains 'result' key")

        # Verify analyzerId
        if "analyzerId" in result_data:
            print(f"[PASS] Analyzer ID: {result_data['analyzerId']}")

        # Verify contents
        if "contents" in result_data and isinstance(result_data["contents"], list):
            contents_count = len(result_data["contents"])
            print(f"[PASS] Contents count: {contents_count}")

            if contents_count > 0:
                first_content = result_data["contents"][0]
                if "kind" in first_content:
                    print(f"[PASS] Content kind: {first_content['kind']}")
                if "mimeType" in first_content:
                    print(f"[PASS] MIME type: {first_content['mimeType']}")

        print("\n[SUCCESS] All test_sample_analyze_return_raw_json assertions passed")
