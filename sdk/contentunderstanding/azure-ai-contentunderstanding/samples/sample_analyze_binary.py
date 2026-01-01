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
    analyzer. The prebuilt-documentSearch analyzer transforms unstructured documents into structured,
    machine-readable data optimized for RAG scenarios.

    Content Understanding supports multiple content types:
    - Documents: Extract text, tables, figures, layout information, and structured markdown
    - Images: Analyze standalone images to generate descriptions and extract visual features
    - Audio: Transcribe audio content with speaker diarization and timing information
    - Video: Analyze video content with visual frame extraction and audio transcription

USAGE:
    python sample_analyze_binary.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using prebuilt analyzers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_configure_defaults.py for setup instructions.
"""

import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    AnalyzeResult,
    DocumentContent,
    MediaContentKind,
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
    if result.contents and len(result.contents) > 0:
        content = result.contents[0]
        if content.markdown:
            print(content.markdown)
        else:
            print("No markdown content available.")
    else:
        print("No content found in the analysis result.")

    print("=" * 50)
    # [END extract_markdown]

    # Extract document properties
    if result.contents and len(result.contents) > 0:
        content = result.contents[0]

        # Check if this is document content to access document-specific properties
        if content.kind == MediaContentKind.DOCUMENT:
            # Type assertion: we know this is DocumentContent for PDF files
            document_content: DocumentContent = content  # type: ignore
            print(f"\nDocument Information:")
            print(f"  Start page: {document_content.start_page_number}")
            print(f"  End page: {document_content.end_page_number}")

            if document_content.start_page_number and document_content.end_page_number:
                total_pages = document_content.end_page_number - document_content.start_page_number + 1
                print(f"  Total pages: {total_pages}")

            # Check for pages
            if document_content.pages:
                print(f"\nPages ({len(document_content.pages)}):")
                for page in document_content.pages:
                    unit = document_content.unit or "units"
                    print(f"  Page {page.page_number}: {page.width} x {page.height} {unit}")


if __name__ == "__main__":
    main()
