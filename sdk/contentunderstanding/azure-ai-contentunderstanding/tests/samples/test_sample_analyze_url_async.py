# pylint: disable=line-too-long,useless-suppression
# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_analyze_url_async.py

DESCRIPTION:
    These tests validate the sample_analyze_url.py sample code (async version).
    This sample demonstrates prebuilt RAG analyzers with URL inputs. Content Understanding supports
    both local binary inputs (see sample_analyze_binary_async.py) and URL inputs across all modalities.
    For URL inputs, use begin_analyze() with AnalysisInput objects that wrap the URL.

USAGE:
    pytest test_sample_analyze_url_async.py
"""

import os
import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from testpreparer_async import ContentUnderstandingPreparer, ContentUnderstandingClientTestBaseAsync
from azure.ai.contentunderstanding.models import AnalysisInput, AudioVisualContent, DocumentContent


class TestSampleAnalyzeUrlAsync(ContentUnderstandingClientTestBaseAsync):
    """Tests for sample_analyze_url_async.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_analyze_document_from_url_async(self, contentunderstanding_endpoint: str) -> None:
        """Test analyzing a document from URL (async version).

        This test validates:
        1. URL validation
        2. Document analysis using begin_analyze with URL input
        3. Markdown content extraction
        4. Document properties (MIME type, pages, tables)

        02_AnalyzeUrl.AnalyzeDocumentUrlAsync()
        """
        client = self.create_async_client(endpoint=contentunderstanding_endpoint)

        # Use a publicly accessible URL for testing
        url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/document/invoice.pdf"

        print(f"[PASS] Analyzing document from URL: {url}")

        # Analyze the document
        poller = await client.begin_analyze(analyzer_id="prebuilt-documentSearch", inputs=[AnalysisInput(url=url)])

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
        print("\n[SUCCESS] All test_sample_analyze_document_from_url_async assertions passed")

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_analyze_video_from_url_async(self, contentunderstanding_endpoint: str) -> None:
        """Test analyzing a video from URL (async version).

        This test validates:
        1. Video analysis using begin_analyze with URL input
        2. Markdown content extraction
        3. Audio/visual properties (timing, frame size)
        4. Multiple segments handling

        02_AnalyzeUrl.AnalyzeVideoUrlAsync()
        """
        client = self.create_async_client(endpoint=contentunderstanding_endpoint)

        # Use a publicly accessible URL for testing
        url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/videos/sdk_samples/FlightSimulator.mp4"

        print(f"[PASS] Analyzing video from URL: {url}")

        # Analyze the video
        # Use 10-second polling interval for video analysis (longer processing time)
        poller = await client.begin_analyze(
            analyzer_id="prebuilt-videoSearch", inputs=[AnalysisInput(url=url)], polling_interval=10
        )

        result = await poller.result()

        # Assertion: Verify analysis operation completed
        assert poller is not None, "Analysis operation should not be null"
        assert poller.done(), "Operation should be completed"
        print("[PASS] Analysis operation completed successfully")

        # Assertion: Verify result
        assert result is not None, "Analysis result should not be null"
        assert result.contents is not None, "Result contents should not be null"
        assert len(result.contents) > 0, "Result should contain at least one content"
        print(f"[PASS] Analysis result contains {len(result.contents)} segment(s)")

        # Test audio/visual properties
        self._test_audiovisual_properties(result)

        await client.close()
        print("\n[SUCCESS] All test_sample_analyze_video_from_url_async assertions passed")

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_analyze_audio_from_url_async(self, contentunderstanding_endpoint: str) -> None:
        """Test analyzing audio from URL (async version).

        This test validates:
        1. Audio analysis using begin_analyze with URL input
        2. Markdown content extraction
        3. Transcript phrases access
        4. Summary field access

        02_AnalyzeUrl.AnalyzeAudioUrlAsync()
        """
        client = self.create_async_client(endpoint=contentunderstanding_endpoint)

        # Use a publicly accessible URL for testing
        url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/audio/callCenterRecording.mp3"

        print(f"[PASS] Analyzing audio from URL: {url}")

        # Analyze the audio
        # Use 10-second polling interval for audio analysis (longer processing time)
        poller = await client.begin_analyze(
            analyzer_id="prebuilt-audioSearch", inputs=[AnalysisInput(url=url)], polling_interval=10
        )

        result = await poller.result()

        # Assertion: Verify analysis operation completed
        assert poller is not None, "Analysis operation should not be null"
        assert poller.done(), "Operation should be completed"
        print("[PASS] Analysis operation completed successfully")

        # Assertion: Verify result
        assert result is not None, "Analysis result should not be null"
        assert result.contents is not None, "Result contents should not be null"
        assert len(result.contents) > 0, "Result should contain at least one content"
        print(f"[PASS] Analysis result contains {len(result.contents)} content(s)")

        # Test audio properties including transcript phrases
        self._test_audio_properties(result)

        await client.close()
        print("\n[SUCCESS] All test_sample_analyze_audio_from_url_async assertions passed")

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_analyze_image_from_url_async(self, contentunderstanding_endpoint: str) -> None:
        """Test analyzing an image from URL (async version).

        This test validates:
        1. Image analysis using begin_analyze with URL input
        2. Markdown content extraction
        3. Summary field access

        02_AnalyzeUrl.AnalyzeImageUrlAsync()
        """
        client = self.create_async_client(endpoint=contentunderstanding_endpoint)

        # Use a publicly accessible URL for testing
        url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/image/pieChart.jpg"

        print(f"[PASS] Analyzing image from URL: {url}")

        # Analyze the image
        poller = await client.begin_analyze(analyzer_id="prebuilt-imageSearch", inputs=[AnalysisInput(url=url)])

        result = await poller.result()

        # Assertion: Verify analysis operation completed
        assert poller is not None, "Analysis operation should not be null"
        assert poller.done(), "Operation should be completed"
        print("[PASS] Analysis operation completed successfully")

        # Assertion: Verify result
        assert result is not None, "Analysis result should not be null"
        assert result.contents is not None, "Result contents should not be null"
        assert len(result.contents) > 0, "Result should contain at least one content"
        print(f"[PASS] Analysis result contains {len(result.contents)} content(s)")

        # Test image properties
        self._test_image_properties(result)

        await client.close()
        print("\n[SUCCESS] All test_sample_analyze_image_from_url_async assertions passed")

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

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_analyze_document_url_with_content_range_async(
        self, contentunderstanding_endpoint: str
    ) -> None:
        """Test analyzing a document URL with content range strings (async version).

        This test validates:
        1. "1" — single page extraction
        2. "1-3,5,9-" — combined disjoint page ranges
        3. Comparison between full document and range-limited result

        02_AnalyzeUrl.AnalyzeUrlWithPageContentRangesAsync()
        """
        from typing import cast

        client = self.create_async_client(endpoint=contentunderstanding_endpoint)

        url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/document/mixed_financial_invoices.pdf"

        # Full analysis for comparison
        full_poller = await client.begin_analyze(
            analyzer_id="prebuilt-documentSearch", inputs=[AnalysisInput(url=url)]
        )
        full_result = await full_poller.result()
        full_doc = cast(DocumentContent, full_result.contents[0])
        full_page_count = len(full_doc.pages) if full_doc.pages else 0
        assert full_page_count == 10, f"Full document should return all 10 pages, got {full_page_count}"
        print(f"[PASS] Full document: {full_page_count} pages, {len(full_doc.markdown or '')} chars")

        # "1" — single page
        print("\nAnalyzing page 1 only with content range '1'...")
        range_poller = await client.begin_analyze(
            analyzer_id="prebuilt-documentSearch",
            inputs=[AnalysisInput(url=url, content_range="1")],
        )
        range_result = await range_poller.result()
        range_doc = cast(DocumentContent, range_result.contents[0])
        range_page_count = len(range_doc.pages) if range_doc.pages else 0
        assert range_page_count == 1, f"'1' should return only 1 page, got {range_page_count}"
        assert range_doc.start_page_number == 1, f"'1' should start at page 1, got {range_doc.start_page_number}"
        assert range_doc.end_page_number == 1, f"'1' should end at page 1, got {range_doc.end_page_number}"

        # Compare full vs range-limited
        assert full_page_count > range_page_count, (
            f"Full document ({full_page_count} pages) should have more pages than range-limited ({range_page_count})"
        )
        assert len(full_doc.markdown or '') > len(range_doc.markdown or ''), (
            f"Full document markdown ({len(full_doc.markdown or '')} chars) should exceed range-limited ({len(range_doc.markdown or '')} chars)"
        )
        print(f"[PASS] '1': {range_page_count} page, {len(range_doc.markdown or '')} chars")

        # "1-3,5,9-" — combined disjoint page ranges
        # Document has 10 pages, so pages 1-3, 5, 9-10 match (6 pages total)
        print("\nAnalyzing combined pages (1-3, 5, 9-) with content range '1-3,5,9-'...")
        combine_poller = await client.begin_analyze(
            analyzer_id="prebuilt-documentSearch",
            inputs=[AnalysisInput(url=url, content_range="1-3,5,9-")],
        )
        combine_result = await combine_poller.result()
        combine_doc = cast(DocumentContent, combine_result.contents[0])
        combine_page_count = len(combine_doc.pages) if combine_doc.pages else 0
        assert combine_page_count == 6, f"'1-3,5,9-' should return 6 pages (1-3, 5, 9-10), got {combine_page_count}"
        assert combine_doc.start_page_number == 1, (
            f"'1-3,5,9-' should start at page 1, got {combine_doc.start_page_number}"
        )
        assert combine_doc.end_page_number == 10, (
            f"'1-3,5,9-' should end at page 10, got {combine_doc.end_page_number}"
        )
        actual_combine_pages = sorted([p.page_number for p in combine_doc.pages])
        assert actual_combine_pages == [1, 2, 3, 5, 9, 10], (
            f"'1-3,5,9-' page numbers should be [1, 2, 3, 5, 9, 10], got {actual_combine_pages}"
        )
        print(f"[PASS] '1-3,5,9-': {combine_page_count} pages, page numbers: {actual_combine_pages}")

        await client.close()
        print("\n[SUCCESS] All document URL content range async assertions passed")

    @pytest.mark.live_test_only
    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_analyze_video_url_with_content_ranges_async(
        self, contentunderstanding_endpoint: str
    ) -> None:
        """Test analyzing a video URL with various content range string options (async version).

        This test validates:
        1. "0-5000" — first 5 seconds
        2. "10000-" — from 10 seconds onward
        3. "1200-3651" — sub-second precision
        4. "0-3000,30000-" — combined time ranges

        02_AnalyzeUrl.AnalyzeVideoUrlWithTimeContentRangesAsync()
        """
        from typing import cast

        client = self.create_async_client(endpoint=contentunderstanding_endpoint)

        url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/videos/sdk_samples/FlightSimulator.mp4"

        # Full analysis for comparison
        full_poller = await client.begin_analyze(
            analyzer_id="prebuilt-videoSearch",
            inputs=[AnalysisInput(url=url)],
            polling_interval=10,
        )
        full_result = await full_poller.result()
        assert full_result.contents is not None
        assert len(full_result.contents) > 0
        full_segments = [cast(AudioVisualContent, c) for c in full_result.contents]
        full_total_duration = sum(
            (s.end_time_ms or 0) - (s.start_time_ms or 0) for s in full_segments
        )
        print(f"[PASS] Full video: {len(full_segments)} segment(s), {full_total_duration} ms")

        # "0-5000" — first 5 seconds
        print("\nAnalyzing first 5 seconds with content range '0-5000'...")
        range_poller = await client.begin_analyze(
            analyzer_id="prebuilt-videoSearch",
            inputs=[
                AnalysisInput(
                    url=url,
                    content_range="0-5000",
                )
            ],
            polling_interval=10,
        )
        range_result = await range_poller.result()
        assert range_result.contents is not None
        range_segments = [cast(AudioVisualContent, c) for c in range_result.contents]
        assert len(range_segments) > 0, "'0-5000' should return segments"
        for seg in range_segments:
            assert (seg.end_time_ms or 0) > (seg.start_time_ms or 0), "Segment should have EndTime > StartTime"
            assert (seg.start_time_ms or 0) >= 0, (
                f"'0-5000' segment StartTime ({seg.start_time_ms} ms) should be >= 0 ms"
            )
            assert (seg.end_time_ms or 0) <= 5000, (
                f"'0-5000' segment EndTime ({seg.end_time_ms} ms) should be <= 5000 ms"
            )
        print(f"[PASS] '0-5000': {len(range_segments)} segment(s)")

        # "10000-" — from 10 seconds onward
        print("\nAnalyzing from 10 seconds onward with content range '10000-'...")
        from_poller = await client.begin_analyze(
            analyzer_id="prebuilt-videoSearch",
            inputs=[
                AnalysisInput(
                    url=url,
                    content_range="10000-",
                )
            ],
            polling_interval=10,
        )
        from_result = await from_poller.result()
        assert from_result.contents is not None
        from_segments = [cast(AudioVisualContent, c) for c in from_result.contents]
        assert len(from_segments) > 0, "'10000-' should return segments"
        for seg in from_segments:
            assert (seg.end_time_ms or 0) > (seg.start_time_ms or 0), "Segment should have EndTime > StartTime"
            assert seg.markdown, "Segment should have markdown"
            assert (seg.start_time_ms or 0) >= 10000, (
                f"'10000-' segment StartTime ({seg.start_time_ms} ms) should be >= 10000 ms"
            )
        print(f"[PASS] '10000-': {len(from_segments)} segment(s)")

        # "1200-3651" — sub-second precision
        print("\nAnalyzing with sub-second precision (1.2s to 3.651s) with content range '1200-3651'...")
        subsec_poller = await client.begin_analyze(
            analyzer_id="prebuilt-videoSearch",
            inputs=[
                AnalysisInput(
                    url=url,
                    content_range="1200-3651",
                )
            ],
            polling_interval=10,
        )
        subsec_result = await subsec_poller.result()
        assert subsec_result.contents is not None
        subsec_segments = [cast(AudioVisualContent, c) for c in subsec_result.contents]
        assert len(subsec_segments) > 0, "'1200-3651' should return segments"
        for seg in subsec_segments:
            assert (seg.end_time_ms or 0) > (seg.start_time_ms or 0), "Segment should have EndTime > StartTime"
            assert (seg.start_time_ms or 0) >= 1200, (
                f"'1200-3651' segment StartTime ({seg.start_time_ms} ms) should be >= 1200 ms"
            )
            assert (seg.end_time_ms or 0) <= 3651, (
                f"'1200-3651' segment EndTime ({seg.end_time_ms} ms) should be <= 3651 ms"
            )
        print(f"[PASS] '1200-3651': {len(subsec_segments)} segment(s)")

        # "0-3000,30000-" — combined time ranges
        print("\nAnalyzing with combined time ranges (0-3s and 30s onward) with content range '0-3000,30000-'...")
        combine_poller = await client.begin_analyze(
            analyzer_id="prebuilt-videoSearch",
            inputs=[
                AnalysisInput(
                    url=url,
                    content_range="0-3000,30000-",
                )
            ],
            polling_interval=10,
        )
        combine_result = await combine_poller.result()
        assert combine_result.contents is not None
        combine_segments = [cast(AudioVisualContent, c) for c in combine_result.contents]
        assert len(combine_segments) > 0, "'0-3000,30000-' should return segments"
        for seg in combine_segments:
            assert (seg.end_time_ms or 0) > (seg.start_time_ms or 0), "Segment should have EndTime > StartTime"
            assert seg.markdown, "Segment should have markdown"
            seg_start = seg.start_time_ms or 0
            seg_end = seg.end_time_ms or 0
            in_first_range = seg_start >= 0 and seg_end <= 3000
            in_second_range = seg_start >= 30000
            assert in_first_range or in_second_range, (
                f"'0-3000,30000-' segment ({seg_start}-{seg_end} ms) should fall within 0-3000 ms or >= 30000 ms"
            )
        print(f"[PASS] '0-3000,30000-': {len(combine_segments)} segment(s)")

        await client.close()
        print("\n[SUCCESS] All video URL content range async assertions passed")

    @pytest.mark.live_test_only
    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_analyze_audio_url_with_content_ranges_async(
        self, contentunderstanding_endpoint: str
    ) -> None:
        """Test analyzing an audio URL with various content range string options (async version).

        This test validates:
        1. "0-5000" — first 5 seconds
        2. "10000-" — from 10 seconds onward
        3. "1200-3651" — sub-second precision
        4. "0-3000,30000-" — combined time ranges

        02_AnalyzeUrl.AnalyzeAudioUrlWithTimeContentRangesAsync()
        """
        from typing import cast

        client = self.create_async_client(endpoint=contentunderstanding_endpoint)

        url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/audio/callCenterRecording.mp3"

        # Full analysis for comparison
        full_poller = await client.begin_analyze(
            analyzer_id="prebuilt-audioSearch",
            inputs=[AnalysisInput(url=url)],
            polling_interval=10,
        )
        full_result = await full_poller.result()
        assert full_result.contents is not None
        full_audio = cast(AudioVisualContent, full_result.contents[0])
        full_duration = (full_audio.end_time_ms or 0) - (full_audio.start_time_ms or 0)
        print(f"[PASS] Full audio: {len(full_audio.markdown or '')} chars, {full_duration} ms")

        # "0-5000" — first 5 seconds
        print("\nAnalyzing first 5 seconds with content range '0-5000'...")
        range_poller = await client.begin_analyze(
            analyzer_id="prebuilt-audioSearch",
            inputs=[
                AnalysisInput(
                    url=url,
                    content_range="0-5000",
                )
            ],
            polling_interval=10,
        )
        range_result = await range_poller.result()
        assert range_result.contents is not None
        range_audio = cast(AudioVisualContent, range_result.contents[0])
        assert (range_audio.end_time_ms or 0) > (range_audio.start_time_ms or 0), (
            "'0-5000' should have EndTime > StartTime"
        )
        assert (range_audio.start_time_ms or 0) >= 0, (
            f"'0-5000' audio StartTime ({range_audio.start_time_ms} ms) should be >= 0 ms"
        )
        assert (range_audio.end_time_ms or 0) <= 5000, (
            f"'0-5000' audio EndTime ({range_audio.end_time_ms} ms) should be <= 5000 ms"
        )
        assert range_audio.markdown, "'0-5000' should have markdown"
        assert len(range_audio.markdown) > 0, "'0-5000' markdown should not be empty"
        range_duration = (range_audio.end_time_ms or 0) - (range_audio.start_time_ms or 0)
        assert full_duration >= range_duration, (
            f"Full audio duration ({full_duration} ms) should be >= range-limited duration ({range_duration} ms)"
        )
        print(f"[PASS] '0-5000': {len(range_audio.markdown)} chars, {range_duration} ms")

        # "10000-" — from 10 seconds onward
        print("\nAnalyzing audio from 10 seconds onward with content range '10000-'...")
        from_poller = await client.begin_analyze(
            analyzer_id="prebuilt-audioSearch",
            inputs=[
                AnalysisInput(
                    url=url,
                    content_range="10000-",
                )
            ],
            polling_interval=10,
        )
        from_result = await from_poller.result()
        assert from_result.contents is not None
        from_audio = cast(AudioVisualContent, from_result.contents[0])
        assert (from_audio.end_time_ms or 0) > (from_audio.start_time_ms or 0), (
            "'10000-' should have EndTime > StartTime"
        )
        assert (from_audio.start_time_ms or 0) >= 10000, (
            f"'10000-' audio StartTime ({from_audio.start_time_ms} ms) should be >= 10000 ms"
        )
        assert from_audio.markdown, "'10000-' should have markdown"
        print(f"[PASS] '10000-': {len(from_audio.markdown)} chars")

        # "1200-3651" — sub-second precision
        print("\nAnalyzing audio with sub-second precision (1.2s to 3.651s) with content range '1200-3651'...")
        subsec_poller = await client.begin_analyze(
            analyzer_id="prebuilt-audioSearch",
            inputs=[
                AnalysisInput(
                    url=url,
                    content_range="1200-3651",
                )
            ],
            polling_interval=10,
        )
        subsec_result = await subsec_poller.result()
        assert subsec_result.contents is not None
        subsec_audio = cast(AudioVisualContent, subsec_result.contents[0])
        assert (subsec_audio.end_time_ms or 0) > (subsec_audio.start_time_ms or 0), (
            "'1200-3651' should have EndTime > StartTime"
        )
        assert (subsec_audio.start_time_ms or 0) >= 1200, (
            f"'1200-3651' audio StartTime ({subsec_audio.start_time_ms} ms) should be >= 1200 ms"
        )
        assert (subsec_audio.end_time_ms or 0) <= 3651, (
            f"'1200-3651' audio EndTime ({subsec_audio.end_time_ms} ms) should be <= 3651 ms"
        )
        assert subsec_audio.markdown, "'1200-3651' should have markdown"
        assert len(subsec_audio.markdown) > 0, "'1200-3651' markdown should not be empty"
        subsec_duration = (subsec_audio.end_time_ms or 0) - (subsec_audio.start_time_ms or 0)
        assert full_duration >= subsec_duration, (
            f"Full audio duration ({full_duration} ms) should be >= sub-second duration ({subsec_duration} ms)"
        )
        print(f"[PASS] '1200-3651': {len(subsec_audio.markdown)} chars, {subsec_duration} ms")

        # "0-3000,30000-" — combined time ranges
        print("\nAnalyzing audio with combined time ranges (0-3s and 30s onward) with content range '0-3000,30000-'...")
        combine_poller = await client.begin_analyze(
            analyzer_id="prebuilt-audioSearch",
            inputs=[
                AnalysisInput(
                    url=url,
                    content_range="0-3000,30000-",
                )
            ],
            polling_interval=10,
        )
        combine_result = await combine_poller.result()
        assert combine_result.contents is not None
        combine_audio = cast(AudioVisualContent, combine_result.contents[0])
        assert (combine_audio.end_time_ms or 0) > (combine_audio.start_time_ms or 0), (
            "'0-3000,30000-' should have EndTime > StartTime"
        )
        assert combine_audio.markdown, "'0-3000,30000-' should have markdown"
        print(f"[PASS] '0-3000,30000-': {len(combine_audio.markdown)} chars")

        await client.close()
        print("\n[SUCCESS] All audio URL content range async assertions passed")
