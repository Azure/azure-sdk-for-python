# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: retrieve an analyzer using the get API.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # or set AZURE_CONTENT_UNDERSTANDING_KEY

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - falls back to DefaultAzureCredential)

Run:
    python content_analyzers_get_analyzer.py
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
from sample_helper import get_credential, save_response_to_file

load_dotenv()


# ---------------------------------------------------------------------------
# Sample: Retrieve analyzer using get API
# ---------------------------------------------------------------------------
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Create a custom analyzer (for retrieval demo)
# 3. Retrieve the analyzer using the get API
# 4. Save the analyzer definition to a JSON file
# 5. Clean up by deleting the analyzer (demo purposes)

async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    credential = get_credential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client, credential:
        analyzer_id = f"sdk-sample-analyzer-to-retrieve-{int(asyncio.get_event_loop().time())}"
        
        # First, create an analyzer to retrieve (for demo purposes)
        print(f"🔧 Creating analyzer '{analyzer_id}' for retrieval demo...")
        custom_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-documentAnalyzer",
            description="Custom analyzer for retrieval demo",
            config=ContentAnalyzerConfig(return_details=True),
            field_schema=FieldSchema(
                name="retrieval_schema",
                description="Schema for retrieval demo",
                fields={
                    "demo_field": FieldDefinition(
                        type=FieldType.STRING,
                        method=GenerationMethod.EXTRACT,
                        description="Demo field for retrieval",
                    ),
                },
            ),
        )
        
        poller = await client.content_analyzers.begin_create_or_replace(
            analyzer_id=analyzer_id,
            resource=custom_analyzer,
        )
        await poller.result()
        print(f"✅ Analyzer '{analyzer_id}' created successfully!")
        
        # Now retrieve the analyzer
        print(f"📋 Retrieving analyzer '{analyzer_id}'...")
        retrieved_analyzer = await client.content_analyzers.get(analyzer_id=analyzer_id)
        print(f"✅ Analyzer '{analyzer_id}' retrieved successfully!")
        print(f"   Description: {retrieved_analyzer.description}")
        print(f"   Status: {retrieved_analyzer.status}")
        print(f"   Created at: {retrieved_analyzer.created_at}")
        
        save_response_to_file(retrieved_analyzer, filename_prefix="content_analyzers_get_analyzer")
        
        # Clean up: delete the analyzer (demo purposes only)
        # Note: You can leave the analyzer for later use if desired
        print(f"🗑️  Deleting analyzer '{analyzer_id}' (demo cleanup)...")
        await client.content_analyzers.delete(analyzer_id=analyzer_id)
        print(f"✅ Analyzer '{analyzer_id}' deleted successfully!")


if __name__ == "__main__":
    asyncio.run(main())
