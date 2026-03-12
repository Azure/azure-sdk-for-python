# pylint: disable=line-too-long,useless-suppression
# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_analyze_binary.py

DESCRIPTION:
    These tests validate the sample_analyze_binary.py sample code.
    
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
    pytest test_sample_analyze_binary.py
"""

import os
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import ContentUnderstandingPreparer, ContentUnderstandingClientTestBase
from azure.ai.contentunderstanding.models import ContentRange, DocumentContent


class TestSampleAnalyzeBinary(ContentUnderstandingClientTestBase):
    """Tests for sample_analyze_binary.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_analyze_binary(self, contentunderstanding_endpoint: str) -> None:
        """Test analyzing a document from binary data.

        This test validates:
        1. File loading and binary data creation
        2. Document analysis using begin_analyze_binary
        3. Markdown content extraction
        4. Document properties (MIME type, pages, tables)

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

        # Assertion: Verify binary data
        assert file_bytes is not None, "Binary data should not be null"
        print("[PASS] Binary data created successfully")

        # Analyze the document
        poller = client.begin_analyze_binary(analyzer_id="prebuilt-documentSearch", binary_input=file_bytes)

        result = poller.result()

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

        print("\n[SUCCESS] All test_sample_analyze_binary assertions passed")

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
    @recorded_by_proxy
    def test_sample_analyze_binary_with_content_range(self, contentunderstanding_endpoint: str) -> None:
        """Test analyzing a document from binary data with ContentRange.

        This test validates:
        1. ContentRange.pages_from(3) — analyze pages 3 onward
        2. ContentRange.combine() — analyze disjoint page ranges
        3. ContentRange.page(2) — single page
        4. ContentRange.pages(1, 3) — page range
        5. ContentRange.combine(page(1), pages(3, 4)) — combined page ranges

        01_AnalyzeBinary.AnalyzeBinaryWithPageContentRangesAsync()
        """
        client = self.create_client(endpoint=contentunderstanding_endpoint)

        # Read the sample file (use multi-page document for ContentRange testing)
        tests_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(tests_dir, "test_data", "mixed_financial_docs.pdf")
        if not os.path.exists(file_path):
            file_path = os.path.join(tests_dir, "test_data", "sample_invoice.pdf")

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        # Full analysis for comparison
        full_poller = client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch", binary_input=file_bytes
        )
        full_result = full_poller.result()
        assert full_result.contents is not None
        full_doc = full_result.contents[0]
        assert isinstance(full_doc, DocumentContent)
        full_page_count = len(full_doc.pages) if full_doc.pages else 0
        print(f"[PASS] Full document: {full_page_count} pages, {len(full_doc.markdown or '')} chars")

        # ContentRange.pages_from(3) — pages 3 onward (wire format: "3-")
        print("\nAnalyzing pages 3 onward with ContentRange.pages_from(3)...")
        range_poller = client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=file_bytes,
            content_range=ContentRange.pages_from(3),
        )
        range_result = range_poller.result()
        assert range_result.contents is not None
        range_doc = range_result.contents[0]
        assert isinstance(range_doc, DocumentContent)
        range_page_count = len(range_doc.pages) if range_doc.pages else 0
        assert range_page_count > 0, "PagesFrom(3) should return at least one page"
        assert full_page_count >= range_page_count, (
            f"Full document ({full_page_count} pages) should have >= pages than range-limited ({range_page_count})"
        )
        print(f"[PASS] PagesFrom(3): {range_page_count} pages (pages {range_doc.start_page_number}-{range_doc.end_page_number})")

        # ContentRange.combine(pages(1, 3), page(5), pages_from(9)) — combined (wire format: "1-3,5,9-")
        print("\nAnalyzing combined pages (1-3, 5, 9-) with ContentRange.combine()...")
        combine_poller = client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=file_bytes,
            content_range=ContentRange.combine(
                ContentRange.pages(1, 3),
                ContentRange.page(5),
                ContentRange.pages_from(9),
            ),
        )
        combine_result = combine_poller.result()
        assert combine_result.contents is not None
        combine_doc = combine_result.contents[0]
        assert isinstance(combine_doc, DocumentContent)
        combine_page_count = len(combine_doc.pages) if combine_doc.pages else 0
        assert combine_page_count > 0, "Combine should return at least one page"
        assert len(full_doc.markdown or '') >= len(combine_doc.markdown or ''), (
            f"Full document ({len(full_doc.markdown or '')} chars) should be >= Combine ({len(combine_doc.markdown or '')} chars)"
        )
        print(f"[PASS] Combine(Pages(1,3), Page(5), PagesFrom(9)): {combine_page_count} pages")

        # ContentRange.page(2) — single page (wire format: "2")
        print("\nAnalyzing page 2 only with ContentRange.page(2)...")
        page2_poller = client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=file_bytes,
            content_range=ContentRange.page(2),
        )
        page2_result = page2_poller.result()
        assert page2_result.contents is not None
        page2_doc = page2_result.contents[0]
        assert isinstance(page2_doc, DocumentContent)
        page2_page_count = len(page2_doc.pages) if page2_doc.pages else 0
        assert page2_page_count == 1, f"Page(2) should return exactly 1 page, got {page2_page_count}"
        assert page2_doc.start_page_number == 2, f"Page(2) should start at page 2, got {page2_doc.start_page_number}"
        assert page2_doc.end_page_number == 2, f"Page(2) should end at page 2, got {page2_doc.end_page_number}"
        print(f"[PASS] Page(2): {page2_page_count} page, {len(page2_doc.markdown or '')} chars")

        # ContentRange.pages(1, 3) — page range (wire format: "1-3")
        print("\nAnalyzing pages 1-3 with ContentRange.pages(1, 3)...")
        pages13_poller = client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=file_bytes,
            content_range=ContentRange.pages(1, 3),
        )
        pages13_result = pages13_poller.result()
        assert pages13_result.contents is not None
        pages13_doc = pages13_result.contents[0]
        assert isinstance(pages13_doc, DocumentContent)
        pages13_page_count = len(pages13_doc.pages) if pages13_doc.pages else 0
        assert pages13_page_count == 3, f"Pages(1,3) should return exactly 3 pages, got {pages13_page_count}"
        assert pages13_doc.start_page_number == 1, f"Pages(1,3) should start at page 1, got {pages13_doc.start_page_number}"
        assert pages13_doc.end_page_number == 3, f"Pages(1,3) should end at page 3, got {pages13_doc.end_page_number}"
        print(f"[PASS] Pages(1,3): {pages13_page_count} pages, {len(pages13_doc.markdown or '')} chars")

        # ContentRange.combine(page(1), pages(3, 4)) — combined (wire format: "1,3-4")
        print("\nAnalyzing combined pages (1, 3-4) with ContentRange.combine()...")
        combine2_poller = client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=file_bytes,
            content_range=ContentRange.combine(
                ContentRange.page(1),
                ContentRange.pages(3, 4),
            ),
        )
        combine2_result = combine2_poller.result()
        assert combine2_result.contents is not None
        combine2_doc = combine2_result.contents[0]
        assert isinstance(combine2_doc, DocumentContent)
        combine2_page_count = len(combine2_doc.pages) if combine2_doc.pages else 0
        assert combine2_page_count >= 2, (
            f"Combine(Page(1), Pages(3,4)) should return at least 2 pages, got {combine2_page_count}"
        )
        assert combine2_doc.start_page_number == 1, f"Combine should start at page 1, got {combine2_doc.start_page_number}"
        print(f"[PASS] Combine(Page(1), Pages(3,4)): {combine2_page_count} pages, {len(combine2_doc.markdown or '')} chars")

        print("\n[SUCCESS] All ContentRange binary test assertions passed")
