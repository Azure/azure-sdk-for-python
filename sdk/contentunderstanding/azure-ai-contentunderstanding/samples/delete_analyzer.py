# pylint: disable=line-too-long,useless-suppression

# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: delete a custom analyzer using the delete API.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python delete_analyzer.py
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
# Sample: Delete custom analyzer using delete API
# ---------------------------------------------------------------------------
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Create a custom analyzer (for deletion demo)
# 3. Delete the analyzer using the delete API
# 4. Verify the analyzer is no longer available


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    print(f"Using endpoint: {endpoint}")
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        analyzer_id = f"sdk_sample_analyzer_to_delete_{int(asyncio.get_event_loop().time())}"

        # First, create an analyzer to delete (for demo purposes)
        print(f"Creating analyzer '{analyzer_id}' for deletion demo...")
        custom_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Temporary analyzer for deletion demo",
            config=ContentAnalyzerConfig(return_details=True),
            field_schema=ContentFieldSchema(
                name="demo_schema",
                description="Schema for deletion demo",
                fields={
                    "demo_field": ContentFieldDefinition(
                        type=ContentFieldType.STRING,
                        method=GenerationMethod.EXTRACT,
                        description="Demo field for deletion",
                    ),
                },
            ),
            models={"completion": "gpt-4.1"},  # Required when using field_schema
        )

        poller = await client.begin_create_analyzer(
            analyzer_id=analyzer_id,
            resource=custom_analyzer,
        )
        await poller.result()
        print(f"Analyzer '{analyzer_id}' created successfully!")

        # Now delete the analyzer
        print(f"Deleting analyzer '{analyzer_id}'...")
        await client.delete_analyzer(analyzer_id=analyzer_id)
        print(f"Analyzer '{analyzer_id}' deleted successfully!")

    # Manually close DefaultAzureCredential if it was used
    if isinstance(credential, DefaultAzureCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
