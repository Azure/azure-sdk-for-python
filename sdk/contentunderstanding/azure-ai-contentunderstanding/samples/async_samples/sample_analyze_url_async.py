# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_analyze_url_async.py

DESCRIPTION:
    Another great value of Content Understanding is its rich set of prebuilt analyzers. Great examples
    of these are the RAG analyzers that work for all modalities (prebuilt-documentSearch, prebuilt-imageSearch,
    prebuilt-audioSearch, and prebuilt-videoSearch).

    This sample demonstrates these RAG analyzers with URL inputs. Content Understanding supports both
    local binary inputs (see sample_analyze_binary_async.py) and URL inputs across all modalities.

    Important: For URL inputs, use begin_analyze() with AnalyzeInput objects that wrap the URL.
    For binary data (local files), use begin_analyze_binary() instead.

    Documents, HTML, and images with text are returned as DocumentContent (derived from MediaContent),
    while audio and video are returned as AudioVisualContent (also derived from MediaContent). These
    prebuilt RAG analyzers return markdown and a one-paragraph Summary for each content item.

USAGE:
    python sample_analyze_url_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    See sample_configure_defaults_async.py for model deployment setup guidance.
"""

import asyncio
import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalyzeInput,
    AnalyzeResult,
    DocumentContent,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        # [START analyze_document_from_url]
        # You can replace this URL with your own publicly accessible document URL.
        document_url = "https://raw.githubusercontent.com/Azure-Samples/azure-ai-content-understanding-assets/main/document/invoice.pdf"

        print(f"Analyzing document from URL with prebuilt-documentSearch...")
        print(f"  URL: {document_url}")

        poller = await client.begin_analyze(
            analyzer_id="prebuilt-documentSearch",
            inputs=[AnalyzeInput(url=document_url)],
        )
        result: AnalyzeResult = await poller.result()

        # Extract markdown content
        print("\nMarkdown:")
        content = result.contents[0]
        print(content.markdown)

        # Cast MediaContent to DocumentContent to access document-specific properties
        # DocumentContent derives from MediaContent and provides additional properties
        # to access full information about document, including Pages, Tables and many others
        document_content: DocumentContent = content  # type: ignore
        print(f"\nPages: {document_content.start_page_number} - {document_content.end_page_number}")

        # Check for pages
        if document_content.pages and len(document_content.pages) > 0:
            print(f"Number of pages: {len(document_content.pages)}")
            for page in document_content.pages:
                unit = document_content.unit or "units"
                print(f"  Page {page.page_number}: {page.width} x {page.height} {unit}")
        # [END analyze_document_from_url]

    if not isinstance(credential, AzureKeyCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
