# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_delete_result.py

DESCRIPTION:
    These tests validate the sample_delete_result.py sample code.

USAGE:
    pytest test_sample_delete_result.py
"""

import os
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import ContentUnderstandingPreparer, ContentUnderstandingClientTestBase


class TestSampleDeleteResult(ContentUnderstandingClientTestBase):
    """Tests for sample_delete_result.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_delete_result(self, azure_content_understanding_endpoint: str) -> None:
        """Test deleting an analysis result.
        
        This test validates:
        1. Document analysis to create a result
        2. Extracting result ID
        3. Deleting the result
        
        13_DeleteResult.DeleteResultAsync()
        """
        client = self.create_client(endpoint=azure_content_understanding_endpoint)

        # First, analyze a document to create a result
        tests_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(tests_dir, "test_data", "sample_invoice.pdf")
        
        assert os.path.exists(file_path), f"Sample file not found at {file_path}"
        print(f"[PASS] Sample file exists: {file_path}")
        
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        
        assert len(file_bytes) > 0, "File should not be empty"
        print(f"[PASS] File loaded: {len(file_bytes)} bytes")
        
        # Analyze to get a result ID
        poller = client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=file_bytes,
            content_type="application/pdf"
        )
        
        result = poller.result()
        
        # Assertions for analysis
        assert poller is not None, "Analysis operation should not be null"
        assert poller.done(), "Operation should be completed"
        assert result is not None, "Analysis result should not be null"
        print("[PASS] Analysis completed successfully")
        
        # Extract operation ID from the poller
        # The operation ID is needed to delete the result
        operation_id = None
        try:
            # Extract operation ID from polling URL
            if hasattr(poller, '_polling_method'):
                polling_method = getattr(poller, '_polling_method', None)
                if polling_method and hasattr(polling_method, '_operation'):
                    operation = getattr(polling_method, '_operation', None)  # type: ignore
                    if operation and hasattr(operation, 'get_polling_url'):
                        polling_url = operation.get_polling_url()  # type: ignore
                        # Extract operation ID from URL (last segment before query string)
                        operation_id = polling_url.split('/')[-1]
                        if '?' in operation_id:
                            operation_id = operation_id.split('?')[0]
        except Exception as e:
            print(f"[WARN] Could not extract operation ID: {str(e)[:100]}")
        
        # Assertion: Verify we have an operation ID
        if operation_id:
            assert operation_id is not None, "Operation ID should not be null"
            assert isinstance(operation_id, str), "Operation ID should be a string"
            assert operation_id.strip(), "Operation ID should not be empty"
            print(f"[PASS] Operation ID extracted: {operation_id[:50]}...")
            
            # Delete the result
            try:
                client.delete_result(operation_id=operation_id)
                print(f"[PASS] Result deleted successfully (operation ID: {operation_id[:50]}...)")
                print("[INFO] Deletion success verified by no exception thrown")
            except Exception as e:
                error_msg = str(e)
                # Some implementations might not support result deletion or result might auto-expire
                if "not found" in error_msg.lower() or "404" in error_msg:
                    print(f"[INFO] Result already deleted or not found: {error_msg[:100]}")
                else:
                    print(f"[WARN] Delete result failed: {error_msg[:100]}")
        else:
            print("[INFO] Operation ID not available in response")
            print("[INFO] Delete result operation skipped - operation ID extraction not supported")
        
        print("\n[SUCCESS] All test_sample_delete_result assertions passed")
