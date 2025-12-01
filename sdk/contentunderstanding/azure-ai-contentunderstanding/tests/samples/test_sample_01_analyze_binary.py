# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_01_analyze_binary.py

DESCRIPTION:
    These tests validate the sample_01_analyze_binary.py sample code.
    Tests correspond to .NET Sample01_AnalyzeBinary.cs

USAGE:
    pytest test_sample_01_analyze_binary.py
"""

import os
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import ContentUnderstandingPreparer, ContentUnderstandingClientTestBase


class TestSample01AnalyzeBinary(ContentUnderstandingClientTestBase):
    """Tests for sample_01_analyze_binary.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_01_analyze_binary(self, contentunderstanding_endpoint: str) -> None:
        """Test analyzing a document from binary data.
        
        This test validates:
        1. File loading and binary data creation
        2. Document analysis using begin_analyze_binary
        3. Markdown content extraction
        4. Document properties (MIME type, pages, tables)
        
        Corresponds to .NET Sample01_AnalyzeBinary.AnalyzeBinaryAsync()
        """
        client = self.create_client(endpoint=contentunderstanding_endpoint)

        # Read the sample file
        # Use test_data directory from parent tests folder
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
        
        # Assertion: Verify binary data (equivalent to .NET BinaryData)
        assert file_bytes is not None, "Binary data should not be null"
        print("[PASS] Binary data created successfully")
        
        # Analyze the document
        poller = client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=file_bytes,
            content_type="application/pdf"
        )
        
        result = poller.result()
        
        # Assertion: Verify analysis operation completed
        assert poller is not None, "Analysis operation should not be null"
        assert poller.done(), "Operation should be completed"
        
        # Verify raw response (equivalent to .NET GetRawResponse())
        # In Python SDK, we can check if the poller has result and get HTTP response info
        # type: ignore is used here because we're accessing internal implementation details
        if hasattr(poller, '_polling_method'):
            polling_method = getattr(poller, '_polling_method', None)
            if polling_method and hasattr(polling_method, '_initial_response'):
                raw_response = getattr(polling_method, '_initial_response', None)  # type: ignore
                if raw_response:
                    # PipelineResponse has http_response attribute
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
        print(f"[PASS] Analysis result contains {len(result.contents)} content(s)")
        
        # Test markdown extraction
        self._test_markdown_extraction(result)
        
        # Test document properties access
        self._test_document_properties(result)
        
        print("\n[SUCCESS] All test_sample_01_analyze_binary assertions passed")

    def _test_markdown_extraction(self, result):
        """Test markdown content extraction.
        
        Corresponds to .NET Assertion:ContentUnderstandingExtractMarkdown
        """
        # Assertion: Verify contents structure
        assert result.contents is not None, "Result should contain contents"
        assert len(result.contents) > 0, "Result should have at least one content"
        assert len(result.contents) == 1, "PDF file should have exactly one content element"
        
        content = result.contents[0]
        assert content is not None, "Content should not be null"
        
        # Assertion: Verify markdown content
        markdown = getattr(content, "markdown", None)
        if markdown:
            assert isinstance(markdown, str), "Markdown should be a string"
            assert len(markdown) > 0, "Markdown content should not be empty"
            assert markdown.strip(), "Markdown content should not be just whitespace"
            print(f"[PASS] Markdown content extracted successfully ({len(markdown)} characters)")
        else:
            print("[WARN]  No markdown content available")

    def _test_document_properties(self, result):
        """Test document property access.
        
        Corresponds to .NET Assertion:ContentUnderstandingAccessDocumentProperties
        """
        content = result.contents[0]
        assert content is not None, "Content should not be null for document properties validation"
        
        # Check if this is DocumentContent (equivalent to .NET's DocumentContent type check)
        content_type = type(content).__name__
        print(f"[INFO] Content type: {content_type}")
        
        # Validate this is document content (should have document-specific properties)
        is_document_content = hasattr(content, 'mime_type') and hasattr(content, 'start_page_number')
        if not is_document_content:
            print(f"[WARN] Expected DocumentContent but got {content_type}, skipping document-specific validations")
            return
        
        # Validate MIME type
        mime_type = getattr(content, "mime_type", None)
        if mime_type:
            assert isinstance(mime_type, str), "MIME type should be a string"
            assert mime_type.strip(), "MIME type should not be empty"
            assert mime_type == "application/pdf", f"MIME type should be application/pdf, but was {mime_type}"
            print(f"[PASS] MIME type verified: {mime_type}")
        
        # Validate page numbers
        start_page = getattr(content, "start_page_number", None)
        if start_page is not None:
            assert start_page >= 1, f"Start page should be >= 1, but was {start_page}"
            
            end_page = getattr(content, "end_page_number", None)
            if end_page is not None:
                assert end_page >= start_page, f"End page {end_page} should be >= start page {start_page}"
                total_pages = end_page - start_page + 1
                assert total_pages > 0, f"Total pages should be positive, but was {total_pages}"
                print(f"[PASS] Page range verified: {start_page} to {end_page} ({total_pages} pages)")
                
                # Validate pages collection
                pages = getattr(content, "pages", None)
                if pages and len(pages) > 0:
                    assert len(pages) > 0, "Pages collection should not be empty when not null"
                    assert len(pages) == total_pages, \
                        f"Pages collection count {len(pages)} should match calculated total pages {total_pages}"
                    print(f"[PASS] Pages collection verified: {len(pages)} pages")
                    
                    # Validate individual pages
                    self._validate_pages(pages, start_page, end_page, content)
                else:
                    print("[WARN] No pages collection available in document content")
        
        # Validate tables collection
        tables = getattr(content, "tables", None)
        if tables and len(tables) > 0:
            self._validate_tables(tables)
        else:
            print("No tables found in document content")
        
        # Final validation message (matching .NET)
        print("[PASS] All document properties validated successfully")

    def _validate_pages(self, pages, start_page, end_page, content=None):
        """Validate pages collection details."""
        page_numbers = set()
        unit = getattr(content, 'unit', None) if content else None
        unit_str = str(unit) if unit else "units"
        
        for page in pages:
            assert page is not None, "Page object should not be null"
            assert hasattr(page, "page_number"), "Page should have page_number attribute"
            assert page.page_number >= 1, f"Page number should be >= 1, but was {page.page_number}"
            assert start_page <= page.page_number <= end_page, \
                f"Page number {page.page_number} should be within document range [{start_page}, {end_page}]"
            
            assert hasattr(page, "width") and page.width > 0, \
                f"Page {page.page_number} width should be > 0, but was {page.width}"
            assert hasattr(page, "height") and page.height > 0, \
                f"Page {page.page_number} height should be > 0, but was {page.height}"
            
            # Ensure page numbers are unique
            assert page.page_number not in page_numbers, \
                f"Page number {page.page_number} appears multiple times"
            page_numbers.add(page.page_number)
            
            # Print page details with unit (matching .NET output)
            print(f"  Page {page.page_number}: {page.width} x {page.height} {unit_str}")
        
        print(f"[PASS] All {len(pages)} pages validated successfully")

    def _validate_tables(self, tables):
        """Validate tables collection details."""
        assert len(tables) > 0, "Tables collection should not be empty when not null"
        print(f"[PASS] Tables collection verified: {len(tables)} tables")
        
        for i, table in enumerate(tables, 1):
            assert table is not None, f"Table {i} should not be null"
            assert hasattr(table, "row_count"), f"Table {i} should have row_count attribute"
            assert hasattr(table, "column_count"), f"Table {i} should have column_count attribute"
            assert table.row_count > 0, \
                f"Table {i} should have at least 1 row, but had {table.row_count}"
            assert table.column_count > 0, \
                f"Table {i} should have at least 1 column, but had {table.column_count}"
            
            # Validate table cells if available
            if hasattr(table, "cells") and table.cells:
                assert len(table.cells) > 0, \
                    f"Table {i} cells collection should not be empty when not null"
                
                for cell in table.cells:
                    assert cell is not None, "Table cell should not be null"
                    assert hasattr(cell, "row_index"), "Cell should have row_index"
                    assert hasattr(cell, "column_index"), "Cell should have column_index"
                    assert 0 <= cell.row_index < table.row_count, \
                        f"Cell row index {cell.row_index} should be within table row count {table.row_count}"
                    assert 0 <= cell.column_index < table.column_count, \
                        f"Cell column index {cell.column_index} should be within table column count {table.column_count}"
                    
                    if hasattr(cell, "row_span"):
                        assert cell.row_span >= 1, f"Cell row span should be >= 1, but was {cell.row_span}"
                    if hasattr(cell, "column_span"):
                        assert cell.column_span >= 1, f"Cell column span should be >= 1, but was {cell.column_span}"
                
                print(f"[PASS] Table {i} validated: {table.row_count} rows x {table.column_count} columns ({len(table.cells)} cells)")
            else:
                print(f"[PASS] Table {i} validated: {table.row_count} rows x {table.column_count} columns")

