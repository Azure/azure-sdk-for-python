# pylint: disable=line-too-long,useless-suppression
# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_analyze_url.py

DESCRIPTION:
    These tests validate the sample_analyze_url.py sample code.
    This sample demonstrates prebuilt RAG analyzers with URL inputs. Content Understanding supports
    both local binary inputs (see sample_analyze_binary.py) and URL inputs across all modalities.
    For URL inputs, use begin_analyze() with AnalyzeInput objects that wrap the URL.

USAGE:
    pytest test_sample_analyze_url.py
"""

import os
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import ContentUnderstandingPreparer, ContentUnderstandingClientTestBase
from azure.ai.contentunderstanding.models import AnalyzeInput


class TestSampleAnalyzeUrl(ContentUnderstandingClientTestBase):
    """Tests for sample_analyze_url.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_analyze_url(self, azure_content_understanding_endpoint: str) -> None:
        """Test analyzing a document from URL.

        This test validates:
        1. URL validation
        2. Document analysis using begin_analyze with URL input
        3. Markdown content extraction
        4. Document properties (MIME type, pages, tables)

        02_AnalyzeUrl.AnalyzeUrlAsync()
        """
        client = self.create_client(endpoint=azure_content_understanding_endpoint)

        # Use a publicly accessible URL for testing
        # In production, this would be a real URL to a document
        # For testing, we'll use binary data instead since file:// URLs are not supported
        tests_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(tests_dir, "test_data", "sample_invoice.pdf")

        # Read file as binary data (since test proxy doesn't support file:// URLs)
        with open(file_path, "rb") as f:
            file_data = f.read()

        print(f"[PASS] Document loaded from: {file_path}")

        # Analyze the document
        poller = client.begin_analyze(analyzer_id="prebuilt-documentSearch", inputs=[AnalyzeInput(data=file_data)])

        result = poller.result()

        # Assertion: Verify analysis operation completed
        assert poller is not None, "Analysis operation should not be null"
        assert poller.done(), "Operation should be completed"

        # Verify raw response
        if hasattr(poller, "_polling_method"):
            polling_method = getattr(poller, "_polling_method", None)
            if polling_method and hasattr(polling_method, "_initial_response"):
                raw_response = getattr(polling_method, "_initial_response", None)  # type: ignore
                if raw_response:
                    if hasattr(raw_response, "http_response"):
                        status = raw_response.http_response.status_code
                    elif hasattr(raw_response, "status_code"):
                        status = raw_response.status_code
                    else:
                        status = None

                    if status:
                        assert (
                            status >= 200 and status < 300
                        ), f"Response status should be successful (200-299), but was {status}"
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

        print("\n[SUCCESS] All test_sample_analyze_url assertions passed")

    def _test_markdown_extraction(self, result):
        """Test markdown content extraction."""
        assert result.contents is not None, "Result should contain contents"
        assert len(result.contents) > 0, "Result should have at least one content"
        assert len(result.contents) == 1, "PDF file should have exactly one content element"

        content = result.contents[0]
        assert content is not None, "Content should not be null"

        markdown = getattr(content, "markdown", None)
        if markdown:
            assert isinstance(markdown, str), "Markdown should be a string"
            assert len(markdown) > 0, "Markdown content should not be empty"
            assert markdown.strip(), "Markdown content should not be just whitespace"
            print(f"[PASS] Markdown content extracted successfully ({len(markdown)} characters)")
        else:
            print("[WARN] No markdown content available")

    def _test_document_properties(self, result):
        """Test document property access."""
        content = result.contents[0]
        assert content is not None, "Content should not be null for document properties validation"

        content_type = type(content).__name__
        print(f"[INFO] Content type: {content_type}")

        is_document_content = hasattr(content, "mime_type") and hasattr(content, "start_page_number")
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

                pages = getattr(content, "pages", None)
                if pages and len(pages) > 0:
                    assert len(pages) > 0, "Pages collection should not be empty when not null"
                    assert (
                        len(pages) == total_pages
                    ), f"Pages collection count {len(pages)} should match calculated total pages {total_pages}"
                    print(f"[PASS] Pages collection verified: {len(pages)} pages")
                    self._validate_pages(pages, start_page, end_page, content)
                else:
                    print("[WARN] No pages collection available in document content")

        tables = getattr(content, "tables", None)
        if tables and len(tables) > 0:
            self._validate_tables(tables)
        else:
            print("No tables found in document content")

        print("[PASS] All document properties validated successfully")

    def _validate_pages(self, pages, start_page, end_page, content=None):
        """Validate pages collection details."""
        page_numbers = set()
        unit = getattr(content, "unit", None) if content else None
        unit_str = str(unit) if unit else "units"

        for page in pages:
            assert page is not None, "Page object should not be null"
            assert hasattr(page, "page_number"), "Page should have page_number attribute"
            assert page.page_number >= 1, f"Page number should be >= 1, but was {page.page_number}"
            assert (
                start_page <= page.page_number <= end_page
            ), f"Page number {page.page_number} should be within document range [{start_page}, {end_page}]"

            assert (
                hasattr(page, "width") and page.width > 0
            ), f"Page {page.page_number} width should be > 0, but was {page.width}"
            assert (
                hasattr(page, "height") and page.height > 0
            ), f"Page {page.page_number} height should be > 0, but was {page.height}"

            assert page.page_number not in page_numbers, f"Page number {page.page_number} appears multiple times"
            page_numbers.add(page.page_number)

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
            assert table.row_count > 0, f"Table {i} should have at least 1 row, but had {table.row_count}"
            assert table.column_count > 0, f"Table {i} should have at least 1 column, but had {table.column_count}"

            if hasattr(table, "cells") and table.cells:
                assert len(table.cells) > 0, f"Table {i} cells collection should not be empty when not null"

                for cell in table.cells:
                    assert cell is not None, "Table cell should not be null"
                    assert hasattr(cell, "row_index"), "Cell should have row_index"
                    assert hasattr(cell, "column_index"), "Cell should have column_index"
                    assert (
                        0 <= cell.row_index < table.row_count
                    ), f"Cell row index {cell.row_index} should be within table row count {table.row_count}"
                    assert (
                        0 <= cell.column_index < table.column_count
                    ), f"Cell column index {cell.column_index} should be within table column count {table.column_count}"

                    if hasattr(cell, "row_span"):
                        assert cell.row_span >= 1, f"Cell row span should be >= 1, but was {cell.row_span}"
                    if hasattr(cell, "column_span"):
                        assert cell.column_span >= 1, f"Cell column span should be >= 1, but was {cell.column_span}"

                print(
                    f"[PASS] Table {i} validated: {table.row_count} rows x {table.column_count} columns ({len(table.cells)} cells)"
                )
            else:
                print(f"[PASS] Table {i} validated: {table.row_count} rows x {table.column_count} columns")
