# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_create_analyzer_async.py

DESCRIPTION:
    This sample demonstrates how to create a custom analyzer with a field schema to extract
    structured data from documents. While this sample shows document modalities, custom analyzers
    can also be created for video, audio, and image content. The same concepts apply across all
    modalities.

    ## About custom analyzers

    Custom analyzers allow you to define a field schema that specifies what structured data to
    extract from documents. You can:
    - Define custom fields (string, number, date, object, array)
    - Specify extraction methods to control how field values are extracted:
      - generate - Values are generated freely based on the content using AI models (best for
        complex or variable fields requiring interpretation)
      - classify - Values are classified against a predefined set of categories (best when using
        enum with a fixed set of possible values)
      - extract - Values are extracted as they appear in the content (best for literal text
        extraction from specific locations). Note: This method is only available for document
        content. Requires estimateSourceAndConfidence to be set to true for the field.

      When not specified, the system automatically determines the best method based on the field
      type and description.
    - Use prebuilt analyzers as a base. Supported base analyzers include:
      - prebuilt-document - for document-based custom analyzers
      - prebuilt-audio - for audio-based custom analyzers
      - prebuilt-video - for video-based custom analyzers
      - prebuilt-image - for image-based custom analyzers
    - Configure analysis options (OCR, layout, formulas)
    - Enable source and confidence tracking: Set estimateFieldSourceAndConfidence to true at the
      analyzer level (in ContentAnalyzerConfig) or estimateSourceAndConfidence to true at the field
      level to get source location (page number, bounding box) and confidence scores for extracted
      field values. This is required for fields with method = extract and is useful for validation,
      quality assurance, debugging, and highlighting source text in user interfaces. Field-level
      settings override analyzer-level settings.

USAGE:
    python sample_create_analyzer_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using custom analyzers, you MUST configure model deployments for your Microsoft Foundry
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
    ContentFieldSchema,
    ContentFieldDefinition,
    ContentFieldType,
    GenerationMethod,
)
from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        # [START create_analyzer]
        # Generate a unique analyzer ID
        analyzer_id = f"my_custom_analyzer_{int(time.time())}"

        print(f"Creating custom analyzer '{analyzer_id}'...")

        # Define field schema with custom fields
        # This example demonstrates three extraction methods:
        # - extract: Literal text extraction (requires estimateSourceAndConfidence)
        # - generate: AI-generated values based on content interpretation
        # - classify: Classification against predefined categories
        field_schema = ContentFieldSchema(
            name="company_schema",
            description="Schema for extracting company information",
            fields={
                "company_name": ContentFieldDefinition(
                    type=ContentFieldType.STRING,
                    method=GenerationMethod.EXTRACT,
                    description="Name of the company",
                    estimate_source_and_confidence=True,
                ),
                "total_amount": ContentFieldDefinition(
                    type=ContentFieldType.NUMBER,
                    method=GenerationMethod.EXTRACT,
                    description="Total amount on the document",
                    estimate_source_and_confidence=True,
                ),
                "document_summary": ContentFieldDefinition(
                    type=ContentFieldType.STRING,
                    method=GenerationMethod.GENERATE,
                    description="A brief summary of the document content",
                ),
                "document_type": ContentFieldDefinition(
                    type=ContentFieldType.STRING,
                    method=GenerationMethod.CLASSIFY,
                    description="Type of document",
                    enum=["invoice", "receipt", "contract", "report", "other"],
                ),
            },
        )

        # Create analyzer configuration
        config = ContentAnalyzerConfig(
            enable_formula=True,
            enable_layout=True,
            enable_ocr=True,
            estimate_field_source_and_confidence=True,
            return_details=True,
        )

        # Create the analyzer with field schema
        analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Custom analyzer for extracting company information",
            config=config,
            field_schema=field_schema,
            models={
                "completion": "gpt-4.1",
                "embedding": "text-embedding-3-large",
            },  # Required when using field_schema
        )

        # Create the analyzer
        poller = await client.begin_create_analyzer(
            analyzer_id=analyzer_id,
            resource=analyzer,
        )
        result = await poller.result()  # Wait for creation to complete

        # Get the full analyzer details after creation
        result = await client.get_analyzer(analyzer_id=analyzer_id)

        print(f"Analyzer '{analyzer_id}' created successfully!")
        if result.description:
            print(f"  Description: {result.description}")

        if result.field_schema and result.field_schema.fields:
            print(f"  Fields ({len(result.field_schema.fields)}):")
            for field_name, field_def in result.field_schema.fields.items():
                method = field_def.method if field_def.method else "auto"
                field_type = field_def.type if field_def.type else "unknown"
                print(f"    - {field_name}: {field_type} ({method})")
        # [END create_analyzer]

        # Clean up - delete the analyzer
        print(f"\nCleaning up: deleting analyzer '{analyzer_id}'...")
        await client.delete_analyzer(analyzer_id=analyzer_id)
        print(f"Analyzer '{analyzer_id}' deleted successfully.")

    if not isinstance(credential, AzureKeyCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
