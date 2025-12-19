# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_create_classifier_async.py

DESCRIPTION:
    This sample demonstrates how to create a classifier analyzer to categorize documents and
    use it to analyze documents with and without automatic segmentation.

    Classifiers are a type of custom analyzer that categorize documents into predefined categories.
    They're useful for:
    - Document routing: Automatically route documents to the right processing pipeline
    - Content organization: Organize large document collections by type
    - Multi-document processing: Process files containing multiple document types by segmenting them

USAGE:
    python sample_create_classifier_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using classifiers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_update_defaults.py for setup instructions.
"""

import asyncio
import os
import time

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentCategoryDefinition,
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
        # [START create_classifier]
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
        poller = await client.begin_create_analyzer(
            analyzer_id=analyzer_id,
            resource=classifier,
        )
        result = await poller.result()  # Wait for creation to complete

        # Get the full analyzer details after creation
        result = await client.get_analyzer(analyzer_id=analyzer_id)

        print(f"Classifier '{analyzer_id}' created successfully!")
        if result.description:
            print(f"  Description: {result.description}")
        # [END create_classifier]

        # [START analyze_with_classifier]
        file_path = "sample_files/mixed_financial_docs.pdf"

        with open(file_path, "rb") as f:
            file_bytes = f.read()

        print(f"\nAnalyzing document with classifier '{analyzer_id}'...")

        analyze_poller = await client.begin_analyze_binary(
            analyzer_id=analyzer_id,
            binary_input=file_bytes,
        )
        analyze_result: AnalyzeResult = await analyze_poller.result()

        # Display classification results
        if analyze_result.contents and len(analyze_result.contents) > 0:
            document_content: DocumentContent = analyze_result.contents[0]  # type: ignore
            print(f"Pages: {document_content.start_page_number}-{document_content.end_page_number}")

            # Display segments (classification results)
            if document_content.segments and len(document_content.segments) > 0:
                print(f"\nFound {len(document_content.segments)} segment(s):")
                for segment in document_content.segments:
                    print(f"  Category: {segment.category or '(unknown)'}")
                    print(f"  Pages: {segment.start_page_number}-{segment.end_page_number}")
                    print()
            else:
                print("No segments found (document classified as a single unit).")
        else:
            print("No content found in the analysis result.")
        # [END analyze_with_classifier]

        # Clean up - delete the classifier
        print(f"\nCleaning up: deleting classifier '{analyzer_id}'...")
        await client.delete_analyzer(analyzer_id=analyzer_id)
        print(f"Classifier '{analyzer_id}' deleted successfully.")

    if not isinstance(credential, AzureKeyCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
