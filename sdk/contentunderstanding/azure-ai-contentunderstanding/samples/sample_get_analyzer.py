# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_get_analyzer.py

DESCRIPTION:
    This sample demonstrates how to retrieve information about analyzers, including prebuilt
    analyzers and custom analyzers.

    The get_analyzer method allows you to retrieve detailed information about any analyzer:
    - Prebuilt analyzers: System-provided analyzers like prebuilt-documentSearch, prebuilt-invoice
    - Custom analyzers: Analyzers you've created with custom field schemas or classifiers

    This is useful for:
    - Verifying analyzer configuration
    - Inspecting prebuilt analyzers to learn about their capabilities
    - Debugging analyzer behavior

USAGE:
    python sample_get_analyzer.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).
"""

import json
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

    # [START get_prebuilt_analyzer]
    print("Retrieving prebuilt-documentSearch analyzer...")
    analyzer = client.get_analyzer(analyzer_id="prebuilt-documentSearch")

    # Print a few properties from the analyzer
    print(f"Analyzer ID: {analyzer.analyzer_id}")
    print(f"Base Analyzer ID: {analyzer.base_analyzer_id}")
    print(f"Description: {analyzer.description}")
    if analyzer.config:
        print(f"Enable OCR: {analyzer.config.enable_ocr}")
        print(f"Enable Layout: {analyzer.config.enable_layout}")
    if analyzer.models:
        models_str = ", ".join(f"{k}={v}" for k, v in analyzer.models.items())
        print(f"Models: {models_str}")

    # Display full analyzer JSON
    print("\n" + "=" * 80)
    print("Prebuilt-documentSearch Analyzer (Raw JSON):")
    print("=" * 80)
    analyzer_json = json.dumps(analyzer.as_dict(), indent=2, default=str)
    print(analyzer_json)
    print("=" * 80)
    # [END get_prebuilt_analyzer]

    # [START get_custom_analyzer]
    # First, create a custom analyzer
    analyzer_id = f"my_custom_analyzer_{int(time.time())}"

    print(f"\nCreating custom analyzer '{analyzer_id}'...")

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
        },
    )

    custom_analyzer = ContentAnalyzer(
        base_analyzer_id="prebuilt-document",
        description="Custom analyzer for extracting company information",
        config=ContentAnalyzerConfig(return_details=True),
        field_schema=field_schema,
        models={"completion": "gpt-4.1"},
    )

    poller = client.begin_create_analyzer(
        analyzer_id=analyzer_id,
        resource=custom_analyzer,
    )
    poller.result()
    print(f"Custom analyzer '{analyzer_id}' created successfully!")

    # Now retrieve the custom analyzer
    print(f"\nRetrieving custom analyzer '{analyzer_id}'...")
    retrieved_analyzer = client.get_analyzer(analyzer_id=analyzer_id)

    # Display full analyzer JSON
    print("\n" + "=" * 80)
    print(f"Custom Analyzer '{analyzer_id}':")
    print("=" * 80)
    retrieved_json = json.dumps(retrieved_analyzer.as_dict(), indent=2, default=str)
    print(retrieved_json)
    print("=" * 80)

    # Clean up - delete the analyzer
    print(f"\nCleaning up: deleting analyzer '{analyzer_id}'...")
    client.delete_analyzer(analyzer_id=analyzer_id)
    print(f"Analyzer '{analyzer_id}' deleted successfully.")
    # [END get_custom_analyzer]


if __name__ == "__main__":
    main()
