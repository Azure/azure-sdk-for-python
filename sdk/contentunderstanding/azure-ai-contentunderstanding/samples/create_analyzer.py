# pylint: disable=line-too-long,useless-suppression

# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: create a custom analyzer using begin_create_analyzer API.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python create_analyzer.py
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
# Sample: Create custom analyzer using begin_create_analyzer API
# ---------------------------------------------------------------------------
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Create a custom analyzer with field schema using object model
# 3. Wait for analyzer creation to complete
# 4. Save the analyzer definition to a JSON file


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    print(f"Using endpoint: {endpoint}")
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        analyzer_id = f"sdk_sample_custom_analyzer_{int(asyncio.get_event_loop().time())}"

        # Create a custom analyzer using object model
        custom_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Custom analyzer for extracting company information",
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
                    ),
                    # CLASSIFY: Categorize the document or content
                    "document_category": ContentFieldDefinition(
                        type=ContentFieldType.STRING,
                        method=GenerationMethod.CLASSIFY,
                        description="Category of the document",
                        enum=["invoice", "contract", "receipt", "report", "other"],
                    ),
                    "urgency_level": ContentFieldDefinition(
                        type=ContentFieldType.STRING,
                        method=GenerationMethod.CLASSIFY,
                        description="Urgency level of the document",
                        enum=["high", "medium", "low"],
                    ),
                },
            ),
            models={"completion": "gpt-4o"},  # Required when using field_schema
        )

        print(f"Creating custom analyzer '{analyzer_id}'...")
        poller = await client.begin_create_analyzer(
            analyzer_id=analyzer_id,
            resource=custom_analyzer,
        )
        result = await poller.result()
        print(f"Analyzer '{analyzer_id}' created successfully!")

        # Clean up the created analyzer (demo cleanup)
        print(f"Deleting analyzer '{analyzer_id}' (demo cleanup)...")
        await client.delete_analyzer(analyzer_id=analyzer_id)
        print(f"Analyzer '{analyzer_id}' deleted successfully!")

        # Next steps:
        # - To retrieve the analyzer: see get_analyzer.py
        # - To use the analyzer for analysis: see analyze_binary.py
        # - To delete the analyzer: see delete_analyzer.py

    # Manually close DefaultAzureCredential if it was used
    if isinstance(credential, DefaultAzureCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
