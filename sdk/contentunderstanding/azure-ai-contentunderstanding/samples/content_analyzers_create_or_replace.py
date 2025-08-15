# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: create a custom analyzer using begin_create_or_replace API.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python content_analyzers_create_or_replace.py
"""

from __future__ import annotations

import asyncio
import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer,
    ContentAnalyzerConfig,
    FieldSchema,
    FieldDefinition,
    FieldType,
    GenerationMethod,
)
from sample_helper import get_credential

load_dotenv()


# ---------------------------------------------------------------------------
# Sample: Create custom analyzer using begin_create_or_replace API
# ---------------------------------------------------------------------------
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Create a custom analyzer with field schema using object model
# 3. Wait for analyzer creation to complete
# 4. Save the analyzer definition to a JSON file

async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    credential = get_credential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client, credential:
        analyzer_id = f"sdk-sample-custom-analyzer-{int(asyncio.get_event_loop().time())}"
        
        # Create a custom analyzer using object model
        custom_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-documentAnalyzer",
            description="Custom analyzer for extracting company information",
            config=ContentAnalyzerConfig(
                enable_formula=True,
                enable_layout=True,
                enable_ocr=True,
                estimate_field_source_and_confidence=True,
                return_details=True,
            ),
            field_schema=FieldSchema(
                name="company_schema",
                description="Schema for extracting company information",
                fields={
                    "company_name": FieldDefinition(
                        type=FieldType.STRING,
                        method=GenerationMethod.EXTRACT,
                        description="Name of the company",
                    ),
                    "total_amount": FieldDefinition(
                        type=FieldType.NUMBER,
                        method=GenerationMethod.EXTRACT,
                        description="Total amount on the document",
                    ),
                },
            ),
        )

        print(f"🔧 Creating custom analyzer '{analyzer_id}'...")
        poller = await client.content_analyzers.begin_create_or_replace(
            analyzer_id=analyzer_id,
            resource=custom_analyzer,
        )
        result = await poller.result()
        print(f"✅ Analyzer '{analyzer_id}' created successfully!")
        
        # Clean up the created analyzer (demo cleanup)
        print(f"🗑️  Deleting analyzer '{analyzer_id}' (demo cleanup)...")
        await client.content_analyzers.delete(analyzer_id=analyzer_id)
        print(f"✅ Analyzer '{analyzer_id}' deleted successfully!")
        
        # Next steps:
        # - To retrieve the analyzer: see content_analyzers_get_analyzer.py
        # - To use the analyzer for analysis: see content_analyzers_analyze_binary.py
        # - To delete the analyzer: see content_analyzers_delete_analyzer.py


if __name__ == "__main__":
    asyncio.run(main())
