# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_create_classifier.py

DESCRIPTION:
    This sample demonstrates how to create a classifier analyzer to categorize documents and
    use it to analyze documents with and without automatic segmentation.

    Classifiers are a type of custom analyzer that categorize documents into predefined categories.
    They're useful for:
    - Document routing: Automatically route documents to the right processing pipeline
    - Content organization: Organize large document collections by type
    - Multi-document processing: Process files containing multiple document types by segmenting them

USAGE:
    python sample_create_classifier.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using classifiers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_configure_defaults.py for setup instructions.
"""

import os
import time

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentCategoryDefinition,
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

    # Create a classifier
    analyzer_id = create_classifier(client)

    # Analyze with the classifier (demonstrates both with and without segmentation)
    if analyzer_id:
        analyze_with_classifier(client, analyzer_id)

        # Clean up - delete the classifier
        print(f"\nCleaning up: deleting classifier '{analyzer_id}'...")
        client.delete_analyzer(analyzer_id=analyzer_id)
        print(f"Classifier '{analyzer_id}' deleted successfully.")


# [START ContentUnderstandingCreateClassifier]
def create_classifier(client: ContentUnderstandingClient) -> str:
    """Create a classifier analyzer with content categories."""

    # Generate a unique analyzer ID
    analyzer_id = f"my_classifier_{int(time.time())}"

    print(f"Creating classifier '{analyzer_id}'...")

    # Define content categories for classification
    categories = {
        "Loan_Application": ContentCategoryDefinition(
            description="Documents submitted by individuals or businesses to request funding, "
            "typically including personal or business details, financial history, "
            "loan amount, purpose, and supporting documentation."
        ),
        "Invoice": ContentCategoryDefinition(
            description="Billing documents issued by sellers or service providers to request "
            "payment for goods or services, detailing items, prices, taxes, totals, "
            "and payment terms."
        ),
        "Bank_Statement": ContentCategoryDefinition(
            description="Official statements issued by banks that summarize account activity "
            "over a period, including deposits, withdrawals, fees, and balances."
        ),
    }

    # Create analyzer configuration
    config = ContentAnalyzerConfig(
        return_details=True,
        enable_segment=True,  # Enable automatic segmentation by category
        content_categories=categories,
    )

    # Create the classifier analyzer
    classifier = ContentAnalyzer(
        base_analyzer_id="prebuilt-document",
        description="Custom classifier for financial document categorization",
        config=config,
        models={"completion": "gpt-4.1"},
    )

    # Create the classifier
    poller = client.begin_create_analyzer(
        analyzer_id=analyzer_id,
        resource=classifier,
    )
    result = poller.result()

    print(f"Classifier '{analyzer_id}' created successfully!")
    print(f"  Status: {result.status}")

    return analyzer_id
# [END ContentUnderstandingCreateClassifier]


# [START ContentUnderstandingAnalyzeCategory]
def analyze_with_classifier(client: ContentUnderstandingClient, analyzer_id: str) -> None:
    """Analyze a document with the classifier."""

    file_path = "sample_files/sample_invoice.pdf"

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    print(f"\nAnalyzing document with classifier '{analyzer_id}'...")

    poller = client.begin_analyze_binary(
        analyzer_id=analyzer_id,
        binary_input=file_bytes,
    )
    result: AnalyzeResult = poller.result()

    # Display classification results
    display_classification_results(result)
# [END ContentUnderstandingAnalyzeCategory]


# [START ContentUnderstandingAnalyzeCategoryWithSegments]
def display_classification_results(result: AnalyzeResult) -> None:
    """Display classification results including segments if available."""

    if not result.contents or len(result.contents) == 0:
        print("No content found in the analysis result.")
        return

    content = result.contents[0]

    if content.kind == MediaContentKind.DOCUMENT:
        document_content: DocumentContent = content  # type: ignore
        print(f"Pages: {document_content.start_page_number}-{document_content.end_page_number}")

        # Display segments (classification results)
        if document_content.segments and len(document_content.segments) > 0:
            print(f"\nFound {len(document_content.segments)} segment(s):")
            for segment in document_content.segments:
                print(f"  Category: {segment.category or '(unknown)'}")
                print(f"  Pages: {segment.start_page_number}-{segment.end_page_number}")
                if segment.confidence:
                    print(f"  Confidence: {segment.confidence:.2f}")
                print()
        else:
            print("No segments found (document classified as a single unit).")
# [END ContentUnderstandingAnalyzeCategoryWithSegments]


if __name__ == "__main__":
    main()
