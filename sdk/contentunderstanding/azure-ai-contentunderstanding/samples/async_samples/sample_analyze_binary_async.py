# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_analyze_binary_async.py

DESCRIPTION:
    This sample demonstrates how to analyze a PDF file from disk using the prebuilt-documentSearch
    analyzer.

    ## About analyzing documents from binary data

    One of the key values of Content Understanding is taking a content file and extracting the content
    for you in one call. The service returns an AnalyzeResult that contains an array of MediaContent
    items in AnalyzeResult.contents. This sample starts with a document file, so each item is a
    DocumentContent (a subtype of MediaContent) that exposes markdown plus detailed structure such
    as pages, tables, figures, and paragraphs.

    This sample focuses on document analysis. For prebuilt RAG analyzers covering images, audio, and
    video, see sample_analyze_url_async.py.

    ## Prebuilt analyzers

    Content Understanding provides prebuilt RAG analyzers (the prebuilt-*Search analyzers, such as
    prebuilt-documentSearch) that return markdown and a one-paragraph Summary for each content item,
    making them useful for retrieval-augmented generation (RAG) and other downstream applications:

    - prebuilt-documentSearch - Extracts content from documents (PDF, images, Office documents) with
      layout preservation, table detection, figure analysis, and structured markdown output.
      Optimized for RAG scenarios.
    - prebuilt-audioSearch - Transcribes audio content with speaker diarization, timing information,
      and conversation summaries. Supports multilingual transcription.
    - prebuilt-videoSearch - Analyzes video content with visual frame extraction, audio transcription,
      and structured summaries. Provides temporal alignment of visual and audio content.
    - prebuilt-imageSearch - Analyzes standalone images and returns a one-paragraph Summary of the
      image content. For images that contain text (including hand-written text), use
      prebuilt-documentSearch.

    This sample uses prebuilt-documentSearch to extract structured content from PDF documents.

USAGE:
    python sample_analyze_binary_async.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    See sample_update_defaults_async.py for model deployment setup guidance.
"""

import asyncio
import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalyzeResult,
    DocumentContent,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


async def main() -> None:
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        # [START analyze_document_from_binary]
        # Replace with the path to your local document file.
        file_path = "sample_files/sample_invoice.pdf"

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        print(f"Analyzing {file_path} with prebuilt-documentSearch...")
        poller = await client.begin_analyze_binary(
            analyzer_id="prebuilt-documentSearch",
            binary_input=file_bytes,
        )
        result: AnalyzeResult = await poller.result()
        # [END analyze_document_from_binary]

        # [START extract_markdown]
        print("\nMarkdown Content:")
        print("=" * 50)

        # A PDF file has only one content element even if it contains multiple pages
        content = result.contents[0]
        print(content.markdown)

        print("=" * 50)
        # [END extract_markdown]

        # [START access_document_properties]
        # Check if this is document content to access document-specific properties
        if isinstance(content, DocumentContent):
            print(f"\nDocument type: {content.mime_type or '(unknown)'}")
            print(f"Start page: {content.start_page_number}")
            print(f"End page: {content.end_page_number}")

            # Check for pages
            if content.pages and len(content.pages) > 0:
                print(f"\nNumber of pages: {len(content.pages)}")
                for page in content.pages:
                    unit = content.unit or "units"
                    print(f"  Page {page.page_number}: {page.width} x {page.height} {unit}")

            # Check for tables
            if content.tables and len(content.tables) > 0:
                print(f"\nNumber of tables: {len(content.tables)}")
                table_counter = 1
                for table in content.tables:
                    print(f"  Table {table_counter}: {table.row_count} rows x {table.column_count} columns")
                    table_counter += 1
        # [END access_document_properties]

    if not isinstance(credential, AzureKeyCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
