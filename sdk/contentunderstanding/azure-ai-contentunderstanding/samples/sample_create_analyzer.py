# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_create_analyzer.py

DESCRIPTION:
    This sample demonstrates how to create a custom analyzer with a field schema to extract
    structured data from documents.

    Custom analyzers allow you to:
    - Define custom fields (string, number, date, object, array)
    - Specify extraction methods:
      - extract: Values are extracted as they appear in the content (literal text extraction)
      - generate: Values are generated freely based on the content using AI models
      - classify: Values are classified against a predefined set of categories
    - Use prebuilt analyzers as a base (prebuilt-document, prebuilt-audio, prebuilt-video, prebuilt-image)
    - Configure analysis options (OCR, layout, formulas)
    - Enable source and confidence tracking for extracted field values

USAGE:
    python sample_create_analyzer.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).

    Before using custom analyzers, you MUST configure model deployments for your Microsoft Foundry
    resource. See sample_update_defaults.py for setup instructions.
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
            ),
            "total_amount": ContentFieldDefinition(
                type=ContentFieldType.NUMBER,
                method=GenerationMethod.EXTRACT,
                description="Total amount on the document",
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
        models={"completion": "gpt-4.1"},  # Required when using field_schema
    )

    # Create the analyzer
    poller = client.begin_create_analyzer(
        analyzer_id=analyzer_id,
        resource=analyzer,
    )
    result = poller.result()  # Wait for creation to complete

    # Get the full analyzer details after creation
    result = client.get_analyzer(analyzer_id=analyzer_id)

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
    client.delete_analyzer(analyzer_id=analyzer_id)
    print(f"Analyzer '{analyzer_id}' deleted successfully.")


if __name__ == "__main__":
    main()
