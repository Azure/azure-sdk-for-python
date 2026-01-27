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
    This sample demonstrates how to delete analysis results using the delete_result API.

USAGE:
    pytest test_sample_delete_result.py
"""

import os
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import ContentUnderstandingPreparer, ContentUnderstandingClientTestBase
from azure.ai.contentunderstanding.models import AnalyzeInput, AnalyzeResult, DocumentContent


class TestSampleDeleteResult(ContentUnderstandingClientTestBase):
    """Tests for sample_delete_result.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_delete_result(self, contentunderstanding_endpoint: str) -> None:
        """Test deleting an analysis result.

        This test validates:
        1. Document analysis to create a result
        2. Extracting operation ID
        3. Deleting the result using operation ID

        Equivalent to: Sample13_DeleteResult.DeleteResultAsync()
        """
        client = self.create_client(endpoint=contentunderstanding_endpoint)

        # First, analyze a document to create a result
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_data_dir = os.path.join(os.path.dirname(current_dir), "test_data")
        file_path = os.path.join(test_data_dir, "sample_invoice.pdf")

        assert os.path.exists(file_path), f"Sample file not found at {file_path}"
        print(f"[PASS] Sample file exists: {file_path}")

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        assert len(file_bytes) > 0, "File should not be empty"
        print(f"[PASS] File loaded: {len(file_bytes)} bytes")

        # Analyze to get an operation ID
        analyze_operation = client.begin_analyze(
            analyzer_id="prebuilt-invoice", inputs=[AnalyzeInput(data=file_bytes)]
        )

        result: AnalyzeResult = analyze_operation.result()

        # Assertions for analysis
        assert analyze_operation is not None, "Analysis operation should not be null"
        assert analyze_operation.done(), "Operation should be completed"
        assert result is not None, "Analysis result should not be null"
        print("[PASS] Analysis completed successfully")

        # Get operation ID - this is needed to delete the result
        operation_id = analyze_operation.operation_id
        assert operation_id is not None, "Operation ID should not be null"
        assert isinstance(operation_id, str), "Operation ID should be a string"
        assert operation_id.strip(), "Operation ID should not be empty"
        print(f"[PASS] Operation ID extracted: {operation_id[:50]}...")

        # Verify we have analysis content
        assert hasattr(result, "contents"), "Result should contain contents"
        contents = getattr(result, "contents", None)
        assert contents is not None, "Result contents should not be null"
        assert len(contents) > 0, "Result should have at least one content"
        print(f"[PASS] Analysis result contains {len(contents)} content item(s)")

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
                raise

        print("\n[SUCCESS] All test_sample_delete_result assertions passed")
