# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_analyze_binary.py

DESCRIPTION:
    This sample demonstrates how to analyze a PDF file from disk using the prebuilt-documentSearch
    analyzer.

    One of the key values of Content Understanding is taking a content file and extracting the content
    for you in one call. The service returns an AnalyzeResult that contains an array of MediaContent
    items in AnalyzeResult.contents. This sample starts with a document file, so each item is a
    DocumentContent (a subtype of MediaContent) that exposes markdown plus detailed structure such
    as pages, tables, figures, and paragraphs.

    This sample focuses on document analysis. For prebuilt RAG analyzers covering images, audio, and
    video, see sample_analyze_url.py.

USAGE:
    python sample_analyze_binary.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    See sample_configure_defaults.py for model deployment setup guidance.
"""

import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalyzeResult,
    DocumentContent,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

load_dotenv()


def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    # [START analyze_document_from_binary]
    file_path = "sample_files/sample_invoice.pdf"

    with open(file_path, "rb") as f:
        pdf_bytes = f.read()

    print(f"Analyzing {file_path} with prebuilt-documentSearch...")
    poller = client.begin_analyze_binary(
        analyzer_id="prebuilt-documentSearch",
        binary_input=pdf_bytes,
    )
    result: AnalyzeResult = poller.result()
    # [END analyze_document_from_binary]

    # [START extract_markdown]
    print("\nMarkdown Content:")
    print("=" * 50)

    # A PDF file has only one content element even if it contains multiple pages
    content = result.contents[0]
    print(content.markdown)

    print("=" * 50)
    # [END extract_markdown]

    # Access document properties
    # Cast MediaContent to DocumentContent to access document-specific properties
    # DocumentContent derives from MediaContent and provides additional properties
    # to access full information about document, including pages, tables and many others
    document_content: DocumentContent = content  # type: ignore
    print(f"\nDocument Information:")
    print(f"  Start page: {document_content.start_page_number}")
    print(f"  End page: {document_content.end_page_number}")

    # Check for pages
    if document_content.pages and len(document_content.pages) > 0:
        print(f"\nNumber of pages: {len(document_content.pages)}")
        for page in document_content.pages:
            unit = document_content.unit or "units"
            print(f"  Page {page.page_number}: {page.width} x {page.height} {unit}")


if __name__ == "__main__":
    main()
