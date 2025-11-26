# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_copy_analyzer.py

DESCRIPTION:
    This sample demonstrates how to copy an analyzer from source to target within the same
    resource using the copy_analyzer API. This is useful for creating copies of analyzers
    for testing, staging, or production deployment.

    The copy_analyzer API allows you to copy an analyzer within the same Azure resource:
    - Same-resource copy: Copies an analyzer from one ID to another within the same resource
    - Exact copy: The target analyzer is an exact copy of the source analyzer
    - Use cases: Testing, staging, production deployment, versioning

    Note: For cross-resource copying (copying between different Azure resources or subscriptions),
    use the grant_copy_auth sample instead.

USAGE:
    python sample_copy_analyzer.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).
"""

import os
import time

from dotenv import load_dotenv
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentFieldSchema,
    ContentFieldDefinition,
    ContentFieldType,
    GenerationMethod,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

load_dotenv()


def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

    # Copy analyzer from source to target
    copy_analyzer_demo(client)


def copy_analyzer_demo(client: ContentUnderstandingClient) -> None:
    """Demonstrate copying an analyzer from source to target."""

    base_id = f"my_analyzer_{int(time.time())}"
    source_analyzer_id = f"{base_id}_source"
    target_analyzer_id = f"{base_id}_target"

    # Step 1: Create the source analyzer
    create_source_analyzer(client, source_analyzer_id)

    # Step 2: Copy the analyzer
    copy_analyzer(client, source_analyzer_id, target_analyzer_id)

    # Step 3: Update and verify the target analyzer
    update_and_verify_analyzer(client, target_analyzer_id)

    # Step 4: Clean up
    cleanup_analyzers(client, source_analyzer_id, target_analyzer_id)


def create_source_analyzer(client: ContentUnderstandingClient, analyzer_id: str) -> None:
    """Create the source analyzer."""

    print(f"Creating source analyzer '{analyzer_id}'...")

    analyzer = ContentAnalyzer(
        base_analyzer_id="prebuilt-document",
        description="Source analyzer for copy example",
        config=ContentAnalyzerConfig(
            enable_formula=False,
            enable_layout=True,
            enable_ocr=True,
            estimate_field_source_and_confidence=True,
            return_details=True,
        ),
        field_schema=ContentFieldSchema(
            name="company_schema",
            description="Schema for extracting company information",
            fields={
                "company_name": ContentFieldDefinition(
                    type=ContentFieldType.STRING,
                    method=GenerationMethod.EXTRACT,
                    description="Name of the company",
                ),
                "total_amount": ContentFieldDefinition(
                    type=ContentFieldType.NUMBER,
                    method=GenerationMethod.EXTRACT,
                    description="Total amount on the document",
                ),
            },
        ),
        models={"completion": "gpt-4.1"},
    )

    poller = client.begin_create_analyzer(
        analyzer_id=analyzer_id,
        resource=analyzer,
    )
    poller.result()
    print(f"Source analyzer '{analyzer_id}' created successfully!")


# [START ContentUnderstandingCopyAnalyzer]
def copy_analyzer(client: ContentUnderstandingClient, source_analyzer_id: str, target_analyzer_id: str) -> None:
    """Copy an analyzer from source to target."""

    print(f"\nCopying analyzer from '{source_analyzer_id}' to '{target_analyzer_id}'...")

    poller = client.begin_copy_analyzer(
        target_analyzer_id=target_analyzer_id,
        source_analyzer_id=source_analyzer_id,
    )
    poller.result()

    print(f"Analyzer copied successfully!")
# [END ContentUnderstandingCopyAnalyzer]


# [START ContentUnderstandingUpdateAndVerifyAnalyzer]
def update_and_verify_analyzer(client: ContentUnderstandingClient, analyzer_id: str) -> None:
    """Update the target analyzer with a production tag and verify."""

    # Get the target analyzer first to get its BaseAnalyzerId
    print(f"\nGetting target analyzer '{analyzer_id}'...")
    target_analyzer = client.get_analyzer(analyzer_id=analyzer_id)

    # Update the target analyzer with a production tag
    updated_analyzer = ContentAnalyzer(
        base_analyzer_id=target_analyzer.base_analyzer_id,
        tags={"modelType": "model_in_production"},
    )

    print(f"Updating target analyzer with production tag...")
    client.update_analyzer(analyzer_id=analyzer_id, resource=updated_analyzer)

    # Verify the update
    updated_target = client.get_analyzer(analyzer_id=analyzer_id)
    print(f"  Description: {updated_target.description}")
    if updated_target.tags:
        print(f"  Tag 'modelType': {updated_target.tags.get('modelType', 'N/A')}")
# [END ContentUnderstandingUpdateAndVerifyAnalyzer]


# [START ContentUnderstandingDeleteCopiedAnalyzers]
def cleanup_analyzers(client: ContentUnderstandingClient, source_analyzer_id: str, target_analyzer_id: str) -> None:
    """Clean up by deleting both source and target analyzers."""

    print(f"\nCleaning up analyzers...")

    try:
        client.delete_analyzer(analyzer_id=source_analyzer_id)
        print(f"  Source analyzer '{source_analyzer_id}' deleted successfully.")
    except Exception:
        pass  # Ignore cleanup errors

    try:
        client.delete_analyzer(analyzer_id=target_analyzer_id)
        print(f"  Target analyzer '{target_analyzer_id}' deleted successfully.")
    except Exception:
        pass  # Ignore cleanup errors
# [END ContentUnderstandingDeleteCopiedAnalyzers]


if __name__ == "__main__":
    main()
