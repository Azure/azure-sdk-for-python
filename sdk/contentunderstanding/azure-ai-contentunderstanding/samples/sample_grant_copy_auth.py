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
    Microsoft Foundry resource to a target Microsoft Foundry resource (cross-resource copying).
    This is useful for copying analyzers between different Azure resources or subscriptions.

    About cross-resource copying
    The grant_copy_authorization and begin_copy_analyzer APIs allow you to copy an analyzer
    between different Azure resources:
    - Cross-resource copy: Copies an analyzer from one Azure resource to another
    - Authorization required: You must grant copy authorization before copying

    When to use cross-resource copying:
    - Copy between subscriptions: Move analyzers between different Azure subscriptions
    - Multi-region deployment: Deploy the same analyzer to multiple regions
    - Resource migration: Migrate analyzers from one resource to another
    - Environment promotion: Promote analyzers from development to production across resources

    Note: For same-resource copying (copying within the same Microsoft Foundry resource),
    use the sample_copy_analyzer.py sample instead.

PREREQUISITES:
    To get started you'll need a Microsoft Foundry resource. See Sample 00: Configure model
    deployment defaults for setup guidance. For this cross-resource scenario, you'll also need:
    - Source Microsoft Foundry resource with model deployments configured
    - Target Microsoft Foundry resource with model deployments configured

    Important: Both the source and target resources require the 'Cognitive Services User' role
    to be granted to the credential used to run the code. This role is required for cross-resource
    copying operations. Without this role, the grant_copy_authorization and begin_copy_analyzer
    operations will fail with authorization errors.

HOW AUTHORIZATION WORKS:
    The grant_copy_authorization method must be called on the source Microsoft Foundry resource
    (where the analyzer currently exists). This is because the source resource needs to explicitly
    grant permission for its analyzer to be copied. The method creates a time-limited authorization
    record that grants permission to a specific target resource. The method takes:
    - The source analyzer ID to be copied
    - The target Azure resource ID that is allowed to receive the copy
    - The target region where the copy will be performed (optional, defaults to current region)

    The method returns a CopyAuthorization object containing:
    - The full path of the source analyzer
    - The target Azure resource ID
    - An expiration timestamp for the authorization

    Where copy is performed: The begin_copy_analyzer method must be called on the target Microsoft
    Foundry resource (where the analyzer will be copied to). This is because the target resource
    is the one receiving and creating the copy. When the target resource calls begin_copy_analyzer,
    the service validates that authorization was previously granted by the source resource. The
    authorization must be active (not expired) and match the target resource ID and region
    specified in the copy request.

