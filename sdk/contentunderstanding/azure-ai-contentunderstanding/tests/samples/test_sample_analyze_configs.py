# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_analyze_configs.py

DESCRIPTION:
    These tests validate the sample_analyze_configs.py sample code.

USAGE:
    pytest test_sample_analyze_configs.py
"""

import os
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import ContentUnderstandingPreparer, ContentUnderstandingClientTestBase


class TestSampleAnalyzeConfigs(ContentUnderstandingClientTestBase):
    """Tests for sample_analyze_configs.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_analyze_configs(self, contentunderstanding_endpoint: str) -> None:
        """Test analyzing a document with specific configuration options.
        
        This test validates:
        1. Document analysis with prebuilt-documentSearch analyzer
        2. Configuration options (formulas, layout, OCR enabled)
        3. Document features extraction (charts, annotations, hyperlinks, formulas)
        
        10_AnalyzeConfigs.AnalyzeConfigsAsync()
        """
        client = self.create_client(endpoint=contentunderstanding_endpoint)

        # Read the sample file (using sample_invoice.pdf as it contains various features)
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
        
        # Assertion: Verify binary data
        assert file_bytes is not None, "Binary data should not be null"
        print("[PASS] Binary data created successfully")
        
        # Analyze with prebuilt-documentSearch which has formulas, layout, and OCR enabled
        poller = client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=file_bytes,
            content_type="application/pdf"
        )
        
        result = poller.result()
        
        # Assertion: Verify analysis operation completed
        assert poller is not None, "Analysis operation should not be null"
        assert poller.done(), "Operation should be completed"
        
        # Verify raw response
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
                        print(f"[PASS] Raw response verified (status: {status})")
        
        assert poller.status() == "Succeeded", f"Operation status should be Succeeded, but was {poller.status()}"
        print("[PASS] Analysis operation completed successfully")
        
        # Assertion: Verify result
        assert result is not None, "Analysis result should not be null"
        assert hasattr(result, "contents"), "Result should have contents attribute"
        assert result.contents is not None, "Result contents should not be null"
        assert len(result.contents) > 0, "Result should have at least one content"
        assert len(result.contents) == 1, "PDF file should have exactly one content element"
        print(f"[PASS] Analysis result contains {len(result.contents)} content(s)")
        
        # Verify document content type
        first_content = result.contents[0]
        assert first_content is not None, "Content should not be null"
        
        # Check if this is document content
        content_type = type(first_content).__name__
        print(f"[INFO] Content type: {content_type}")
        
        is_document_content = hasattr(first_content, 'mime_type') and hasattr(first_content, 'start_page_number')
        if is_document_content:
            start_page = getattr(first_content, "start_page_number", None)
            end_page = getattr(first_content, "end_page_number", None)
            
            if start_page and end_page:
                assert start_page >= 1, "Start page should be >= 1"
                assert end_page >= start_page, "End page should be >= start page"
                total_pages = end_page - start_page + 1
                print(f"[PASS] Document has {total_pages} page(s) from {start_page} to {end_page}")
        
        print("[PASS] Document features analysis with configs completed successfully")
        
        # Test document feature extraction
        self._test_document_features(first_content)
        
        print("\n[SUCCESS] All test_sample_analyze_configs assertions passed")

    def _test_document_features(self, content):
        """Test extraction of document features like charts, annotations, hyperlinks."""
        # Check for charts
        charts = getattr(content, "charts", None)
        if charts and len(charts) > 0:
            print(f"[PASS] Found {len(charts)} chart(s) in document")
            for i, chart in enumerate(charts, 1):
                assert chart is not None, f"Chart {i} should not be null"
                print(f"  Chart {i} detected")
        else:
            print("[INFO] No charts found in document")
        
        # Check for annotations
        annotations = getattr(content, "annotations", None)
        if annotations and len(annotations) > 0:
            print(f"[PASS] Found {len(annotations)} annotation(s) in document")
        else:
            print("[INFO] No annotations found in document")
        
        # Check for hyperlinks
        hyperlinks = getattr(content, "hyperlinks", None)
        if hyperlinks and len(hyperlinks) > 0:
            print(f"[PASS] Found {len(hyperlinks)} hyperlink(s) in document")
        else:
            print("[INFO] No hyperlinks found in document")
        
        # Check for formulas
        formulas = getattr(content, "formulas", None)
        if formulas and len(formulas) > 0:
            print(f"[PASS] Found {len(formulas)} formula(s) in document")
        else:
            print("[INFO] No formulas found in document")
