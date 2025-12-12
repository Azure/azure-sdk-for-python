# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_grant_copy_auth.py

DESCRIPTION:
    This sample demonstrates how to grant copy authorization and copy an analyzer from a source
    resource to a target resource (cross-resource copying). This is useful for copying analyzers
    between different Azure resources or subscriptions.

    The grant_copy_authorization and copy_analyzer APIs allow you to copy an analyzer between
    different Azure resources:
    - Cross-resource copy: Copies an analyzer from one Azure resource to another
    - Authorization required: You must grant copy authorization before copying
    - Use cases: Cross-subscription copying, resource migration, multi-region deployment

    Note: For same-resource copying (copying within the same Azure resource), use the
    sample_copy_analyzer.py sample instead.

USAGE:
    python sample_grant_copy_auth.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the source endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).
    3) AZURE_CONTENT_UNDERSTANDING_SOURCE_RESOURCE_ID - Full Azure Resource Manager resource ID of source.
    4) AZURE_CONTENT_UNDERSTANDING_SOURCE_REGION - Azure region of source resource.
    5) AZURE_CONTENT_UNDERSTANDING_TARGET_ENDPOINT - Target endpoint for cross-subscription copy.
    6) AZURE_CONTENT_UNDERSTANDING_TARGET_RESOURCE_ID - Full Azure Resource Manager resource ID of target.
    7) AZURE_CONTENT_UNDERSTANDING_TARGET_REGION - Azure region of target resource.
    8) AZURE_CONTENT_UNDERSTANDING_TARGET_KEY - Target API key (optional if using DefaultAzureCredential).

    Example resource ID format:
    /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.CognitiveServices/accounts/{name}

    Note: Both source and target AI Foundry Resources require 'Cognitive Services User' role for cross-subscription copy.
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
    # Check for required environment variables
    required_vars = [
        "AZURE_CONTENT_UNDERSTANDING_ENDPOINT",
        "AZURE_CONTENT_UNDERSTANDING_SOURCE_RESOURCE_ID",
        "AZURE_CONTENT_UNDERSTANDING_SOURCE_REGION",
        "AZURE_CONTENT_UNDERSTANDING_TARGET_ENDPOINT",
        "AZURE_CONTENT_UNDERSTANDING_TARGET_RESOURCE_ID",
        "AZURE_CONTENT_UNDERSTANDING_TARGET_REGION",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these environment variables and try again.")
        print("\nExample resource ID format:")
        print(
            "  /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.CognitiveServices/accounts/{name}"
        )
        return

    # [START grant_copy_auth]
    # Get source configuration
    source_endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    source_key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    source_credential = AzureKeyCredential(source_key) if source_key else DefaultAzureCredential()

    source_resource_id = os.environ["AZURE_CONTENT_UNDERSTANDING_SOURCE_RESOURCE_ID"]
    source_region = os.environ["AZURE_CONTENT_UNDERSTANDING_SOURCE_REGION"]

    # Get target configuration
    target_endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_TARGET_ENDPOINT"]
    target_key = os.getenv("AZURE_CONTENT_UNDERSTANDING_TARGET_KEY")
    target_credential = AzureKeyCredential(target_key) if target_key else DefaultAzureCredential()

    target_resource_id = os.environ["AZURE_CONTENT_UNDERSTANDING_TARGET_RESOURCE_ID"]
    target_region = os.environ["AZURE_CONTENT_UNDERSTANDING_TARGET_REGION"]

    # Create clients
    source_client = ContentUnderstandingClient(endpoint=source_endpoint, credential=source_credential)
    target_client = ContentUnderstandingClient(endpoint=target_endpoint, credential=target_credential)

    # Generate unique analyzer IDs
    base_id = f"my_analyzer_{int(time.time())}"
    source_analyzer_id = f"{base_id}_source"
    target_analyzer_id = f"{base_id}_target"

    print("Cross-Resource Copy Workflow")
    print("=" * 60)
    print(f"  Source Endpoint: {source_endpoint}")
    print(f"  Source Region: {source_region}")
    print(f"  Target Endpoint: {target_endpoint}")
    print(f"  Target Region: {target_region}")
    print("=" * 60)

    try:
        # Step 1: Create the source analyzer
        print(f"\nStep 1: Creating source analyzer '{source_analyzer_id}'...")

        source_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Source analyzer for cross-resource copying",
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

        poller = source_client.begin_create_analyzer(
            analyzer_id=source_analyzer_id,
            resource=source_analyzer,
        )
        poller.result()
        print(f"  Source analyzer created successfully!")

        # Step 2: Grant copy authorization from source
        # Grant authorization on the source client for copying to the target resource
        print(f"\nStep 2: Granting copy authorization from source resource...")

        copy_auth = source_client.grant_copy_authorization(
            analyzer_id=source_analyzer_id,
            target_azure_resource_id=target_resource_id,
            target_region=target_region,
        )

        print(f"  Authorization granted!")
        print(f"  Target Azure Resource ID: {copy_auth.target_azure_resource_id}")
        print(f"  Target Region: {target_region}")
        print(f"  Expires at: {copy_auth.expires_at}")

        # Step 3: Copy analyzer using authorization
        # Copy is performed on the target client, copying from source to target
        print(f"\nStep 3: Copying analyzer from source to target...")

        copy_poller = target_client.begin_copy_analyzer(
            analyzer_id=target_analyzer_id,
            source_analyzer_id=source_analyzer_id,
            source_azure_resource_id=source_resource_id,
            source_region=source_region,
        )
        copy_poller.result()
        print(f"  Analyzer copied successfully!")

        # Step 4: Verify the copy
        print(f"\nStep 4: Verifying the copied analyzer...")
        copied_analyzer = target_client.get_analyzer(analyzer_id=target_analyzer_id)
        print(f"  Target Analyzer ID: {copied_analyzer.analyzer_id}")
        print(f"  Description: {copied_analyzer.description}")
        print(f"  Status: {copied_analyzer.status}")

    finally:
        # Clean up
        print(f"\nCleaning up...")
        try:
            source_client.delete_analyzer(analyzer_id=source_analyzer_id)
            print(f"  Source analyzer '{source_analyzer_id}' deleted.")
        except Exception:
            pass

        try:
            target_client.delete_analyzer(analyzer_id=target_analyzer_id)
            print(f"  Target analyzer '{target_analyzer_id}' deleted.")
        except Exception:
            pass
    # [END grant_copy_auth]


if __name__ == "__main__":
    main()