USAGE:
    python sample_grant_copy_auth.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the source endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).
    3) CONTENTUNDERSTANDING_SOURCE_RESOURCE_ID - Full Azure Resource Manager resource ID of source.
    4) CONTENTUNDERSTANDING_SOURCE_REGION - Azure region of source resource.
    5) CONTENTUNDERSTANDING_TARGET_ENDPOINT - Target endpoint for cross-subscription copy.
    6) CONTENTUNDERSTANDING_TARGET_RESOURCE_ID - Full Azure Resource Manager resource ID of target.
    7) CONTENTUNDERSTANDING_TARGET_REGION - Azure region of target resource.
    8) CONTENTUNDERSTANDING_TARGET_KEY - Target API key (optional if using DefaultAzureCredential).

    Example resource ID format:
    /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.CognitiveServices/accounts/{name}

    Important: Cross-resource copying requires credential-based authentication (such as DefaultAzureCredential).
    API keys cannot be used for cross-resource operations.
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
        "CONTENTUNDERSTANDING_ENDPOINT",
        "CONTENTUNDERSTANDING_SOURCE_RESOURCE_ID",
        "CONTENTUNDERSTANDING_SOURCE_REGION",
        "CONTENTUNDERSTANDING_TARGET_ENDPOINT",
        "CONTENTUNDERSTANDING_TARGET_RESOURCE_ID",
        "CONTENTUNDERSTANDING_TARGET_REGION",
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
    source_endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    source_key = os.getenv("CONTENTUNDERSTANDING_KEY")
    source_credential = AzureKeyCredential(source_key) if source_key else DefaultAzureCredential()

    source_resource_id = os.environ["CONTENTUNDERSTANDING_SOURCE_RESOURCE_ID"]
    source_region = os.environ["CONTENTUNDERSTANDING_SOURCE_REGION"]

    # Get target configuration
    target_endpoint = os.environ["CONTENTUNDERSTANDING_TARGET_ENDPOINT"]
    target_key = os.getenv("CONTENTUNDERSTANDING_TARGET_KEY")
    target_credential = AzureKeyCredential(target_key) if target_key else DefaultAzureCredential()

    target_resource_id = os.environ["CONTENTUNDERSTANDING_TARGET_RESOURCE_ID"]
    target_region = os.environ["CONTENTUNDERSTANDING_TARGET_REGION"]

    # Create source and target clients using DefaultAzureCredential
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
        # The analyzer must exist in the source resource before it can be copied
        print(f"\nStep 1: Creating source analyzer '{source_analyzer_id}'...")

        source_config = ContentAnalyzerConfig(
            enable_formula=False,
            enable_layout=True,
            enable_ocr=True,
            estimate_field_source_and_confidence=True,
            return_details=True,
        )

        source_field_schema = ContentFieldSchema(
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
        )

        source_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Source analyzer for cross-resource copying",
            config=source_config,
            field_schema=source_field_schema,
            models={"completion": "gpt-4.1"},
        )

        poller = source_client.begin_create_analyzer(
            analyzer_id=source_analyzer_id,
            resource=source_analyzer,
        )
        poller.result()
        print(f"  Source analyzer created successfully!")

        # Step 2: Grant copy authorization
        # Authorization must be granted by the source resource before the target resource can copy
        # The grant_copy_authorization method takes:
        # - The source analyzer ID to be copied
        # - The target Azure resource ID that is allowed to receive the copy
        # - The target region where the copy will be performed (optional, defaults to current region)
        print(f"\nStep 2: Granting copy authorization from source resource...")
        print(f"  Target Azure Resource ID: {target_resource_id}")
        print(f"  Target Region: {target_region}")

        copy_auth = source_client.grant_copy_authorization(
            analyzer_id=source_analyzer_id,
            target_azure_resource_id=target_resource_id,
            target_region=target_region,
        )

        print(f"  Authorization granted successfully!")
        print(f"  Target Azure Resource ID: {copy_auth.target_azure_resource_id}")
        print(f"  Target Region: {target_region}")
        print(f"  Expires at: {copy_auth.expires_at}")

        # Step 3: Copy analyzer to target resource
        # The copy_analyzer method must be called on the target client because the target
        # resource is the one receiving and creating the copy. The target resource validates
        # that authorization was previously granted by the source resource.
        print(f"\nStep 3: Copying analyzer from source to target...")
        print(f"  Source Analyzer ID: {source_analyzer_id}")
        print(f"  Source Azure Resource ID: {source_resource_id}")
        print(f"  Source Region: {source_region}")
        print(f"  Target Analyzer ID: {target_analyzer_id}")

        copy_poller = target_client.begin_copy_analyzer(
            analyzer_id=target_analyzer_id,
            source_analyzer_id=source_analyzer_id,
            source_azure_resource_id=source_resource_id,
            source_region=source_region,
        )
        copy_poller.result()
        print(f"  Analyzer copied successfully to target resource!")

        # Step 4: Verify the copy
        # Retrieve the analyzer from the target resource to verify the copy was successful
        print(f"\nStep 4: Verifying the copied analyzer...")
        copied_analyzer = target_client.get_analyzer(analyzer_id=target_analyzer_id)
        print(f"  Target Analyzer ID: {copied_analyzer.analyzer_id}")
        print(f"  Description: {copied_analyzer.description}")
        print(f"  Status: {copied_analyzer.status}")
        print(f"\nCross-resource copy completed successfully!")

    finally:
        # Clean up: Delete both source and target analyzers
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
