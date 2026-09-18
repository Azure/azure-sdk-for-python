# pylint: disable=line-too-long,useless-suppression,protected-access
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
TEST FILE: test_readme_snippets.py

DESCRIPTION:
    Offline coverage for code snippets in the package README.md.

    README sections covered:
    - Service API versions (GA and preview client construction)
    - Authenticate the client (DefaultAzureCredential sync/async, API key)
    - Enable logging
    - Convert results to LLM-ready text (``to_llm_input`` output shape and
      nested ``content_range`` / ``InputPageNumber`` markers)

    End-to-end service coverage for the README analyze + ``to_llm_input`` flow:
    - ``tests/samples/test_sample_analyze_binary.py``
    - ``tests/samples/test_sample_to_llm_input.py::test_to_llm_input_multi_page_content_range``

USAGE:
    pytest test_readme_snippets.py
"""

from __future__ import annotations

import asyncio
import logging

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential

from azure.ai.contentunderstanding import ContentUnderstandingClient, to_llm_input
from azure.ai.contentunderstanding.aio import (
    ContentUnderstandingClient as AsyncContentUnderstandingClient,
)
from azure.ai.contentunderstanding.models import (
    AnalysisInput,
    AnalysisResult,
    ContentSpan,
    DocumentContent,
    DocumentPage,
    StringField,
)
from testpreparer import GA_API_VERSION, PREVIEW_API_VERSION

_ENDPOINT = "https://sanitized.services.ai.azure.com"
_FAKE_KEY = "fake-key"


class TestReadmeSnippetsOffline:
    """Offline construction checks that mirror README authentication / version snippets."""

    def test_readme_use_latest_ga_service_api_version(self) -> None:
        """README: Use the latest GA service API version."""
        endpoint = _ENDPOINT
        client = ContentUnderstandingClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(_FAKE_KEY),
            api_version=GA_API_VERSION,
        )
        assert client._config.api_version == GA_API_VERSION

    def test_readme_use_latest_preview_service_api_version(self) -> None:
        """README: Use the latest preview service API version."""
        endpoint = _ENDPOINT
        client = ContentUnderstandingClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(_FAKE_KEY),
            api_version=PREVIEW_API_VERSION,
        )
        assert client._config.api_version == PREVIEW_API_VERSION

    def test_readme_authenticate_with_default_azure_credential(self) -> None:
        """README: Authenticate with DefaultAzureCredential (sync)."""
        endpoint = _ENDPOINT
        # Construction only — credential is not used until a service call.
        credential = DefaultAzureCredential()
        client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)
        assert client is not None
        assert client._config.api_version == PREVIEW_API_VERSION

    def test_readme_authenticate_with_default_azure_credential_async(self) -> None:
        """README: Authenticate with DefaultAzureCredential (async)."""

        async def _create_async_client() -> None:
            endpoint = _ENDPOINT
            credential = AsyncDefaultAzureCredential()
            try:
                client = AsyncContentUnderstandingClient(endpoint=endpoint, credential=credential)
                assert client is not None
                assert client._config.api_version == PREVIEW_API_VERSION
                await client.close()
            finally:
                await credential.close()

        asyncio.run(_create_async_client())

    def test_readme_authenticate_with_api_key(self) -> None:
        """README: Authenticate with API key."""
        endpoint = _ENDPOINT
        api_key = _FAKE_KEY
        client = ContentUnderstandingClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))
        assert client is not None

    def test_readme_enable_logging(self) -> None:
        """README: Enable logging on the client."""
        endpoint = _ENDPOINT
        api_key = _FAKE_KEY
        logging.basicConfig(level=logging.DEBUG)
        client = ContentUnderstandingClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key),
            logging_enable=True,
        )
        assert client is not None

    def test_readme_convert_results_to_llm_ready_text(self) -> None:
        """README: Convert results to LLM-ready text (to_llm_input output shape).

        Service analyze call coverage for the same README flow lives in
        ``tests/samples/test_sample_analyze_binary.py``.
        """
        result = AnalysisResult(
            contents=[
                DocumentContent(
                    kind="document",
                    mime_type="application/pdf",
                    markdown=(
                        "# ==This is title==\n"
                        "## 1. Text\n"
                        "[Latin](https://en.wikipedia.org/wiki/Latin) refers to an ancient Italic language..."
                    ),
                    fields={
                        "Summary": StringField(
                            type="string",
                            value_string=(
                                "The document provides an overview of Latin, includes a sample "
                                "table with names and corporate affiliations, presents a bar chart "
                                "figure illustrating monthly values, and describes the AI Document "
                                "Intelligence service..."
                            ),
                        )
                    },
                    start_page_number=1,
                    end_page_number=1,
                    pages=[DocumentPage(page_number=1)],
                )
            ]
        )

        text = to_llm_input(result)
        assert text.startswith("---")
        assert "mimeType: application/pdf" in text
        assert "pages: 1" in text
        assert "Summary:" in text
        assert "<!-- InputPageNumber: 1 -->" in text
        assert "# ==This is title==" in text

    def test_readme_to_llm_input_content_range_page_markers(self) -> None:
        """README nested example: content_range preserves original InputPageNumber markers.

        End-to-end service coverage for the same snippet lives in
        ``tests/samples/test_sample_to_llm_input.py::test_to_llm_input_multi_page_content_range``.
        """
        # Construction of the AnalysisInput mirrors the README nested snippet.
        analysis_input = AnalysisInput(url="https://example.com/multi-page.pdf", content_range="2-3,5")
        assert analysis_input.content_range == "2-3,5"

        # Simulate a result that only contains the requested original page numbers.
        # Page markers are derived from pages[].spans offsets (same as the service).
        markdown = "page 2 content\n\npage 3 content\n\npage 5 content"
        page2 = "page 2 content"
        page3 = "page 3 content"
        page5 = "page 5 content"
        offset2 = 0
        offset3 = markdown.index(page3)
        offset5 = markdown.index(page5)
        result = AnalysisResult(
            contents=[
                DocumentContent(
                    kind="document",
                    markdown=markdown,
                    start_page_number=2,
                    end_page_number=5,
                    pages=[
                        DocumentPage(
                            page_number=2,
                            spans=[ContentSpan(offset=offset2, length=len(page2))],
                        ),
                        DocumentPage(
                            page_number=3,
                            spans=[ContentSpan(offset=offset3, length=len(page3))],
                        ),
                        DocumentPage(
                            page_number=5,
                            spans=[ContentSpan(offset=offset5, length=len(page5))],
                        ),
                    ],
                )
            ]
        )
        text = to_llm_input(result)
        assert "2-3, 5" in text or "'2-3, 5'" in text
        for page in (2, 3, 5):
            assert f"<!-- InputPageNumber: {page} -->" in text
        assert "<!-- InputPageNumber: 1 -->" not in text
