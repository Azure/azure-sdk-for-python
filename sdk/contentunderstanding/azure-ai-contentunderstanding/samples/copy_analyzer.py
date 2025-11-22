# pylint: disable=line-too-long,useless-suppression

# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: copy an analyzer from dev to prod using begin_copy_analyzer API.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python copy_analyzer_to_prod.py
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
# Sample: Copy analyzer from dev to prod using begin_copy_analyzer API
# ---------------------------------------------------------------------------
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Create a dev analyzer with "-dev" postfix and tag "modelType": "dev"
# 3. Copy the dev analyzer to prod with "-prod" postfix and tag "modelType": "prod"
# 4. Wait for copy operation to complete
# 5. Clean up both analyzers


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    print(f"Using endpoint: {endpoint}")
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        base_analyzer_id = f"sdk_sample_custom_analyzer_{int(asyncio.get_event_loop().time())}"
        dev_analyzer_id = f"{base_analyzer_id}_dev"
        prod_analyzer_id = f"{base_analyzer_id}_prod"

        # Step 1: Create the dev analyzer with "-dev" postfix and tag "modelType": "dev"
        print(f"Creating dev analyzer '{dev_analyzer_id}' with tag 'modelType': 'dev'...")
        
        # Create a custom analyzer using object model (following pattern from create_analyzer.py)
        dev_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Development analyzer for extracting company information",
            tags={"modelType": "dev"},
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
            models={"completion": "gpt-4o"},  # Required when using field_schema
        )

        poller = await client.begin_create_analyzer(
            analyzer_id=dev_analyzer_id,
            resource=dev_analyzer,
        )
        dev_result = await poller.result()
        print(f"Dev analyzer '{dev_analyzer_id}' created successfully!")
        print(f"Dev analyzer tags: {dev_result.tags}")

        # Step 2: Copy the dev analyzer to prod using begin_copy_analyzer API
        print(f"\nCopying analyzer from '{dev_analyzer_id}' to '{prod_analyzer_id}' with tag 'modelType': 'prod'...")
        
        # Use begin_copy_analyzer with source_analyzer_id keyword argument
        # The body will include sourceAnalyzerId and we can add tags to the target analyzer
        # Note: Tags may need to be set via update after copy, or included in the copy body if supported
        try:
            copy_poller = await client.begin_copy_analyzer(
                analyzer_id=prod_analyzer_id,
                source_analyzer_id=dev_analyzer_id,
            )
            prod_result = await copy_poller.result()
            print(f"Prod analyzer '{prod_analyzer_id}' copied successfully!")
            print(f"Prod analyzer tags (before update): {prod_result.tags}")
        except Exception as e:
            print(f"Error copying analyzer: {e}")
            print("Note: The copy operation may not be available on all service endpoints.")
            # Clean up dev analyzer before raising
            print(f"\nDeleting dev analyzer '{dev_analyzer_id}' (cleanup after error)...")
            await client.delete_analyzer(analyzer_id=dev_analyzer_id)
            print(f"Dev analyzer '{dev_analyzer_id}' deleted successfully!")
            raise

        # Update the prod analyzer to add the "modelType": "prod" tag
        # Since copy may not preserve or set tags, we update after copying
        print(f"\nUpdating prod analyzer '{prod_analyzer_id}' with tag 'modelType': 'prod'...")
        updated_prod_analyzer = ContentAnalyzer(
            tags={"modelType": "prod"}
        )
        final_prod_result = await client.update_analyzer(
            analyzer_id=prod_analyzer_id,
            resource=updated_prod_analyzer,
        )
        print(f"Prod analyzer '{prod_analyzer_id}' updated successfully!")
        print(f"Prod analyzer tags: {final_prod_result.tags}")

        # Clean up the created analyzers (demo cleanup)
        print(f"\nDeleting analyzers (demo cleanup)...")
        print(f"Deleting dev analyzer '{dev_analyzer_id}'...")
        await client.delete_analyzer(analyzer_id=dev_analyzer_id)
        print(f"Dev analyzer '{dev_analyzer_id}' deleted successfully!")
        
        print(f"Deleting prod analyzer '{prod_analyzer_id}'...")
        await client.delete_analyzer(analyzer_id=prod_analyzer_id)
        print(f"Prod analyzer '{prod_analyzer_id}' deleted successfully!")

    # Manually close DefaultAzureCredential if it was used
    if isinstance(credential, DefaultAzureCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())

