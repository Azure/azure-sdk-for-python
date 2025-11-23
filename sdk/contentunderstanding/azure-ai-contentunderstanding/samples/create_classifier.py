# pylint: disable=line-too-long,useless-suppression

# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: create a classifier to categorize documents.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python create_classifier.py
"""

from __future__ import annotations
import asyncio
import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentCategoryDefinition,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


# ---------------------------------------------------------------------------
# Sample: Create a classifier for document categorization
# ---------------------------------------------------------------------------
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Create a custom classifier with content categories
# 3. Configure the classifier to segment multi-document files
# 4. Wait for classifier creation to complete
# 5. Verify the classifier was created successfully
# 6. Clean up by deleting the classifier
#
# Note: In Azure AI Content Understanding, classification is integrated into
# analyzers using the contentCategories configuration. The enableSegment parameter
# controls whether to split multi-document files (e.g., a loan package with multiple forms).


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    print(f"Using endpoint: {endpoint}")
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        await create_document_classifier(client)

    # Manually close DefaultAzureCredential if it was used
    if isinstance(credential, DefaultAzureCredential):
        await credential.close()


async def create_document_classifier(client: ContentUnderstandingClient) -> None:
    """Create and configure a classifier for document categorization."""

    # Generate a unique classifier ID
    analyzer_id = f"sdk_sample_classifier_{int(asyncio.get_event_loop().time())}"

    print(f"\n🔧 Creating classifier '{analyzer_id}'...")
    print("\nClassifier Configuration:")
    print("=" * 60)

    # Define content categories for classification
    # Each category has a name and description to guide the classification
    categories = {
        "Loan_Application": ContentCategoryDefinition(
            description=(
                "Documents submitted by individuals or businesses to request funding, "
                "typically including personal or business details, financial history, "
                "loan amount, purpose, and supporting documentation."
            )
        ),
        "Invoice": ContentCategoryDefinition(
            description=(
                "Billing documents issued by sellers or service providers to request "
                "payment for goods or services, detailing items, prices, taxes, totals, "
                "and payment terms."
            )
        ),
        "Bank_Statement": ContentCategoryDefinition(
            description=(
                "Official statements issued by banks that summarize account activity "
                "over a period, including deposits, withdrawals, fees, and balances."
            )
        ),
    }

    # Display the categories being configured
    print("   Content Categories:")
    for category_name, category_obj in categories.items():
        print(f"   • {category_name}")
        if category_obj.description:
            desc_preview = category_obj.description[:80] + "..." if len(category_obj.description) > 80 else category_obj.description
            print(f"     {desc_preview}")

    print("=" * 60)

    try:
        # Create classifier configuration
        # - base_analyzer_id: Use prebuilt-document for general document classification
        # - enable_segment: Split multi-document files and classify each segment
        # - return_details: Include detailed classification information
        # - content_categories: Define the classification categories
        classifier = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Custom classifier for financial document categorization",
            config=ContentAnalyzerConfig(
                return_details=True,
                enable_segment=True,  # Automatically split and classify multi-document files
                content_categories=categories,
            ),
            models={"completion": "gpt-4.1"},  # Model used for classification
            tags={"sample_type": "classifier_demo", "document_type": "financial"},
        )

        # Start the classifier creation operation
        print(f"\n⏳ Starting classifier creation operation...")
        poller = await client.begin_create_analyzer(
            analyzer_id=analyzer_id,
            resource=classifier,
        )

        # Wait for the operation to complete
        print(f"⏳ Waiting for classifier creation to complete...")
        result = await poller.result()
        print(f"\n✅ Classifier '{analyzer_id}' created successfully!")

        # Display any warnings from the creation process
        if result.warnings:
            print("\n⚠️  Warnings encountered while creating the classifier:")
            for warning in result.warnings:
                print(f"   - {warning}")

        # Retrieve the full analyzer details using get_analyzer
        print(f"\n📋 Retrieving classifier details...")
        analyzer_details = await client.get_analyzer(analyzer_id=analyzer_id)

        print("\nClassifier Properties:")
        print("=" * 60)
        print(f"   Analyzer ID: {analyzer_details.analyzer_id}")
        print(f"   Description: {analyzer_details.description}")
        print(f"   Base Analyzer: {analyzer_details.base_analyzer_id}")
        print(f"   Status: {analyzer_details.status}")

        if analyzer_details.config:
            if hasattr(analyzer_details.config, "enable_segment"):
                print(f"   Enable Segment: {analyzer_details.config.enable_segment}")
            if hasattr(analyzer_details.config, "content_categories") and analyzer_details.config.content_categories:
                print(f"   Categories: {len(analyzer_details.config.content_categories)}")
                for cat_name in analyzer_details.config.content_categories.keys():
                    print(f"     • {cat_name}")

        if analyzer_details.models:
            print(f"   Models: {analyzer_details.models}")

        if analyzer_details.tags:
            print(f"   Tags: {analyzer_details.tags}")

        print("=" * 60)

        print("\n💡 Usage Tips:")
        print("   • Use this classifier with begin_analyze() or begin_analyze_binary()")
        print("   • Set enable_segment=True to classify different document types in a single file")
        print("   • Each segment in the result will have a 'category' field with the classification")
        print("   • You can add up to 200 content categories per classifier")

        # Clean up: Delete the classifier
        print(f"\n🗑️  Cleaning up: Deleting classifier '{analyzer_id}'...")
        await client.delete_analyzer(analyzer_id=analyzer_id)
        print(f"✅ Classifier '{analyzer_id}' deleted successfully!")

    except Exception as e:
        print(f"\n❌ Error creating classifier: {e}")
        print("\nThis error may occur if:")
        print("   - The GPT-4.1 model deployment is not configured (run update_defaults.py)")
        print("   - You don't have permission to create analyzers")
        print("   - The analyzer ID already exists (try running the sample again)")
        print("\nTroubleshooting steps:")
        print("   1. Ensure default model deployments are configured (run get_defaults.py)")
        print("   2. Verify you have permissions to create analyzers")
        print("   3. Check that the endpoint and credentials are correct")
        raise


if __name__ == "__main__":
    asyncio.run(main())
