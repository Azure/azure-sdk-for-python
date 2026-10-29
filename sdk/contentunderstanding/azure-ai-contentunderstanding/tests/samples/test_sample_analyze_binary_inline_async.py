# pylint: disable=line-too-long,useless-suppression
# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_sample_analyze_binary_inline_async.py

DESCRIPTION:
    Async tests for the analyze_binary_inline (inline binary analysis) operation.
    Validates sample_analyze_binary_inline_async.py.

USAGE:
    pytest test_sample_analyze_binary_inline_async.py
"""

import os
import pytest
from azure.core.exceptions import HttpResponseError
from devtools_testutils.aio import recorded_by_proxy_async
from testpreparer_async import (
    ContentUnderstandingPreparer,
    ContentUnderstandingClientTestBaseAsync,
)
from azure.ai.contentunderstanding.models import DocumentContent


pytestmark = pytest.mark.preview


class TestSampleAnalyzeBinaryInlineAsync(ContentUnderstandingClientTestBaseAsync):
    """Tests for sample_analyze_binary_inline_async.py"""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_analyze_binary_inline_async(self, contentunderstanding_endpoint: str) -> None:
        """Test async inline analysis of a document from binary data."""
        client = self.create_preview_async_client(endpoint=contentunderstanding_endpoint)

        tests_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(tests_dir, "test_data", "sample_invoice.pdf")
        assert os.path.exists(file_path), f"Sample file not found at {file_path}"

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        assert len(file_bytes) > 0, "File should not be empty"
        print(f"[PASS] File loaded: {len(file_bytes)} bytes")

        async with client:
            inline_response = await client.analyze_binary_inline(
                analyzer_id="prebuilt-layout",
                binary_input=file_bytes,
            )

        assert inline_response is not None, "Inline response should not be null"
        result = inline_response.result if hasattr(inline_response, "result") else inline_response.get("result")
        assert result is not None, "Analysis result should not be null"
        contents = result.contents if hasattr(result, "contents") else result.get("contents")
        assert contents is not None, "Result contents should not be null"
        assert len(contents) > 0, "Result should have at least one content"
        print(f"[PASS] Inline binary analysis returned {len(contents)} content(s)")

        content = contents[0]
        markdown = content.markdown if hasattr(content, "markdown") else content.get("markdown")
        assert markdown is not None, "Content should have markdown"
        assert len(markdown) > 0, "Markdown should not be empty"
        print(f"[PASS] Markdown extracted: {len(markdown)} chars")

        if not isinstance(content, dict):
            assert isinstance(content, DocumentContent), "Content should be DocumentContent"
            if content.pages:
                print(f"[PASS] Document has {len(content.pages)} page(s)")
            if content.tables:
                print(f"[PASS] Document has {len(content.tables)} table(s)")

        usage = inline_response.usage
        assert usage is not None, "Inline usage details should be available after a succeeded analyze"
        assert usage.document_pages_standard_inline is not None
        assert usage.document_pages_standard_inline > 0
        assert usage.document_pages_standard is None
        assert usage.document_pages_minimal_inline is None
        assert usage.document_pages_basic_inline is None
        print(f"[PASS] Inline usage document_pages_standard_inline={usage.document_pages_standard_inline}")

        print("\n[SUCCESS] All test_sample_analyze_binary_inline_async assertions passed")

    @ContentUnderstandingPreparer()
    @recorded_by_proxy_async
    async def test_sample_analyze_binary_inline_five_page_limit_async(self, contentunderstanding_endpoint: str) -> None:
        """content_range 1-5 succeeds; 3- exceeds the 5-page inline limit."""
        client = self.create_preview_async_client(endpoint=contentunderstanding_endpoint)

        tests_dir = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(tests_dir, "test_data", "mixed_financial_invoices.pdf")
        assert os.path.exists(file_path), f"Sample file not found at {file_path}"

        with open(file_path, "rb") as f:
            multi_page_bytes = f.read()

        async with client:
            within_limit = await client.analyze_binary_inline(
                analyzer_id="prebuilt-layout",
                binary_input=multi_page_bytes,
                content_range="1-5",
            )
            within_result = within_limit.result if hasattr(within_limit, "result") else within_limit.get("result")
            assert within_result is not None, "Analysis result should not be null"
            content = within_result.contents[0]
            if isinstance(content, DocumentContent) and content.pages:
                assert (
                    len(content.pages) <= 5
                ), f"content_range '1-5' should return at most 5 pages, got {len(content.pages)}"
                print(f"[PASS] content_range '1-5' returned {len(content.pages)} page(s)")

            with pytest.raises(HttpResponseError) as exc_info:
                await client.analyze_binary_inline(
                    analyzer_id="prebuilt-layout",
                    binary_input=multi_page_bytes,
                    content_range="3-",
                )

        error_text = str(exc_info.value)
        message = getattr(exc_info.value, "message", "") or ""
        combined = f"{error_text} {message}"
        assert (
            "InputPageCountExceeded" in combined or "5" in combined or "page" in combined.lower()
        ), f"Expected page-limit error details, got: {combined}"
        print("[PASS] content_range '3-' raised HttpResponseError for 5-page inline limit")
        print("\n[SUCCESS] All test_sample_analyze_binary_inline_five_page_limit_async assertions passed")
