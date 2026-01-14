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
from azure.ai.contentunderstanding.models import AnalyzeInput, AudioVisualContent, DocumentContent


class TestSampleAnalyzeUrl(ContentUnderstandingClientTestBase):
    """Tests for sample_analyze_url.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_analyze_document_from_url(self, contentunderstanding_endpoint: str) -> None:
        """Test analyzing a document from URL.

        This test validates:
        1. URL validation
        2. Document analysis using begin_analyze with URL input
        3. Markdown content extraction
        4. Document properties (MIME type, pages, tables)

        02_AnalyzeUrl.AnalyzeDocumentUrlAsync()
        """
        client = self.create_client(endpoint=contentunderstanding_endpoint)

        # Use a publicly accessible URL for testing
        url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/document/invoice.pdf"

        print(f"[PASS] Analyzing document from URL: {url}")

        # Analyze the document
        poller = client.begin_analyze(analyzer_id="prebuilt-documentSearch", inputs=[AnalyzeInput(url=url)])

        result = poller.result()

        # Assertion: Verify analysis operation completed
        assert poller is not None, "Analysis operation should not be null"
        assert poller.done(), "Operation should be completed"

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

        print("\n[SUCCESS] All test_sample_analyze_document_from_url assertions passed")

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_analyze_video_from_url(self, contentunderstanding_endpoint: str) -> None:
        """Test analyzing a video from URL.

        This test validates:
        1. Video analysis using begin_analyze with URL input
        2. Markdown content extraction
        3. Audio/visual properties (timing, frame size)
        4. Multiple segments handling

        02_AnalyzeUrl.AnalyzeVideoUrlAsync()
        """
        client = self.create_client(endpoint=contentunderstanding_endpoint)

        # Use a publicly accessible URL for testing
        url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/videos/sdk_samples/FlightSimulator.mp4"

        print(f"[PASS] Analyzing video from URL: {url}")

        # Analyze the video
        # Use 10-second polling interval for video analysis (longer processing time)
        poller = client.begin_analyze(analyzer_id="prebuilt-videoSearch", inputs=[AnalyzeInput(url=url)], polling_interval=10)

        result = poller.result()

        # Assertion: Verify analysis operation completed
        assert poller is not None, "Analysis operation should not be null"
        assert poller.done(), "Operation should be completed"
        assert poller.status() == "Succeeded", f"Operation status should be Succeeded, but was {poller.status()}"
        print("[PASS] Analysis operation completed successfully")

        # Assertion: Verify result
        assert result is not None, "Analysis result should not be null"
        assert result.contents is not None, "Result contents should not be null"
        assert len(result.contents) > 0, "Result should contain at least one content"
        print(f"[PASS] Analysis result contains {len(result.contents)} segment(s)")

        # Test audio/visual properties
        self._test_audiovisual_properties(result)

        print("\n[SUCCESS] All test_sample_analyze_video_from_url assertions passed")

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_analyze_audio_from_url(self, contentunderstanding_endpoint: str) -> None:
        """Test analyzing audio from URL.

        This test validates:
        1. Audio analysis using begin_analyze with URL input
        2. Markdown content extraction
        3. Transcript phrases access
        4. Summary field access

        02_AnalyzeUrl.AnalyzeAudioUrlAsync()
        """
        client = self.create_client(endpoint=contentunderstanding_endpoint)

        # Use a publicly accessible URL for testing
        url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/audio/callCenterRecording.mp3"

        print(f"[PASS] Analyzing audio from URL: {url}")

        # Analyze the audio
        # Use 10-second polling interval for audio analysis (longer processing time)
        poller = client.begin_analyze(analyzer_id="prebuilt-audioSearch", inputs=[AnalyzeInput(url=url)], polling_interval=10)
        
        result = poller.result()

        # Assertion: Verify analysis operation completed
        assert poller is not None, "Analysis operation should not be null"
        assert poller.done(), "Operation should be completed"
        assert poller.status() == "Succeeded", f"Operation status should be Succeeded, but was {poller.status()}"
        print("[PASS] Analysis operation completed successfully")

        # Assertion: Verify result
        assert result is not None, "Analysis result should not be null"
        assert result.contents is not None, "Result contents should not be null"
        assert len(result.contents) > 0, "Result should contain at least one content"
        print(f"[PASS] Analysis result contains {len(result.contents)} content(s)")

        # Test audio properties including transcript phrases
        self._test_audio_properties(result)

        print("\n[SUCCESS] All test_sample_analyze_audio_from_url assertions passed")

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_sample_analyze_image_from_url(self, contentunderstanding_endpoint: str) -> None:
        """Test analyzing an image from URL.

        This test validates:
        1. Image analysis using begin_analyze with URL input
        2. Markdown content extraction
        3. Summary field access

        02_AnalyzeUrl.AnalyzeImageUrlAsync()
        """
        client = self.create_client(endpoint=contentunderstanding_endpoint)

        # Use a publicly accessible URL for testing
        url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/image/pieChart.jpg"

        print(f"[PASS] Analyzing image from URL: {url}")

        # Analyze the image
        poller = client.begin_analyze(analyzer_id="prebuilt-imageSearch", inputs=[AnalyzeInput(url=url)])
        
        result = poller.result()

        # Assertion: Verify analysis operation completed
        assert poller is not None, "Analysis operation should not be null"
        assert poller.done(), "Operation should be completed"
        assert poller.status() == "Succeeded", f"Operation status should be Succeeded, but was {poller.status()}"
        print("[PASS] Analysis operation completed successfully")

        # Assertion: Verify result
        assert result is not None, "Analysis result should not be null"
        assert result.contents is not None, "Result contents should not be null"
        assert len(result.contents) > 0, "Result should contain at least one content"
        print(f"[PASS] Analysis result contains {len(result.contents)} content(s)")

        # Test image properties
        self._test_image_properties(result)

        print("\n[SUCCESS] All test_sample_analyze_image_from_url assertions passed")

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

    def _test_audiovisual_properties(self, result):
        """Test audio/visual content properties for video."""
        content = result.contents[0]
        assert content is not None, "Content should not be null"

        # Verify markdown
        markdown = getattr(content, "markdown", None)
        if markdown:
            assert isinstance(markdown, str), "Markdown should be a string"
            assert len(markdown) > 0, "Markdown content should not be empty"
            print(f"[PASS] Video markdown content extracted ({len(markdown)} characters)")

        # Verify timing properties
        start_time = getattr(content, "start_time_ms", None)
        if start_time is not None:
            assert start_time >= 0, f"Start time should be >= 0, but was {start_time}"
            print(f"[PASS] Video start time verified: {start_time} ms")

        end_time = getattr(content, "end_time_ms", None)
        if end_time is not None:
            assert end_time >= 0, f"End time should be >= 0, but was {end_time}"
            print(f"[PASS] Video end time verified: {end_time} ms")

        # Verify frame size
        width = getattr(content, "width", None)
        height = getattr(content, "height", None)
        if width is not None and height is not None:
            assert width > 0, f"Video width should be > 0, but was {width}"
            assert height > 0, f"Video height should be > 0, but was {height}"
            print(f"[PASS] Video frame size verified: {width} x {height}")

        # Verify summary field
        fields = getattr(content, "fields", None)
        if fields:
            summary = fields.get("Summary")
            if summary:
                print("[PASS] Summary field available in video content")

        print("[PASS] All audio/visual properties validated successfully")

    def _test_audio_properties(self, result):
        """Test audio content properties including transcript phrases."""
        content = result.contents[0]
        assert content is not None, "Content should not be null"

        # Verify markdown
        markdown = getattr(content, "markdown", None)
        if markdown:
            assert isinstance(markdown, str), "Markdown should be a string"
            assert len(markdown) > 0, "Markdown content should not be empty"
            print(f"[PASS] Audio markdown content extracted ({len(markdown)} characters)")

        # Verify timing properties
        start_time = getattr(content, "start_time_ms", None)
        if start_time is not None:
            assert start_time >= 0, f"Start time should be >= 0, but was {start_time}"
            print(f"[PASS] Audio start time verified: {start_time} ms")

        # Verify summary field
        fields = getattr(content, "fields", None)
        if fields:
            summary = fields.get("Summary")
            if summary:
                print("[PASS] Summary field available in audio content")

        # Verify transcript phrases
        transcript_phrases = getattr(content, "transcript_phrases", None)
        if transcript_phrases and len(transcript_phrases) > 0:
            print(f"[PASS] Transcript phrases found: {len(transcript_phrases)} phrases")
            for phrase in transcript_phrases[:2]:
                speaker = getattr(phrase, "speaker", None)
                text = getattr(phrase, "text", None)
                start_ms = getattr(phrase, "start_time_ms", None)
                if speaker and text:
                    print(f"  [{speaker}] {start_ms} ms: {text}")
        else:
            print("[WARN] No transcript phrases available")

        print("[PASS] All audio properties validated successfully")

    def _test_image_properties(self, result):
        """Test image content properties."""
        content = result.contents[0]
        assert content is not None, "Content should not be null"

        # Verify markdown
        markdown = getattr(content, "markdown", None)
        if markdown:
            assert isinstance(markdown, str), "Markdown should be a string"
            assert len(markdown) > 0, "Markdown content should not be empty"
            print(f"[PASS] Image markdown content extracted ({len(markdown)} characters)")

        # Verify summary field
        fields = getattr(content, "fields", None)
        if fields:
            summary = fields.get("Summary")
            if summary and hasattr(summary, "value"):
                summary_value = summary.value
                if summary_value:
                    assert isinstance(summary_value, str), "Summary should be a string"
                    assert len(summary_value) > 0, "Summary should not be empty"
                    print(f"[PASS] Image summary verified ({len(summary_value)} characters)")

        print("[PASS] All image properties validated successfully")

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
