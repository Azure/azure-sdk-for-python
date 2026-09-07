# pylint: disable=line-too-long,useless-suppression
# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
TEST FILE: test_analyze_inline_errors.py

DESCRIPTION:
    Verifies that inline analyze APIs raise ``HttpResponseError`` for invalid
    or empty inputs. Today's service returns these as HTTP 4xx (not HTTP 200
    with envelope ``status: Failed``); Azure Core raises before the
    raise-on-Failed wrapper runs. Keep the wrapper for forward compatibility.

USAGE:
    CONTENTUNDERSTANDING_TEST_API_VERSION=2026-06-01-preview pytest test_analyze_inline_errors.py
"""

from __future__ import annotations

import pytest
from azure.core.exceptions import HttpResponseError
from devtools_testutils import recorded_by_proxy
from testpreparer import (
    ContentUnderstandingPreparer,
    ContentUnderstandingClientTestBase,
)
from azure.ai.contentunderstanding.models import AnalysisInput


pytestmark = pytest.mark.preview


class TestAnalyzeInlineErrors(ContentUnderstandingClientTestBase):
    """Inline analyze error-path coverage for invalid / empty inputs."""

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_analyze_binary_inline_raises_on_invalid_pdf(self, contentunderstanding_endpoint: str) -> None:
        """Corrupt PDF bytes raise HttpResponseError (HTTP 4xx InvalidRequest)."""
        client = self.create_preview_client(endpoint=contentunderstanding_endpoint)

        with pytest.raises(HttpResponseError) as exc_info:
            client.analyze_binary_inline(
                analyzer_id="prebuilt-layout",
                binary_input=b"%PDF-1.4\n%not-a-real-pdf\n",
            )

        combined = f"{exc_info.value} {getattr(exc_info.value, 'message', '') or ''}"
        assert (
            "InvalidRequest" in combined or "FailedToExtractPageCount" in combined or "Invalid" in combined
        ), f"Expected invalid-document error details, got: {combined}"
        print("[PASS] invalid PDF raised HttpResponseError")

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_analyze_inline_raises_on_invalid_url(self, contentunderstanding_endpoint: str) -> None:
        """Unreachable / missing URL raises HttpResponseError (HTTP 4xx InvalidRequest)."""
        client = self.create_preview_client(endpoint=contentunderstanding_endpoint)

        with pytest.raises(HttpResponseError) as exc_info:
            client.analyze_inline(
                analyzer_id="prebuilt-layout",
                inputs=[AnalysisInput(url="https://example.com/does-not-exist-cu-inline-test-404.pdf")],
            )

        combined = f"{exc_info.value} {getattr(exc_info.value, 'message', '') or ''}"
        assert (
            "InvalidRequest" in combined or "ContentSourceNotAccessible" in combined or "Invalid" in combined
        ), f"Expected inaccessible-source error details, got: {combined}"
        print("[PASS] invalid URL raised HttpResponseError")

    @ContentUnderstandingPreparer()
    @recorded_by_proxy
    def test_analyze_binary_inline_raises_on_empty_input(self, contentunderstanding_endpoint: str) -> None:
        """Empty binary body raises HttpResponseError (HTTP 4xx ContentEmpty)."""
        client = self.create_preview_client(endpoint=contentunderstanding_endpoint)

        with pytest.raises(HttpResponseError) as exc_info:
            client.analyze_binary_inline(
                analyzer_id="prebuilt-layout",
                binary_input=b"",
            )

        combined = f"{exc_info.value} {getattr(exc_info.value, 'message', '') or ''}"
        assert (
            "InvalidRequest" in combined or "ContentEmpty" in combined or "empty" in combined.lower()
        ), f"Expected empty-content error details, got: {combined}"
        print("[PASS] empty binary input raised HttpResponseError")
