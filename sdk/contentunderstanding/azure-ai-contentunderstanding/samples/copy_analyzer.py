# pylint: disable=line-too-long,useless-suppression

# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: copy an analyzer from source to target using begin_copy_analyzer API.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python copy_analyzer.py
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
)
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


# ---------------------------------------------------------------------------
# Sample: Copy analyzer from source to target using begin_copy_analyzer API
# ---------------------------------------------------------------------------
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Create a source analyzer with tag "modelType": "in_development"
# 3. Copy the source analyzer to target with tag "modelType": "in_production"
# 4. Wait for copy operation to complete
# 5. Retrieve analyzer details using get_analyzer (workaround for service bug where result is empty)
# 6. Clean up both analyzers


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    print(f"Using endpoint: {endpoint}")
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        base_analyzer_id = f"sdk_sample_custom_analyzer_{int(asyncio.get_event_loop().time())}"
        source_analyzer_id = f"{base_analyzer_id}_source"
        target_analyzer_id = f"{base_analyzer_id}_target"

        # Step 1: Create the source analyzer with tag "modelType": "in_development"
        print(f"Creating source analyzer '{source_analyzer_id}' with tag 'modelType': 'in_development'...")
        
        # Create a custom analyzer using object model (following pattern from create_analyzer.py)
        source_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Source analyzer for extracting company information",
            tags={"modelType": "in_development"},
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

        poller = await client.begin_create_analyzer(
            analyzer_id=source_analyzer_id,
            resource=source_analyzer,
        )
        await poller.result()
        print(f"Source analyzer '{source_analyzer_id}' created successfully!")
        
        # Retrieve the full analyzer details using get_analyzer
        # Note: This is a workaround for a service bug where begin_create_analyzer result
        # returns empty/None values. See SERVICE-BUG.md Bug #3 for details.
        print(f"\nRetrieving source analyzer details using get_analyzer...")
        source_analyzer_details = await client.get_analyzer(analyzer_id=source_analyzer_id)
        print(f"\n=== Source Analyzer Details ===")
        print(f"Analyzer ID: {source_analyzer_details.analyzer_id}")
        print(f"Description: {source_analyzer_details.description}")
        print(f"Tags: {source_analyzer_details.tags}")
        print(f"=== End Source Analyzer Details ===\n")

        # Step 2: Copy the source analyzer to target using begin_copy_analyzer API
        print(f"Copying analyzer from '{source_analyzer_id}' to '{target_analyzer_id}'...")
        
        # Use begin_copy_analyzer with source_analyzer_id keyword argument
        # The body will include sourceAnalyzerId and we can add tags to the target analyzer
        # Note: Tags may need to be set via update after copy, or included in the copy body if supported
        try:
            copy_poller = await client.begin_copy_analyzer(
                analyzer_id=target_analyzer_id,
                source_analyzer_id=source_analyzer_id,
            )
            await copy_poller.result()
            print(f"Target analyzer '{target_analyzer_id}' copied successfully!")
            
            # Retrieve the full analyzer details using get_analyzer
            # Note: This is a workaround for a service bug where begin_copy_analyzer result
            # returns empty/None values. See SERVICE-BUG.md Bug #3 for details.
            print(f"\nRetrieving target analyzer details using get_analyzer...")
            target_analyzer_details = await client.get_analyzer(analyzer_id=target_analyzer_id)
            print(f"\n=== Target Analyzer Details (before update) ===")
            print(f"Analyzer ID: {target_analyzer_details.analyzer_id}")
            print(f"Description: {target_analyzer_details.description}")
            print(f"Tags: {target_analyzer_details.tags}")
            print(f"=== End Target Analyzer Details ===\n")
        except Exception as e:
            print(f"Error copying analyzer: {e}")
            print("Note: The copy operation may not be available on all service endpoints.")
            # Clean up source analyzer before raising
            print(f"\nDeleting source analyzer '{source_analyzer_id}' (cleanup after error)...")
            await client.delete_analyzer(analyzer_id=source_analyzer_id)
            print(f"Source analyzer '{source_analyzer_id}' deleted successfully!")
            raise

        # Update the target analyzer to add the "modelType": "in_production" tag
        # Since copy may not preserve or set tags, we update after copying
        print(f"Updating target analyzer '{target_analyzer_id}' with tag 'modelType': 'in_production'...")
        updated_target_analyzer = ContentAnalyzer(
            tags={"modelType": "in_production"}
        )
        await client.update_analyzer(
            analyzer_id=target_analyzer_id,
            resource=updated_target_analyzer,
        )
        print(f"Target analyzer '{target_analyzer_id}' updated successfully!")
        
        # Retrieve the updated analyzer details
        print(f"\nRetrieving updated target analyzer details...")
        final_target_analyzer_details = await client.get_analyzer(analyzer_id=target_analyzer_id)
        print(f"\n=== Target Analyzer Details (after update) ===")
        print(f"Analyzer ID: {final_target_analyzer_details.analyzer_id}")
        print(f"Description: {final_target_analyzer_details.description}")
        print(f"Tags: {final_target_analyzer_details.tags}")
        print(f"=== End Target Analyzer Details ===\n")

        # Clean up the created analyzers (demo cleanup)
        print(f"Deleting analyzers (demo cleanup)...")
        print(f"Deleting source analyzer '{source_analyzer_id}'...")
        await client.delete_analyzer(analyzer_id=source_analyzer_id)
        print(f"Source analyzer '{source_analyzer_id}' deleted successfully!")
        
        print(f"Deleting target analyzer '{target_analyzer_id}'...")
        await client.delete_analyzer(analyzer_id=target_analyzer_id)
        print(f"Target analyzer '{target_analyzer_id}' deleted successfully!")

    # Manually close DefaultAzureCredential if it was used
    if isinstance(credential, DefaultAzureCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())

