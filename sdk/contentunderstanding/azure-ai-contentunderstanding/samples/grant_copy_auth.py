# pylint: disable=line-too-long,useless-suppression

# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: grant copy authorization and copy an analyzer from source to target.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT           (required) - Source endpoint
    AZURE_CONTENT_UNDERSTANDING_KEY                (optional - DefaultAzureCredential() will be used if not set)
    AZURE_CONTENT_UNDERSTANDING_SOURCE_RESOURCE_ID (required) - Full Azure Resource Manager resource ID of source
    AZURE_CONTENT_UNDERSTANDING_SOURCE_REGION      (required) - Azure region of source resource
    AZURE_CONTENT_UNDERSTANDING_TARGET_ENDPOINT    (required) - Target endpoint for cross-subscription copy
    AZURE_CONTENT_UNDERSTANDING_TARGET_RESOURCE_ID (required) - Full Azure Resource Manager resource ID of target
    AZURE_CONTENT_UNDERSTANDING_TARGET_REGION      (required) - Azure region of target resource
    AZURE_CONTENT_UNDERSTANDING_TARGET_KEY         (optional) - Target API key if different from source
    Example resource ID format: /subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.CognitiveServices/accounts/{name}
    Note: Both source and target AI Foundry Resources require Cognitive Services User Role for cross-subscription copy
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python grant_copy_auth.py
"""

from __future__ import annotations
import asyncio
import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentFieldSchema,
    ContentFieldDefinition,
    ContentFieldType,
    GenerationMethod,
    CopyAuthorization,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


# ---------------------------------------------------------------------------
# Sample: Grant copy authorization and copy analyzer from source to target
# ---------------------------------------------------------------------------
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Create a source analyzer
# 3. Grant copy authorization for copying the analyzer
# 4. Print the authorization result
# 5. Copy the source analyzer to target
# 6. Wait for copy operation to complete
# 7. Clean up both analyzers


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    print(f"Using endpoint: {endpoint}")
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as source_client:
        base_analyzer_id = f"sdk_sample_custom_analyzer_{int(asyncio.get_event_loop().time())}"
        source_analyzer_id = f"{base_analyzer_id}_source"
        target_analyzer_id = f"{base_analyzer_id}_target"

        # Step 1: Create the source analyzer
        print(f"Creating source analyzer '{source_analyzer_id}'...")
        
        # Create a custom analyzer using object model (following pattern from create_analyzer.py)
        source_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Source analyzer for extracting company information",
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
                    # EXTRACT: Extract information directly from document content
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
                    # GENERATE: AI generates content based on document understanding
                    "document_summary": ContentFieldDefinition(
                        type=ContentFieldType.STRING,
                        method=GenerationMethod.GENERATE,
                        description="A concise summary of the document's main content",
                    ),
                    "key_insights": ContentFieldDefinition(
                        type=ContentFieldType.STRING,
                        method=GenerationMethod.GENERATE,
                        description="Key business insights or actionable items from the document",
                    )
                },
            ),
            models={"completion": "gpt-4.1"},  # Required when using field_schema
        )

        poller = await source_client.begin_create_analyzer(
            analyzer_id=source_analyzer_id,
            resource=source_analyzer,
        )
        source_result = await poller.result()
        print(f"Source analyzer '{source_analyzer_id}' created successfully!")
        print(f"Source analyzer tags: {source_result.tags}")

        # Step 2: Grant copy authorization before copying
        print(f"\nGranting copy authorization for analyzer '{source_analyzer_id}'...")
        
        # Source Azure Resource Manager resource ID (where the analyzer currently exists)
        source_resource_id = os.environ["AZURE_CONTENT_UNDERSTANDING_SOURCE_RESOURCE_ID"]
        source_region = os.environ["AZURE_CONTENT_UNDERSTANDING_SOURCE_REGION"]
        
        # Target endpoint and region for cross-subscription copy
        target_endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_TARGET_ENDPOINT"]
        target_region = os.environ["AZURE_CONTENT_UNDERSTANDING_TARGET_REGION"]
        
        # Target resource ID (where we want to copy the analyzer to)
        target_resource_id = os.environ["AZURE_CONTENT_UNDERSTANDING_TARGET_RESOURCE_ID"]
        
        copy_auth: CopyAuthorization = await source_client.grant_copy_authorization(
            analyzer_id=source_analyzer_id,
            target_azure_resource_id=target_resource_id,
            target_region=target_region,
        )
        
        # Step 3: Print the authorization result
        print(f"\nCopy authorization granted successfully!")
        print(f"Authorization details:")
        print(f"  Source: {copy_auth.source}")
        print(f"  Target Azure Resource ID: {copy_auth.target_azure_resource_id}")
        print(f"  Target Region: {target_region}")
        print(f"  Expires at: {copy_auth.expires_at}")

        # Step 4: Create target client for cross-subscription copy
        print(f"\nCreating target client for cross-subscription copy...")
        print(f"Target endpoint: {target_endpoint}")
        print(f"Target region: {target_region}")
        
        # Create target client with the target endpoint
        # Use the same credential (should work across subscriptions if properly configured)
        target_key = os.getenv("AZURE_CONTENT_UNDERSTANDING_TARGET_KEY")
        target_credential = AzureKeyCredential(target_key) if target_key else DefaultAzureCredential()
        
        async with ContentUnderstandingClient(endpoint=target_endpoint, credential=target_credential) as target_client:
            # Step 5: Copy the source analyzer to target using begin_copy_analyzer API on target client
            print(f"\nCopying analyzer from '{source_analyzer_id}' to '{target_analyzer_id}' on target subscription...")
            print(f"Source resource ID: {source_resource_id}")
            print(f"Source region: {source_region}")
            print(f"Target region: {target_region}")
            
            # For cross-subscription copy, use parameters to specify source location
            # Note: Copy authorization was granted above, but we'll use parameters instead of the CopyAuthorization object
            # since the CopyAuthorization might not be correctly populated (source: None)
            try:
                copy_poller = await target_client.begin_copy_analyzer(
                    analyzer_id=target_analyzer_id,
                    source_analyzer_id=source_analyzer_id,
                    source_azure_resource_id=source_resource_id,
                    source_region=source_region,
                )
                target_result = await copy_poller.result()
                print(f"Target analyzer '{target_analyzer_id}' copied successfully to target subscription!")
                print(f"Target analyzer tags (before update): {target_result.tags}")
            except Exception as e:
                print(f"Error copying analyzer: {e}")
                print("Note: The copy operation may not be available on all service endpoints or may require additional permissions.")
                # Continue to cleanup section
                raise

            # Step 6: Get the target analyzer using target client and dump values
            print(f"\nRetrieving target analyzer '{target_analyzer_id}' from target client...")
            retrieved_analyzer = await target_client.get_analyzer(analyzer_id=target_analyzer_id)
            
            # Dump all analyzer values
            print(f"\n=== Target Analyzer Details ===")
            print(f"Analyzer ID: {retrieved_analyzer.analyzer_id}")
            print(f"Description: {retrieved_analyzer.description}")
            print(f"Status: {retrieved_analyzer.status}")
            print(f"Created at: {retrieved_analyzer.created_at}")
            print(f"Last modified: {retrieved_analyzer.last_modified_at}")
            print(f"Tags: {retrieved_analyzer.tags}")
            if retrieved_analyzer.base_analyzer_id:
                print(f"Base analyzer ID: {retrieved_analyzer.base_analyzer_id}")
            if retrieved_analyzer.config:
                print(f"Config: {retrieved_analyzer.config}")
            if retrieved_analyzer.field_schema:
                print(f"Field schema name: {retrieved_analyzer.field_schema.name}")
                print(f"Field schema description: {retrieved_analyzer.field_schema.description}")
                if retrieved_analyzer.field_schema.fields:
                    print(f"Number of fields: {len(retrieved_analyzer.field_schema.fields)}")
                    for field_name, field_def in retrieved_analyzer.field_schema.fields.items():
                        print(f"  - {field_name}: {field_def.type} ({field_def.method})")
            if retrieved_analyzer.models:
                print(f"Models: {retrieved_analyzer.models}")
            print(f"=== End Target Analyzer Details ===\n")

            # Update the target analyzer tags if needed
            # Since copy may not preserve or set tags, we update after copying
            print(f"\nUpdating target analyzer '{target_analyzer_id}' tags...")
            updated_target_analyzer = ContentAnalyzer(
                tags={"copiedFrom": source_analyzer_id}
            )
            final_target_result = await target_client.update_analyzer(
                analyzer_id=target_analyzer_id,
                resource=updated_target_analyzer,
            )
            print(f"Target analyzer '{target_analyzer_id}' updated successfully!")
            print(f"Target analyzer tags: {final_target_result.tags}")
            
            # Clean up the target analyzer on target subscription
            print(f"\nDeleting target analyzer '{target_analyzer_id}' from target subscription (demo cleanup)...")
            await target_client.delete_analyzer(analyzer_id=target_analyzer_id)
            print(f"Target analyzer '{target_analyzer_id}' deleted successfully from target subscription!")
        
        # Manually close DefaultAzureCredential if it was used for target client
        if isinstance(target_credential, DefaultAzureCredential):
            await target_credential.close()

        # Clean up the created analyzers (demo cleanup)
        print(f"\nDeleting analyzers (demo cleanup)...")
        print(f"Deleting source analyzer '{source_analyzer_id}'...")
        await source_client.delete_analyzer(analyzer_id=source_analyzer_id)
        print(f"Source analyzer '{source_analyzer_id}' deleted successfully!")
        
        # Note: Target analyzer is already deleted from target subscription above
        print(f"Target analyzer '{target_analyzer_id}' was already deleted from target subscription.")

    # Manually close DefaultAzureCredential if it was used
    if isinstance(credential, DefaultAzureCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())

