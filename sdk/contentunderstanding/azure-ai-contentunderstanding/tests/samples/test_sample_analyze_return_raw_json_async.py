# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_analyze_return_raw_json_async.py

DESCRIPTION:
    These tests validate the sample_analyze_return_raw_json.py sample code (async version).

USAGE:
    pytest test_sample_analyze_return_raw_json_async.py
"""

import os
import json
from devtools_testutils.aio import recorded_by_proxy_async
from testpreparer_async import ContentUnderstandingPreparer, ContentUnderstandingClientTestBaseAsync


class TestSampleAnalyzeReturnRawJsonAsync(ContentUnderstandingClientTestBaseAsync):
    """Tests for sample_analyze_return_raw_json.py (async version)"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_analyze_return_raw_json_async(self, azure_content_understanding_endpoint: str) -> None:
        """Test analyzing a document and getting raw JSON response (async version).
        
        This test validates:
        1. Document analysis using 'cls' callback to get raw HTTP response
        2. Raw JSON response format
        3. JSON structure validation
        
        11_AnalyzeReturnRawJson.AnalyzeReturnRawJsonAsync()
        """
        client = self.create_async_client(endpoint=azure_content_understanding_endpoint)

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
        
        # Use 'cls' callback to get raw HTTP response
        # The 'cls' parameter allows us to intercept the response before it gets deserialized as an object model
        # We return a tuple: (deserialized_object, raw_http_response)
        poller = await client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=file_bytes,
            content_type="application/pdf",
            cls=lambda pipeline_response, deserialized_obj, response_headers: (
                deserialized_obj,
                pipeline_response.http_response,
            ),
        )
        
        # Wait for completion and get both model and raw HTTP response
        _, raw_http_response = await poller.result()
        
        # Assertion: Verify analysis operation completed
        assert poller is not None, "Analysis operation should not be null"
        assert poller.done(), "Operation should be completed"
        assert poller.status() == "Succeeded", f"Operation status should be Succeeded, but was {poller.status()}"
        print("[PASS] Analysis operation completed successfully")
        
        # Assertion: Verify raw HTTP response
        assert raw_http_response is not None, "Raw HTTP response should not be null"
        print("[PASS] Raw HTTP response is not null")
        
        # Parse the raw JSON response
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
        
        await client.close()
        print("\n[SUCCESS] All test_sample_analyze_return_raw_json_async assertions passed")
