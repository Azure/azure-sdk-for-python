# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_analyze_binary_inline_async.py

DESCRIPTION:
        SUPPORTED SERVICE API VERSION: ``2026-06-01-preview``

        This sample demonstrates how to analyze a PDF file from disk using
        ``analyze_binary_inline``.

        ## Inline vs Long Running Operation analysis

        Content Understanding provides two analysis patterns:

        - **Long Running Operation (LRO)**: ``begin_analyze_binary`` starts analysis and returns a
            poller. Use this pattern for larger files or more pages, broader analyzer coverage,
            operation lifecycle APIs, and results retained for up to 24 hours (or until you delete
            them).

        - **Inline**: ``analyze_binary_inline`` returns a ``ContentAnalyzerInlineResponse`` in a
            single HTTP call with no polling. Use this pattern for smaller inputs under the inline size
            and analyzer limits. Access the ``AnalysisResult`` through ``.result``. The result is not
            persisted; a non-succeeded inline status raises the same exception type as a failed
            completed LRO.

        For current limits, see https://aka.ms/cu-doc-limits.

    This sample uses ``analyze_binary_inline`` for binary file input. For URL-based inline input,
    see ``sample_analyze_inline_async.py``. For the LRO pattern, see
    ``sample_analyze_binary_async.py``.

    ## Supported inline analyzers

    - ``prebuilt-digitalParse``
    - ``prebuilt-read``
    - ``prebuilt-layout``
    - Custom document analyzers without fields

    Like ``begin_analyze_binary``, pass ``content_range`` for simple page or time ranges.
    Inline supports at most 5 pages, so select a page window within that limit.

USAGE:
    python sample_analyze_binary_inline_async.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    See sample_update_defaults_async.py for model deployment setup guidance.
"""

import asyncio
import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding import to_llm_input
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalysisResult,
    ContentAnalyzerInlineResponse,
    DocumentContent,
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


async def main() -> None:
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(
        endpoint=endpoint, credential=credential
    ) as client:
        # [START analyze_binary_inline]
        file_path = "sample_files/sample_invoice.pdf"

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        print(f"Analyzing {file_path} with analyze_binary_inline (no polling)...")

        # analyze_binary_inline returns ContentAnalyzerInlineResponse — unwrap .result for AnalysisResult.
        inline_response: ContentAnalyzerInlineResponse = (
            await client.analyze_binary_inline(
                analyzer_id="prebuilt-layout",
                binary_input=file_bytes,
            )
        )
        result: AnalysisResult = inline_response.result
        # [END analyze_binary_inline]

        # [START inline_get_usage]
        # Inline analyze reports document_pages_*_inline meters (see pricing docs for which
        # meter applies). This sample prints the standard inline page meter.
        usage = inline_response.usage
        if usage:
            print(
                f"Document pages (standard inline): {usage.document_pages_standard_inline}"
            )
            if usage.contextualization_tokens is not None:
                print(f"Contextualization tokens: {usage.contextualization_tokens}")
        # [END inline_get_usage]

        # [START binary_inline_markdown]
        print("\n" + "=" * 60)
        print("MARKDOWN CONTENT")
        print("=" * 60)

        content = result.contents[0]
        print(content.markdown)
        # [END binary_inline_markdown]

        # [START binary_inline_document_properties]
        print("\n" + "=" * 60)
        print("DOCUMENT PROPERTIES")
        print("=" * 60)

        if isinstance(content, DocumentContent):
            print(f"Document type: {content.mime_type or '(unknown)'}")
            print(f"Start page: {content.start_page_number}")
            print(f"End page: {content.end_page_number}")
            if content.pages:
                print(f"Total pages: {len(content.pages)}")
            if content.tables:
                print(f"Tables found: {len(content.tables)}")
        # [END binary_inline_document_properties]

        # [START binary_inline_to_llm_input]
        print("\n" + "=" * 60)
        print("LLM-READY OUTPUT")
        print("=" * 60)

        text = to_llm_input(result)
        print(text)
        # [END binary_inline_to_llm_input]

        # [START binary_inline_five_page_limit]
        # Inline analysis supports at most 5 pages per request. The multi-page PDF below
        # has more than 5 pages: content_range="1-5" succeeds, while "3-" exceeds the limit.
        multi_page_path = "sample_files/mixed_financial_invoices.pdf"
        with open(multi_page_path, "rb") as f:
            multi_page_bytes = f.read()

        print("\n" + "=" * 60)
        print("INLINE 5-PAGE LIMIT")
        print("=" * 60)

        print(f"Analyzing pages 1-5 of {multi_page_path} with prebuilt-layout...")
        within_limit: ContentAnalyzerInlineResponse = (
            await client.analyze_binary_inline(
                analyzer_id="prebuilt-layout",
                binary_input=multi_page_bytes,
                content_range="1-5",
            )
        )
        within_result: AnalysisResult = within_limit.result
        within_content = within_result.contents[0]
        if isinstance(within_content, DocumentContent) and within_content.pages:
            print(f"Pages returned within limit: {len(within_content.pages)}")

        print(
            f"Attempting content_range='3-' on {multi_page_path} (exceeds 5-page inline limit)..."
        )
        try:
            await client.analyze_binary_inline(
                analyzer_id="prebuilt-layout",
                binary_input=multi_page_bytes,
                content_range="3-",
            )
        except HttpResponseError:
            print("Warning: Inline analysis supports at most 5 pages per request.")
        # [END binary_inline_five_page_limit]

    if isinstance(credential, DefaultAzureCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
