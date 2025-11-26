# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_analyze_url.py

DESCRIPTION:
    This sample demonstrates how to analyze a document from a URL using the prebuilt-documentSearch
    analyzer. This shows how to analyze a document from a publicly accessible URL instead of a local file.

    For understanding basic analysis concepts, authentication, and result processing,
    see sample_analyze_binary.py first.

USAGE:
    python sample_analyze_url.py

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
    AnalyzeInput,
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

    # Analyze document from URL
    analyze_document_url(client)


# [START ContentUnderstandingAnalyzeUrlAsync]
def analyze_document_url(client: ContentUnderstandingClient) -> None:
    """Analyze a document from a URL using prebuilt-documentSearch analyzer."""

    document_url = "https://github.com/Azure-Samples/azure-ai-content-understanding-python/raw/refs/heads/main/data/invoice.pdf"

    print(f"Analyzing document from URL with prebuilt-documentSearch...")
    print(f"  URL: {document_url}")

    poller = client.begin_analyze(
        analyzer_id="prebuilt-documentSearch",
        inputs=[AnalyzeInput(url=document_url)],
    )
    result: AnalyzeResult = poller.result()

    # Extract markdown content
    print("\nMarkdown Content:")
    print("=" * 50)

    if result.contents and len(result.contents) > 0:
        content = result.contents[0]
        if content.markdown:
            print(content.markdown)
        else:
            print("No markdown content available.")
    else:
        print("No content found in the analysis result.")

    print("=" * 50)

    # Display document properties
    if result.contents and len(result.contents) > 0:
        content = result.contents[0]
        if content.kind == MediaContentKind.DOCUMENT:
            document_content: DocumentContent = content  # type: ignore
            print(f"\nDocument Information:")
            print(f"  Start page: {document_content.start_page_number}")
            print(f"  End page: {document_content.end_page_number}")
# [END ContentUnderstandingAnalyzeUrlAsync]


if __name__ == "__main__":
    main()
