# pylint: disable=line-too-long,useless-suppression
# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_analyze_inline.py

DESCRIPTION:
    Tests for the analyze_inline (inline analysis) operation introduced
    in API version 2026-06-01-preview. This operation returns ContentAnalyzerInlineResponse without LRO polling;
    access AnalysisResult via ``.result``.

    Uses the same test data as test_sample_analyze_binary.py (sample_invoice.pdf).

USAGE:
    # Playback mode (requires recordings):
    pytest test_sample_analyze_inline.py

    # Record mode (requires live service):
    AZURE_TEST_RUN_LIVE=true pytest test_sample_analyze_inline.py

    # Live mode (no recording):
    AZURE_TEST_RUN_LIVE=true AZURE_SKIP_LIVE_RECORDING=true pytest test_sample_analyze_inline.py
"""

import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import (
    ContentUnderstandingPreparer,
    ContentUnderstandingClientTestBase,
)
from azure.ai.contentunderstanding.models import DocumentContent, AnalysisInput


pytestmark = pytest.mark.preview


class TestSampleAnalyzeInline(ContentUnderstandingClientTestBase):
    """Tests for analyze_inline (sync analysis, no LRO)."""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_analyze_inline_url(self, contentunderstanding_endpoint: str) -> None:
        """Test inline analysis of a document from URL.

        Validates:
        1. analyze_inline returns ContentAnalyzerInlineResponse; .result is AnalysisResult
        2. Result contains document content with markdown
        3. Document properties are accessible
        """
        client = self.create_preview_client(endpoint=contentunderstanding_endpoint)

        file_url = "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"

        # Analyze document synchronously — returns ContentAnalyzerInlineResponse
        inline_response = client.analyze_inline(
            analyzer_id="prebuilt-layout",
            inputs=[AnalysisInput(url=file_url)],
        )

        assert inline_response is not None, "Inline response should not be null"
        assert getattr(inline_response, "status", None) is not None or (
            hasattr(inline_response, "get") and inline_response.get("status") is not None
        ), "Inline response should include status"
        result = inline_response.result if hasattr(inline_response, "result") else inline_response.get("result")
        assert result is not None, "Analysis result should not be null"
        contents = result.contents if hasattr(result, "contents") else result.get("contents")
        assert contents is not None, "Result contents should not be null"
        assert len(contents) > 0, "Result should have at least one content"
        print(f"[PASS] Inline analysis returned {len(contents)} content(s)")

        # Verify markdown extraction
        content = contents[0]
        markdown = content.markdown if hasattr(content, "markdown") else content.get("markdown")
        assert markdown is not None, "Content should have markdown"
        assert len(markdown) > 0, "Markdown should not be empty"
        print(f"[PASS] Markdown extracted: {len(markdown)} chars")

        # Verify document-specific properties
        if not isinstance(content, dict):
            assert isinstance(content, DocumentContent), "Content should be DocumentContent"
            print("[PASS] Content is DocumentContent type")

        usage = inline_response.usage
        assert usage is not None, "Inline usage details should be available after a succeeded analyze"
        assert usage.document_pages_standard_inline is not None
        assert usage.document_pages_standard_inline > 0
        assert usage.document_pages_standard is None
        assert usage.document_pages_minimal_inline is None
        assert usage.document_pages_basic_inline is None
        print(f"[PASS] Inline usage document_pages_standard_inline={usage.document_pages_standard_inline}")

        print("\n[SUCCESS] All test_analyze_inline_url assertions passed")
