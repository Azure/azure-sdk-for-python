# pylint: disable=line-too-long,useless-suppression
# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_to_llm_input.py

DESCRIPTION:
    These tests validate the sample_to_llm_input.py sample code.

    The sample demonstrates four scenarios for the to_llm_input() helper:
      1. OUTPUT OPTIONS — fields-only, markdown-only, custom metadata
      2. MULTI-PAGE PDF WITH CONTENT RANGE — page markers preserve original numbers
      3. MULTI-SEGMENT VIDEO — segments separated by '*****', each with timeRange
      4. AUDIO WITH CONTENT RANGE — single segment with custom metadata

    Each test mirrors one section of the sample, exercising the same analyzer,
    URL, and to_llm_input options used in that section.

USAGE:
    pytest test_sample_to_llm_input.py
"""

from devtools_testutils import recorded_by_proxy
from testpreparer import ContentUnderstandingPreparer, ContentUnderstandingClientTestBase
from azure.ai.contentunderstanding import to_llm_input
from azure.ai.contentunderstanding.models import (
    AnalysisInput,
    AudioVisualContent,
    DocumentContent,
)


class TestSampleToLlmInput(ContentUnderstandingClientTestBase):
    """Tests for sample_to_llm_input.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_to_llm_input_output_options(self, contentunderstanding_endpoint: str) -> None:
        """Section 1 of the sample — output option flags and custom metadata.

        Validates:
        - Default output (fields + markdown) contains both
        - include_markdown=False produces fields-only output (no markdown body)
        - include_fields=False produces markdown-only output (no 'fields:' block)
        - metadata={...} injects custom keys into the YAML front matter
        """
        client = self.create_client(endpoint=contentunderstanding_endpoint)

        invoice_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/document/invoice.pdf"

        poller = client.begin_analyze(
            analyzer_id="prebuilt-invoice",
            inputs=[AnalysisInput(url=invoice_url)],
        )
        result = poller.result()

        assert result is not None and result.contents, "Analysis should return contents"
        content = result.contents[0]
        assert isinstance(content, DocumentContent), "Invoice analysis should return DocumentContent"
        markdown = content.markdown or ""
        assert markdown.strip(), "Invoice analysis should return non-empty markdown"
        print(f"[PASS] Invoice analyzed ({len(markdown)} markdown chars)")

        # --- Default: fields + markdown ---
        default_text = to_llm_input(result)
        assert default_text.startswith("---"), "Default output should start with YAML front matter"
        assert "\n---\n" in default_text, "Default output should close YAML front matter"
        assert "contentType: document" in default_text, "Default output should declare contentType: document"
        assert "fields:" in default_text, "Default output should include 'fields:' block"
        assert markdown in default_text, "Default output should include markdown body"
        print(f"[PASS] Default output: fields + markdown ({len(default_text)} chars)")

        # --- Fields-only: include_markdown=False ---
        fields_only = to_llm_input(result, include_markdown=False)
        assert "fields:" in fields_only, "Fields-only output should still include 'fields:' block"
        assert markdown not in fields_only, "Fields-only output should not contain the markdown body"
        assert len(fields_only) < len(default_text), "Fields-only output should be smaller than default"
        print(f"[PASS] Fields-only output validated ({len(fields_only)} chars)")

        # --- Markdown-only: include_fields=False ---
        markdown_only = to_llm_input(result, include_fields=False)
        assert "fields:" not in markdown_only, "Markdown-only output should not include a 'fields:' block"
        assert markdown in markdown_only, "Markdown-only output should still include the markdown body"
        print(f"[PASS] Markdown-only output validated ({len(markdown_only)} chars)")

        # --- Custom metadata ---
        with_metadata = to_llm_input(
            result,
            metadata={"source": "invoice.pdf", "department": "finance"},
        )
        assert "source: invoice.pdf" in with_metadata, "Metadata 'source' key should appear in front matter"
        assert "department: finance" in with_metadata, "Metadata 'department' key should appear in front matter"
        # Metadata is injected after contentType but before fields per helper ordering
        assert with_metadata.index("contentType: document") < with_metadata.index("source: invoice.pdf"), (
            "Custom metadata should appear after 'contentType' in front matter"
        )
        assert with_metadata.index("source: invoice.pdf") < with_metadata.index("fields:"), (
            "Custom metadata should appear before the 'fields:' block in front matter"
        )
        print("[PASS] Custom metadata injected into YAML front matter")

        print("\n[SUCCESS] All test_to_llm_input_output_options assertions passed")

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_to_llm_input_multi_page_content_range(self, contentunderstanding_endpoint: str) -> None:
        """Section 2 of the sample — multi-page PDF with content_range.

        Validates that to_llm_input preserves original document page numbers in the
        page markers (not the renumbered offsets within the requested range).
        """
        client = self.create_client(endpoint=contentunderstanding_endpoint)

        multi_page_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/document/mixed_financial_invoices.pdf"

        # Analyze pages 2-3 and 5 — markers should reflect those page numbers, not 1, 2, 3
        poller = client.begin_analyze(
            analyzer_id="prebuilt-documentSearch",
            inputs=[AnalysisInput(url=multi_page_url, content_range="2-3,5")],
        )
        result = poller.result()

        assert result is not None and result.contents, "Analysis should return contents"
        doc = result.contents[0]
        assert isinstance(doc, DocumentContent), "Range analysis should return DocumentContent"
        page_numbers = sorted([p.page_number for p in (doc.pages or [])])
        assert page_numbers == [2, 3, 5], (
            f"content_range '2-3,5' should return pages [2, 3, 5], got {page_numbers}"
        )
        print(f"[PASS] Range analysis returned pages {page_numbers}")

        text = to_llm_input(result)
        assert text.startswith("---"), "Output should start with YAML front matter"
        assert "contentType: document" in text, "Output should declare contentType: document"
        # The 'pages' front matter key should reflect the original page numbers (2, 3, 5),
        # compressed by the helper as "2-3, 5" — not renumbered to 1-3 within the range.
        assert "pages:" in text, "Output should include a 'pages' key in front matter"
        assert "2-3, 5" in text or "'2-3, 5'" in text, (
            f"'pages' value should be '2-3, 5' (original page numbers preserved). Output:\n{text[:500]}"
        )
        print(f"[PASS] to_llm_input output validated ({len(text)} chars, pages='2-3, 5' preserved)")

        # Page markers in the markdown body should use the original page numbers
        # (<!-- page 2 -->, <!-- page 3 -->, <!-- page 5 -->), not renumbered (1, 2, 3).
        assert "<!-- page 1 -->" not in text, (
            "Page marker '<!-- page 1 -->' should not appear — we only requested pages 2-3, 5"
        )
        for expected_page in [2, 3, 5]:
            assert f"<!-- page {expected_page} -->" in text, (
                f"Page marker '<!-- page {expected_page} -->' should appear in the markdown body. "
                f"Output:\n{text[:800]}"
            )
        print("[PASS] Page markers verified: <!-- page 2 -->, <!-- page 3 -->, <!-- page 5 -->")

        print("\n[SUCCESS] All test_to_llm_input_multi_page_content_range assertions passed")

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_to_llm_input_multi_segment_video(self, contentunderstanding_endpoint: str) -> None:
        """Section 3 of the sample — multi-segment video.

        Validates that to_llm_input renders each segment with its time range in the
        front matter and separates segments with '*****' dividers.
        """
        client = self.create_client(endpoint=contentunderstanding_endpoint)

        video_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/videos/sdk_samples/FlightSimulator.mp4"

        poller = client.begin_analyze(
            analyzer_id="prebuilt-videoSearch",
            inputs=[AnalysisInput(url=video_url)],
        )
        result = poller.result()

        assert result is not None and result.contents, "Video analysis should return contents"
        assert all(isinstance(c, AudioVisualContent) for c in result.contents), (
            "Video analysis should return AudioVisualContent items"
        )
        segment_count = len(result.contents)
        print(f"[PASS] Video analyzed: {segment_count} segment(s)")

        text = to_llm_input(result)
        assert text.startswith("---"), "Output should start with YAML front matter"
        assert "contentType: audioVisual" in text, "Output should declare contentType: audioVisual"

        if segment_count > 1:
            # Multi-segment: each segment has its own front matter with timeRange
            # and is separated by '*****' divider (n segments => n-1 dividers).
            expected_dividers = segment_count - 1
            assert text.count("*****") == expected_dividers, (
                f"{segment_count} segments should produce {expected_dividers} '*****' dividers, "
                f"got {text.count('*****')}"
            )
            assert text.count("timeRange:") == segment_count, (
                f"Each of {segment_count} segments should declare a 'timeRange', "
                f"got {text.count('timeRange:')}"
            )
            print(f"[PASS] Multi-segment output: {segment_count} timeRange entries, "
                  f"{expected_dividers} '*****' dividers")
        else:
            # Single segment: no dividers, single timeRange (or no timeRange if absent)
            assert "*****" not in text, "Single-segment output should not contain '*****' divider"
            print("[PASS] Single-segment video output validated")

        print(f"[PASS] to_llm_input output validated ({len(text)} chars)")
        print("\n[SUCCESS] All test_to_llm_input_multi_segment_video assertions passed")

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_to_llm_input_audio_with_content_range(self, contentunderstanding_endpoint: str) -> None:
        """Section 4 of the sample — audio with content_range and custom metadata.

        Validates that to_llm_input handles audio analysis with a content_range
        (first 10 seconds) and that custom metadata is injected into the front matter.
        """
        client = self.create_client(endpoint=contentunderstanding_endpoint)

        audio_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/audio/callCenterRecording.mp3"

        # content_range for audio is in milliseconds: '0-10000' = first 10 seconds
        poller = client.begin_analyze(
            analyzer_id="prebuilt-audioSearch",
            inputs=[AnalysisInput(url=audio_url, content_range="0-10000")],
        )
        result = poller.result()

        assert result is not None and result.contents, "Audio analysis should return contents"
        assert all(isinstance(c, AudioVisualContent) for c in result.contents), (
            "Audio analysis should return AudioVisualContent items"
        )
        print(f"[PASS] Audio analyzed: {len(result.contents)} segment(s)")

        # Include metadata to track the source file in RAG pipelines
        text = to_llm_input(
            result,
            metadata={"source": "callCenterRecording.mp3"},
        )
        assert text.startswith("---"), "Output should start with YAML front matter"
        assert "contentType: audioVisual" in text, "Output should declare contentType: audioVisual"
        assert "source: callCenterRecording.mp3" in text, (
            "Custom metadata 'source' key should appear in front matter"
        )
        # Metadata should appear after contentType per helper ordering
        assert text.index("contentType: audioVisual") < text.index("source: callCenterRecording.mp3"), (
            "Custom metadata should appear after 'contentType' in front matter"
        )
        print(f"[PASS] to_llm_input output validated ({len(text)} chars, includes source metadata)")

        print("\n[SUCCESS] All test_to_llm_input_audio_with_content_range assertions passed")
