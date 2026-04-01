# pylint: disable=line-too-long,useless-suppression
# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_analyze_binary_async.py

DESCRIPTION:
    These tests validate the sample_analyze_binary.py sample code (async version).
    
    This sample demonstrates how to analyze a PDF file from disk using the `prebuilt-documentSearch`
    analyzer. The service returns an AnalysisResult that contains an array of AnalysisContent items
    in AnalysisResult.contents. For documents, each item is a DocumentContent that exposes markdown
    plus detailed structure such as pages, tables, figures, and paragraphs.
    
    The prebuilt-documentSearch analyzer transforms unstructured documents into structured, machine-
    readable data optimized for RAG scenarios. It extracts rich GitHub Flavored Markdown that preserves
    document structure and can include: structured text, tables (in HTML format), charts and diagrams,
    mathematical formulas, hyperlinks, barcodes, annotations, and page metadata.
    
    Content Understanding supports many document types including PDF, Word, Excel, PowerPoint, images
    (including scanned image files with hand-written text), and more.

USAGE:
    pytest test_sample_analyze_binary_async.py
"""

import os
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from testpreparer_async import ContentUnderstandingPreparer, ContentUnderstandingClientTestBaseAsync
from azure.ai.contentunderstanding.models import DocumentContent


class TestSampleAnalyzeBinaryAsync(ContentUnderstandingClientTestBaseAsync):
    """Tests for sample_analyze_binary.py (async version)"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_analyze_binary_async(self, contentunderstanding_endpoint: str) -> None:
        """Test analyzing a document from binary data (async version).

        This test validates:
        1. File loading and binary data creation
        2. Document analysis using begin_analyze_binary
        3. Markdown content extraction
        4. Document properties (MIME type, pages, tables)

        """
        client = self.create_async_client(endpoint=contentunderstanding_endpoint)

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

        # Assertion: Verify binary data
        assert file_bytes is not None, "Binary data should not be null"
        print("[PASS] Binary data created successfully")

        # Analyze the document
        poller = await client.begin_analyze_binary(analyzer_id="prebuilt-documentSearch", binary_input=file_bytes)

        result = await poller.result()

        # Assertion: Verify analysis operation completed
        assert poller is not None, "Analysis operation should not be null"
        assert poller.done(), "Operation should be completed"
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

        await client.close()
        print("\n[SUCCESS] All test_sample_analyze_binary_async assertions passed")

    def _test_markdown_extraction(self, result):
        """Test markdown content extraction."""
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
        """Test document property access."""
        content = result.contents[0]
        assert content is not None, "Content should not be null for document properties validation"

        # Check if this is DocumentContent
        content_type = type(content).__name__
        print(f"[INFO] Content type: {content_type}")

        # Validate this is document content (should have document-specific properties)
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

                # Validate pages collection
                pages = getattr(content, "pages", None)
                if pages and len(pages) > 0:
                    assert len(pages) > 0, "Pages collection should not be empty when not null"
                    assert (
                        len(pages) == total_pages
                    ), f"Pages collection count {len(pages)} should match calculated total pages {total_pages}"
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

        # Final validation message
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

            # Ensure page numbers are unique
            assert page.page_number not in page_numbers, f"Page number {page.page_number} appears multiple times"
            page_numbers.add(page.page_number)

            # Print page details with unit
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

            # Validate table cells if available
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

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_analyze_binary_with_content_range_async(self, contentunderstanding_endpoint: str) -> None:
        """Test analyzing a document from binary data with content range strings (async version).

        This test validates:
        1. "2" — single page
        2. "1-3" — page range
        3. "1,3-4" — combined page ranges
        4. "3-" — analyze pages 3 onward
        5. "1-3,5,9-" — analyze disjoint page ranges

        01_AnalyzeBinary.AnalyzeBinaryWithPageContentRangesAsync()
        """
        client = self.create_async_client(endpoint=contentunderstanding_endpoint)

        # Read the sample file (use multi-page document for content range testing)
        tests_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(tests_dir, "test_data", "mixed_financial_invoices.pdf")
        assert os.path.exists(file_path), (
            f"Required multi-page test file not found: {file_path}. "
            "This test requires 'mixed_financial_invoices.pdf' to validate content range scenarios."
        )

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        # Full analysis for comparison
        full_poller = await client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch", binary_input=file_bytes
        )
        full_result = await full_poller.result()
        assert full_result.contents is not None
        full_doc = full_result.contents[0]
        assert isinstance(full_doc, DocumentContent)
        full_page_count = len(full_doc.pages) if full_doc.pages else 0
        print(f"[PASS] Full document: {full_page_count} pages, {len(full_doc.markdown or '')} chars")

        # "2" — single page
        print("\nAnalyzing page 2 only with content range '2'...")
        page2_poller = await client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=file_bytes,
            content_range="2",
        )
        page2_result = await page2_poller.result()
        assert page2_result.contents is not None
        page2_doc = page2_result.contents[0]
        assert isinstance(page2_doc, DocumentContent)
        page2_page_count = len(page2_doc.pages) if page2_doc.pages else 0
        assert page2_page_count == 1, f"'2' should return exactly 1 page, got {page2_page_count}"
        assert page2_doc.start_page_number == 2, f"'2' should start at page 2, got {page2_doc.start_page_number}"
        assert page2_doc.end_page_number == 2, f"'2' should end at page 2, got {page2_doc.end_page_number}"
        assert page2_doc.pages[0].page_number == 2, (
            f"'2' page[0].page_number should be 2, got {page2_doc.pages[0].page_number}"
        )
        print(f"[PASS] '2': {page2_page_count} page, page number: {page2_doc.pages[0].page_number}")

        # "1-3" — page range
        print("\nAnalyzing pages 1-3 with content range '1-3'...")
        pages13_poller = await client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=file_bytes,
            content_range="1-3",
        )
        pages13_result = await pages13_poller.result()
        assert pages13_result.contents is not None
        pages13_doc = pages13_result.contents[0]
        assert isinstance(pages13_doc, DocumentContent)
        pages13_page_count = len(pages13_doc.pages) if pages13_doc.pages else 0
        assert pages13_page_count == 3, f"'1-3' should return exactly 3 pages, got {pages13_page_count}"
        assert pages13_doc.start_page_number == 1, f"'1-3' should start at page 1, got {pages13_doc.start_page_number}"
        assert pages13_doc.end_page_number == 3, f"'1-3' should end at page 3, got {pages13_doc.end_page_number}"
        actual_pages13 = sorted([p.page_number for p in pages13_doc.pages])
        assert actual_pages13 == [1, 2, 3], (
            f"'1-3' page numbers should be [1, 2, 3], got {actual_pages13}"
        )
        print(f"[PASS] '1-3': {pages13_page_count} pages, page numbers: {actual_pages13}")

        # "1,3-4" — combined page ranges
        print("\nAnalyzing combined pages (1, 3-4) with content range '1,3-4'...")
        combine2_poller = await client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=file_bytes,
            content_range="1,3-4",
        )
        combine2_result = await combine2_poller.result()
        assert combine2_result.contents is not None
        combine2_doc = combine2_result.contents[0]
        assert isinstance(combine2_doc, DocumentContent)
        combine2_page_count = len(combine2_doc.pages) if combine2_doc.pages else 0
        assert combine2_page_count == 3, (
            f"'1,3-4' should return exactly 3 pages, got {combine2_page_count}"
        )
        assert combine2_doc.start_page_number == 1, f"'1,3-4' should start at page 1, got {combine2_doc.start_page_number}"
        assert combine2_doc.end_page_number == 4, f"'1,3-4' should end at page 4, got {combine2_doc.end_page_number}"
        actual_combine2_pages = sorted([p.page_number for p in combine2_doc.pages])
        assert actual_combine2_pages == [1, 3, 4], (
            f"'1,3-4' page numbers should be [1, 3, 4], got {actual_combine2_pages}"
        )
        print(f"[PASS] '1,3-4': {combine2_page_count} pages, page numbers: {actual_combine2_pages}")

        # "3-" — pages 3 onward
        print("\nAnalyzing pages 3 onward with content range '3-'...")
        range_poller = await client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=file_bytes,
            content_range="3-",
        )
        range_result = await range_poller.result()
        assert range_result.contents is not None
        range_doc = range_result.contents[0]
        assert isinstance(range_doc, DocumentContent)
        expected_range_page_count = full_page_count - 2
        range_page_count = len(range_doc.pages) if range_doc.pages else 0
        assert range_page_count == expected_range_page_count, (
            f"'3-' should return exactly {expected_range_page_count} pages, got {range_page_count}"
        )
        assert range_doc.start_page_number == 3, f"'3-' should start at page 3, got {range_doc.start_page_number}"
        assert range_doc.end_page_number == full_doc.end_page_number, (
            f"'3-' should end at page {full_doc.end_page_number}, got {range_doc.end_page_number}"
        )
        expected_range_pages = list(range(3, full_doc.end_page_number + 1))
        actual_range_pages = sorted([p.page_number for p in range_doc.pages])
        assert actual_range_pages == expected_range_pages, (
            f"'3-' page numbers should be {expected_range_pages}, got {actual_range_pages}"
        )
        print(f"[PASS] '3-': {range_page_count} pages (pages {range_doc.start_page_number}-{range_doc.end_page_number})")

        # "1-3,5,9-" — combined ranges
        print("\nAnalyzing combined pages (1-3, 5, 9-) with content range '1-3,5,9-'...")
        combine_poller = await client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=file_bytes,
            content_range="1-3,5,9-",
        )
        combine_result = await combine_poller.result()
        assert combine_result.contents is not None
        combine_doc = combine_result.contents[0]
        assert isinstance(combine_doc, DocumentContent)
        # Expected pages: 1, 2, 3, 5, 9, 10, ..., N => count = 3 + 1 + (N - 8) = N - 4
        expected_combine_page_count = full_page_count - 4
        combine_page_count = len(combine_doc.pages) if combine_doc.pages else 0
        assert combine_page_count == expected_combine_page_count, (
            f"'1-3,5,9-' should return exactly {expected_combine_page_count} pages, got {combine_page_count}"
        )
        expected_combine_pages = [1, 2, 3, 5] + list(range(9, full_doc.end_page_number + 1))
        actual_combine_pages = sorted([p.page_number for p in combine_doc.pages])
        assert actual_combine_pages == expected_combine_pages, (
            f"'1-3,5,9-' page numbers should be {expected_combine_pages}, got {actual_combine_pages}"
        )
        assert combine_doc.start_page_number == 1, (
            f"'1-3,5,9-' should start at page 1, got {combine_doc.start_page_number}"
        )
        assert combine_doc.end_page_number == full_doc.end_page_number, (
            f"'1-3,5,9-' should end at page {full_doc.end_page_number}, got {combine_doc.end_page_number}"
        )
        print(f"[PASS] '1-3,5,9-': {combine_page_count} pages, page numbers: {actual_combine_pages}")

        await client.close()
        print("\n[SUCCESS] All content range binary async test assertions passed")
