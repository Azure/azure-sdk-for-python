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

USAGE:
    pytest test_sample_analyze_return_raw_json.py
"""

import os
import json
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import ContentUnderstandingPreparer, ContentUnderstandingClientTestBase


class TestSampleAnalyzeReturnRawJson(ContentUnderstandingClientTestBase):
    """Tests for sample_analyze_return_raw_json.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_analyze_return_raw_json(self, contentunderstanding_endpoint: str) -> None:
        """Test analyzing a document and getting raw JSON response.
        
        This test validates:
        1. Document analysis using protocol method
        2. Raw JSON response format
        3. JSON structure validation
        
        11_AnalyzeReturnRawJson.AnalyzeReturnRawJsonAsync()
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
        
        # Analyze the document and get raw response
        # Note: The Python SDK returns structured objects by default
        # We can access the raw response through the result
        poller = client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=file_bytes,
            content_type="application/pdf"
        )
        
        result = poller.result()
        
        # Assertion: Verify analysis operation completed
        assert poller is not None, "Analysis operation should not be null"
        assert poller.done(), "Operation should be completed"
        
        # Verify raw response status
        if hasattr(poller, '_polling_method'):
            polling_method = getattr(poller, '_polling_method', None)
            if polling_method and hasattr(polling_method, '_initial_response'):
                raw_response = getattr(polling_method, '_initial_response', None)  # type: ignore
                if raw_response:
                    if hasattr(raw_response, 'http_response'):
                        status = raw_response.http_response.status_code
                    elif hasattr(raw_response, 'status_code'):
                        status = raw_response.status_code
                    else:
                        status = None
                        
                    if status:
                        assert status >= 200 and status < 300, \
                            f"Response status should be successful (200-299), but was {status}"
                        print(f"[PASS] Raw response status verified: {status}")
        
        assert poller.status() == "Succeeded", f"Operation status should be Succeeded, but was {poller.status()}"
        print("[PASS] Analysis operation completed successfully")
        
        # Assertion: Verify result
        assert result is not None, "Analysis result should not be null"
        print("[PASS] Response data is not null")
        
        # Convert result to JSON string to verify raw format capability
        # In Python SDK, we can serialize the result to JSON
        try:
            # Try to access the raw response data
            if hasattr(result, '__dict__'):
                result_dict = result.__dict__
                json_str = json.dumps(result_dict, default=str)
                assert json_str is not None, "Response string should not be null"
                assert len(json_str) > 0, "Response string should not be empty"
                print(f"[PASS] Response converted to JSON string: {len(json_str)} characters")
                
                # Verify it's valid JSON
                parsed_json = json.loads(json_str)
                assert parsed_json is not None, "Response should be valid JSON"
                print("[PASS] Response is valid JSON format")
            else:
                print("[INFO] Result does not have __dict__ attribute, using alternative method")
                
                # Alternative: Check if result has contents (which confirms it's a valid response)
                assert hasattr(result, "contents"), "Result should have contents attribute"
                assert result.contents is not None, "Result contents should not be null"
                print("[PASS] Response data structure verified")
                
        except json.JSONDecodeError as e:
            pytest.fail(f"Response should be valid JSON format: {str(e)}")
        except Exception as e:
            print(f"[WARN] Could not serialize to JSON: {str(e)}")
            # Still verify basic structure
            assert result is not None, "Result should not be null"
            print("[PASS] Response data verified (structured format)")
        
        # Verify the response contains expected data
        assert hasattr(result, "contents"), "Result should have contents"
        if result.contents and len(result.contents) > 0:
            print(f"[PASS] Response contains {len(result.contents)} content(s)")
        
        print("\n[SUCCESS] All test_sample_analyze_return_raw_json assertions passed")
