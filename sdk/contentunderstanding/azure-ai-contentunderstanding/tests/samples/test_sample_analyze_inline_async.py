# pylint: disable=line-too-long,useless-suppression
# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_analyze_inline_async.py

DESCRIPTION:
    Async tests for the analyze_inline (inline analysis) operation.
    Validates sample_analyze_inline_async.py.

USAGE:
    pytest test_sample_analyze_inline_async.py
"""

import pytest
from devtools_testutils.aio import recorded_by_proxy_async
from testpreparer_async import (
    ContentUnderstandingPreparer,
    ContentUnderstandingClientTestBaseAsync,
)
from azure.ai.contentunderstanding.models import DocumentContent, AnalysisInput


pytestmark = pytest.mark.preview


class TestSampleAnalyzeInlineAsync(ContentUnderstandingClientTestBaseAsync):
    """Tests for sample_analyze_inline_async.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_analyze_inline_async(self, contentunderstanding_endpoint: str) -> None:
        """Test async inline analysis of a document from URL."""
        client = self.create_preview_async_client(endpoint=contentunderstanding_endpoint)

        file_url = "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"

        async with client:
            inline_response = await client.analyze_inline(
                analyzer_id="prebuilt-layout",
                inputs=[AnalysisInput(url=file_url)],
            )

        assert inline_response is not None, "Inline response should not be null"
        result = inline_response.result if hasattr(inline_response, "result") else inline_response.get("result")
        assert result is not None, "Analysis result should not be null"
        contents = result.contents if hasattr(result, "contents") else result.get("contents")
        assert contents is not None, "Result contents should not be null"
        assert len(contents) > 0, "Result should have at least one content"
        print(f"[PASS] Inline analysis returned {len(contents)} content(s)")

        content = contents[0]
        markdown = content.markdown if hasattr(content, "markdown") else content.get("markdown")
        assert markdown is not None, "Content should have markdown"
        assert len(markdown) > 0, "Markdown should not be empty"
        print(f"[PASS] Markdown extracted: {len(markdown)} chars")

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

        print("\n[SUCCESS] All test_sample_analyze_inline_async assertions passed")
