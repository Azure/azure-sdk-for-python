# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_analyze_inline_async.py

DESCRIPTION:
        SUPPORTED SERVICE API VERSION: ``2026-06-01-preview``

        This sample demonstrates how to analyze a document from a URL using ``analyze_inline``.

        ## Inline vs Long Running Operation analysis

        Content Understanding provides two analysis patterns:

        - **Long Running Operation (LRO)**: ``begin_analyze`` / ``begin_analyze_binary`` starts
            analysis and returns a poller. Use this pattern for larger files or more pages, broader
            analyzer coverage, operation lifecycle APIs, and results retained for up to 24 hours (or
            until you delete them).

        - **Inline**: ``analyze_inline`` / ``analyze_binary_inline`` returns a
            ``ContentAnalyzerInlineResponse`` in a single HTTP call with no polling. Use this pattern
            for smaller inputs under the inline size and analyzer limits. Access the ``AnalysisResult``
            through ``.result``. The result is not persisted; a non-succeeded inline status raises the
            same exception type as a failed completed LRO.

        For current limits, see https://aka.ms/cu-doc-limits.

    This sample uses ``analyze_inline`` for URL-based input. For binary inline input, see
    ``sample_analyze_binary_inline_async.py``. For the LRO pattern, see
    ``sample_analyze_url_async.py`` and ``sample_analyze_binary_async.py``.

    ## Supported inline analyzers

    - ``prebuilt-digitalParse``
    - ``prebuilt-read``
    - ``prebuilt-layout``
    - Custom document analyzers without fields

USAGE:
    python sample_analyze_inline_async.py

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
    AnalysisInput,
    AnalysisResult,
    ContentAnalyzerInlineResponse,
    DocumentContent,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


async def main() -> None:
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(
        endpoint=endpoint, credential=credential
    ) as client:
        # [START analyze_inline_from_url]
        file_url = "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"

        print(f"Analyzing {file_url} with analyze_inline (no polling)...")

        # analyze_inline returns ContentAnalyzerInlineResponse — unwrap .result for AnalysisResult.
        inline_response: ContentAnalyzerInlineResponse = await client.analyze_inline(
            analyzer_id="prebuilt-layout",
            inputs=[AnalysisInput(url=file_url)],
        )
        result: AnalysisResult = inline_response.result
        # [END analyze_inline_from_url]

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

        # [START extract_inline_markdown]
        print("\n" + "=" * 60)
        print("MARKDOWN CONTENT")
        print("=" * 60)

        content = result.contents[0]
        print(content.markdown)
        # [END extract_inline_markdown]

        # [START inline_document_properties]
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
        # [END inline_document_properties]

        # [START inline_to_llm_input]
        print("\n" + "=" * 60)
        print("LLM-READY OUTPUT")
        print("=" * 60)

        text = to_llm_input(result)
        print(text)
        # [END inline_to_llm_input]

    if isinstance(credential, DefaultAzureCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
