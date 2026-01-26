# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_get_analyzer_async.py

DESCRIPTION:
    This sample demonstrates how to retrieve information about analyzers, including prebuilt
    analyzers and custom analyzers.

    ## About getting analyzer information

    The get_analyzer method allows you to retrieve detailed information about any analyzer,
    including:
    - Prebuilt analyzers: System-provided analyzers like prebuilt-documentSearch, prebuilt-invoice,
      etc.
    - Custom analyzers: Analyzers you've created with custom field schemas or classifiers

    This is useful for:
    - Verifying analyzer configuration: Check the current state of an analyzer
    - Inspecting prebuilt analyzers: Learn about available prebuilt analyzers and their capabilities
    - Debugging: Understand why an analyzer behaves a certain way

USAGE:
    python sample_get_analyzer_async.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).
"""

import asyncio
import json
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
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        # [START get_prebuilt_analyzer]
        print("Retrieving prebuilt-documentSearch analyzer...")
        analyzer = await client.get_analyzer(analyzer_id="prebuilt-documentSearch")

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

        # [START get_prebuilt_invoice]
        print("\nRetrieving prebuilt-invoice analyzer...")
        invoice_analyzer = await client.get_analyzer(analyzer_id="prebuilt-invoice")

        # Display full analyzer JSON for prebuilt-invoice
        print("\n" + "=" * 80)
        print("Prebuilt-invoice Analyzer (Raw JSON):")
        print("=" * 80)
        invoice_json = json.dumps(invoice_analyzer.as_dict(), indent=2, default=str)
        print(invoice_json)
        print("=" * 80)
        # [END get_prebuilt_invoice]

        # [START get_custom_analyzer]
        # First, create a custom analyzer
        analyzer_id = f"my_custom_analyzer_{int(time.time())}"

        print(f"\nCreating custom analyzer '{analyzer_id}'...")

        # Define field schema with custom fields
        field_schema = ContentFieldSchema(
            name="test_schema",
            description="Test schema for GetAnalyzer sample",
            fields={
                "company_name": ContentFieldDefinition(
                    type=ContentFieldType.STRING,
                    method=GenerationMethod.EXTRACT,
                    description="Name of the company",
                ),
            },
        )

        # Create analyzer configuration
        config = ContentAnalyzerConfig(
            return_details=True
        )

        # Create the custom analyzer
        custom_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Test analyzer for GetAnalyzer sample",
            config=config,
            field_schema=field_schema,
            models={"completion": "gpt-4.1"},
        )

        # Create the analyzer
        poller = await client.begin_create_analyzer(
            analyzer_id=analyzer_id,
            resource=custom_analyzer,
        )
        await poller.result()
        print(f"Custom analyzer '{analyzer_id}' created successfully!")

        try:
            # Get information about the custom analyzer
            retrieved_analyzer = await client.get_analyzer(analyzer_id=analyzer_id)

            # Get raw response JSON and format it for nice printing
            # Display full analyzer JSON
            print("\n" + "=" * 80)
            print(f"Custom Analyzer '{analyzer_id}':")
            print("=" * 80)
            retrieved_json = json.dumps(retrieved_analyzer.as_dict(), indent=2, default=str)
            print(retrieved_json)
            print("=" * 80)
        finally:
            # Clean up - delete the analyzer
            print(f"\nCleaning up: deleting analyzer '{analyzer_id}'...")
            await client.delete_analyzer(analyzer_id=analyzer_id)
            print(f"Analyzer '{analyzer_id}' deleted successfully.")
        # [END get_custom_analyzer]

    if not isinstance(credential, AzureKeyCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
