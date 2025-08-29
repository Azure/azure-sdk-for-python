# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: use the prebuilt-documentAnalyzer to extract content from a URL.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python content_analyzers_analyze_url.py
"""

from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalyzeResult,
    MediaContent,
    DocumentContent,
    MediaContentKind,
    DocumentTable,
)
from sample_helper import save_json_to_file
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


# ---------------------------------------------------------------------------
# Sample: Extract content from URL using begin_analyze API
# ---------------------------------------------------------------------------
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Analyze a document from a remote URL using begin_analyze with prebuilt-documentAnalyzer
# 3. Print the markdown content from the analysis result


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(
        endpoint=endpoint, credential=credential
    ) as client, credential:
        file_url = "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"
        print(
            f"🔍 Analyzing remote document from {file_url} with prebuilt-documentAnalyzer..."
        )
        poller = await client.content_analyzers.begin_analyze(
            analyzer_id="prebuilt-documentAnalyzer", url=file_url
        )
        result: AnalyzeResult = await poller.result()

        # AnalyzeResult contains the full analysis result and can be used to access various properties
        # We are using markdown content as an example of what can be extracted
        print("\n📄 Markdown Content:")
        print("=" * 50)
        # A PDF file has only one content element even if it contains multiple pages
        content: MediaContent = result.contents[0]
        print(content.markdown)
        print("=" * 50)

        # Check if this is document content to access document-specific properties
        if content.kind == MediaContentKind.DOCUMENT:
            # Type assertion: we know this is DocumentContent for PDF files
            document_content: DocumentContent = content  # type: ignore
            print(f"\n📚 Document Information:")
            print(f"Start page: {document_content.start_page_number}")
            print(f"End page: {document_content.end_page_number}")
            print(
                f"Total pages: {document_content.end_page_number - document_content.start_page_number + 1}"
            )

            # Check for pages
            if document_content.pages is not None:
                print(f"\n📄 Pages ({len(document_content.pages)}):")
                for i, page in enumerate(document_content.pages):
                    unit = document_content.unit or "units"
                    print(f"  Page {i + 1}: {page.width} x {page.height} {unit}")

            # The following code shows how to access DocumentContent properties
            # Check if there are tables in the document
            if document_content.tables is not None:
                print(f"\n📊 Tables ({len(document_content.tables)}):")
                table_counter = 1
                # Iterate through tables, each table is of type DocumentTable
                for table in document_content.tables:
                    # Type: table is DocumentTable
                    # Get basic table dimensions
                    row_count: int = table.row_count
                    col_count: int = table.column_count
                    print(
                        f"  Table {table_counter}: {row_count} rows x {col_count} columns"
                    )
                    table_counter += 1
                    # You can use the table object model to get detailed information
                    # such as cell content, borders, spans, etc. (not shown to keep code concise)
        else:
            print("\n📚 Document Information: Not available for this content type")

        # Uncomment the following line to save the response to a file for object model inspection
        # Note: This saves the object model, not the raw JSON response
        # To get the full raw JSON response, see the sample: content_analyzers_analyze_binary_raw_json.py
        # save_json_to_file(result.as_dict(), filename_prefix="content_analyzers_analyze_url")


if __name__ == "__main__":
    asyncio.run(main())
