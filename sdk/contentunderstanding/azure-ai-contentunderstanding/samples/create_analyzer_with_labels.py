# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: build a custom model using training files and test it.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    CONTENT_UNDERSTANDING_STORAGE_CONTAINER_SAS_URL  (required) 
        - SAS URL to Azure Blob Storage container with training files
        - SAS token must have 'read' and 'list' permissions
        - Format: https://<storage-account>.blob.core.windows.net/<container>?<sas-token>
        - Training files: Copy the files from sdk/contentunderstanding/azure-ai-contentunderstanding/samples/sample_files/training_samples/
          into your blob storage container before running this sample
    CONTENT_UNDERSTANDING_STORAGE_PREFIX   (optional)
        - Prefix (folder path) to filter blobs within the container
        - Example: "training_data/" to only use files in that folder
        - If not set, all files in the container will be used
    CONTENT_UNDERSTANDING_FILE_LIST_PATH   (optional)
        - Path to a file listing specific blobs to include in training
        - If not set, all files in the container (or prefix) will be used
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python create_analyzer_with_labels.py
"""

from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime
from typing import cast

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    ContentFieldSchema,
    ContentFieldDefinition,
    ContentFieldType,
    GenerationMethod,
    LabeledDataKnowledgeSource,
    KnowledgeSource,
    AnalyzeResult,
)
from sample_helper import save_json_to_file
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


def create_irs_1040_schema() -> ContentFieldSchema:
    """Create a simplified IRS 1040 field schema with 5 key fields for demonstration."""
    return ContentFieldSchema(
        name="IRS_1040",
        description="Simplified IRS 1040 form schema for demonstration",
        fields={
            "FieldYourFirstNameAndMiddleInitial": ContentFieldDefinition(
                type=ContentFieldType.STRING,
                method=GenerationMethod.EXTRACT,
                description="",
            ),
            "FieldYourFirstNameAndMiddleInitialLastName": ContentFieldDefinition(
                type=ContentFieldType.STRING,
                method=GenerationMethod.EXTRACT,
                description="",
            ),
            "CheckboxYouAsADependent": ContentFieldDefinition(
                type=ContentFieldType.BOOLEAN,
                method=GenerationMethod.EXTRACT,
                description="",
            ),
            "TableDependents": ContentFieldDefinition(
                type=ContentFieldType.ARRAY,
                method=GenerationMethod.GENERATE,
                description="",
                item_definition=ContentFieldDefinition(
                    type=ContentFieldType.OBJECT,
                    method=GenerationMethod.EXTRACT,
                    description="",
                    properties={
                        "FirstNameLastName": ContentFieldDefinition(
                            type=ContentFieldType.STRING,
                            method=GenerationMethod.EXTRACT,
                            description="",
                        ),
                        "SocialSecurityNumber": ContentFieldDefinition(
                            type=ContentFieldType.STRING,
                            method=GenerationMethod.EXTRACT,
                            description="",
                        ),
                        "RelationshipToYou": ContentFieldDefinition(
                            type=ContentFieldType.STRING,
                            method=GenerationMethod.EXTRACT,
                            description="",
                        ),
                        "CheckboxChildTaxCredit": ContentFieldDefinition(
                            type=ContentFieldType.BOOLEAN,
                            method=GenerationMethod.EXTRACT,
                            description="",
                        ),
                        "CheckboxCreditForOtherDependents": ContentFieldDefinition(
                            type=ContentFieldType.BOOLEAN,
                            method=GenerationMethod.EXTRACT,
                            description="",
                        ),
                    },
                ),
            ),
            "FieldWagesSalariesTipsEtcAttachFormSW2": ContentFieldDefinition(
                type=ContentFieldType.STRING,
                method=GenerationMethod.EXTRACT,
                description="",
            ),
        },
    )


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    print(f"Using endpoint: {endpoint}\n")
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    # Get training data container URL
    container_sas_url = os.getenv("CONTENT_UNDERSTANDING_STORAGE_CONTAINER_SAS_URL")
    if not container_sas_url:
        raise ValueError(
            "CONTENT_UNDERSTANDING_STORAGE_CONTAINER_SAS_URL environment variable is required. "
            "Set it in your .env file or environment."
        )

    # Print environment variable values before training
    print("Environment Variables:")
    print("=" * 50)
    print(f"AZURE_CONTENT_UNDERSTANDING_ENDPOINT: {endpoint}")
    print(f"AZURE_CONTENT_UNDERSTANDING_KEY: {'***' if key else '(not set, using DefaultAzureCredential)'}")
    
    # Extract storage account and container from SAS URL (for security, don't print the full SAS token)
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(container_sas_url)
        storage_info = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?<sas-token>"
        print(f"CONTENT_UNDERSTANDING_STORAGE_CONTAINER_SAS_URL: {storage_info}")
    except Exception:
        # Fallback if parsing fails
        print(f"CONTENT_UNDERSTANDING_STORAGE_CONTAINER_SAS_URL: <set>")
    
    file_list_path = os.getenv("CONTENT_UNDERSTANDING_FILE_LIST_PATH", "")
    storage_prefix = os.getenv("CONTENT_UNDERSTANDING_STORAGE_PREFIX", "")
    print(f"CONTENT_UNDERSTANDING_FILE_LIST_PATH: {file_list_path if file_list_path else '(not set, using all files)'}")
    print(f"CONTENT_UNDERSTANDING_STORAGE_PREFIX: {storage_prefix if storage_prefix else '(not set, using all files in container)'}")
    print("=" * 50)

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        # Define the IRS 1040 field schema
        print("Defining IRS 1040 field schema...")
        field_schema = create_irs_1040_schema()

        # Create analyzer ID
        analyzer_id = f"irs_1040_custom_model_{int(asyncio.get_event_loop().time())}"

        # Build analyzer with training data
        description = "Custom IRS 1040 form analyzer built with training files"
        print(f"\nCreating analyzer '{analyzer_id}' {description}...")

        knowledge_sources: list[LabeledDataKnowledgeSource] | None = None
        if container_sas_url:
            file_list_path = os.getenv("CONTENT_UNDERSTANDING_FILE_LIST_PATH", "")
            storage_prefix = os.getenv("CONTENT_UNDERSTANDING_STORAGE_PREFIX", "")
            
            # Build kwargs dynamically - only include non-empty optional parameters
            lds_kwargs = {"container_url": container_sas_url}
            if file_list_path:
                lds_kwargs["file_list_path"] = file_list_path
            if storage_prefix:
                lds_kwargs["prefix"] = storage_prefix
            
            knowledge_sources = [LabeledDataKnowledgeSource(**lds_kwargs)]

        custom_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description=description,
            config=ContentAnalyzerConfig(
                return_details=True,
                enable_layout=True,
                enable_formula=False,
                estimate_field_source_and_confidence=True,
            ),
            field_schema=field_schema,
            knowledge_sources=cast(list[KnowledgeSource] | None, knowledge_sources) if knowledge_sources else None,
            models={"completion": "gpt-4.1", "embedding": "text-embedding-ada-002"},  # Required when using field_schema
        )

        poller = await client.begin_create_analyzer(
            analyzer_id=analyzer_id,
            resource=custom_analyzer,
        )

        print("Waiting for analyzer creation to complete...")
        result = await poller.result()
        print(f"Analyzer '{analyzer_id}' created successfully!")
        print(f"Status: {result.status}")
        print(f"Created at: {result.created_at}")

        if result.warnings:
            print("Warnings encountered while building the analyzer:")
            for warning in result.warnings:
                print(f"  - {warning}")

        # Test the analyzer
        test_file_path = os.path.join(
            os.path.dirname(__file__),
            "sample_files",
            "IRS_1040_test.pdf",
        )
        print(f"\nTesting analyzer with {test_file_path}...")
        with open(test_file_path, "rb") as f:
            pdf_bytes = f.read()

        analyze_poller = await client.begin_analyze_binary(
            analyzer_id=analyzer_id,
            binary_input=pdf_bytes,
            content_type="application/pdf",
        )
        analyze_result = await analyze_poller.result()
        print("Analysis completed successfully!")

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(os.path.dirname(__file__), "sample_output")
        os.makedirs(output_dir, exist_ok=True)

        result_file = os.path.join(output_dir, f"build_custom_model_test_result_{timestamp}.json")
        with open(result_file, "w") as f:
            json.dump(analyze_result.as_dict(), f, indent=2, default=str)
        print(f"Analysis result saved to: {result_file}")
        print("Analysis result saved to JSON file for detailed inspection")

        # Cleanup
        print(f"\nDeleting analyzer '{analyzer_id}' (demo cleanup)...")
        await client.delete_analyzer(analyzer_id=analyzer_id)
        print(f"Analyzer '{analyzer_id}' deleted successfully!")

    # Close DefaultAzureCredential if used
    if isinstance(credential, DefaultAzureCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
