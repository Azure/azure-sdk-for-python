# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: delete a custom analyzer using the delete API.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # or set AZURE_CONTENT_UNDERSTANDING_KEY

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - falls back to DefaultAzureCredential)

Run:
    python content_analyzers_delete_analyzer.py
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
# Sample: Delete custom analyzer using delete API
# ---------------------------------------------------------------------------
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Create a custom analyzer (for deletion demo)
# 3. Delete the analyzer using the delete API
# 4. Verify the analyzer is no longer available

async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    credential = get_credential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client, credential:
        analyzer_id = f"sdk-sample-analyzer-to-delete-{int(asyncio.get_event_loop().time())}"
        
        # First, create an analyzer to delete (for demo purposes)
        print(f"🔧 Creating analyzer '{analyzer_id}' for deletion demo...")
        custom_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-documentAnalyzer",
            description="Temporary analyzer for deletion demo",
            config=ContentAnalyzerConfig(return_details=True),
            field_schema=FieldSchema(
                name="demo_schema",
                description="Schema for deletion demo",
                fields={
                    "demo_field": FieldDefinition(
                        type=FieldType.STRING,
                        method=GenerationMethod.EXTRACT,
                        description="Demo field for deletion",
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
        
        # Now delete the analyzer
        print(f"🗑️  Deleting analyzer '{analyzer_id}'...")
        await client.content_analyzers.delete(analyzer_id=analyzer_id)
        print(f"✅ Analyzer '{analyzer_id}' deleted successfully!")


if __name__ == "__main__":
    asyncio.run(main())
