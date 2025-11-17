# pylint: disable=line-too-long,useless-suppression

# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: retrieve an analyzer using the get API.

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python get_analyzer.py
"""

from __future__ import annotations
import asyncio
import json
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
# Sample: Retrieve analyzer using get API
# ---------------------------------------------------------------------------
# This sample demonstrates:
# 1. Authenticate with Azure AI Content Understanding
# 2. Retrieve a prebuilt analyzer and dump it as JSON
# 3. Create a custom analyzer
# 4. Retrieve the custom analyzer using the get API
# 5. Display analyzer details and dump as JSON
# 6. Clean up by deleting the analyzer (demo purposes)


async def main() -> None:
    endpoint = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    print(f"Using endpoint: {endpoint}")
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        # First, retrieve and dump the prebuilt-document analyzer
        print("Retrieving prebuilt-document analyzer...")
        prebuilt_analyzer: ContentAnalyzer = await client.get_analyzer(analyzer_id="prebuilt-documentSearch")
        print("Prebuilt-document analyzer retrieved successfully!")

        # Dump prebuilt analyzer as JSON
        print("\n" + "=" * 80)
        print("Dump ContentAnalyzer object for prebuilt-document")
        print("=" * 80)
        prebuilt_json = json.dumps(prebuilt_analyzer.as_dict(), indent=2, default=str)
        print(prebuilt_json)
        print("=" * 80 + "\n")

        # Now create a custom analyzer for piano student registration form processing
        analyzer_id = f"piano_student_registration_{int(asyncio.get_event_loop().time())}"
        print(f"Creating custom analyzer '{analyzer_id}' for piano student registration form processing...")
        custom_analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Custom analyzer for processing piano student registration forms",
            config=ContentAnalyzerConfig(return_details=True),
            field_schema=ContentFieldSchema(
                name="piano_student_registration_schema",
                description="Schema for extracting and analyzing piano student registration form data",
                fields={
                    "student_name": ContentFieldDefinition(
                        type=ContentFieldType.STRING,
                        method=GenerationMethod.EXTRACT,
                        description="The full name of the student registering for piano lessons",
                    ),
                    "years_of_playing": ContentFieldDefinition(
                        type=ContentFieldType.STRING,
                        method=GenerationMethod.GENERATE,
                        description="Number of years the student has been playing piano, inferred from experience level or dates mentioned",
                    ),
                    "learning_goals_summary": ContentFieldDefinition(
                        type=ContentFieldType.STRING,
                        method=GenerationMethod.GENERATE,
                        description="A concise summary of the student's learning goals and musical aspirations",
                    ),
                },
            ),
            models={"completion": "gpt-4o"},  # Required when using field_schema
        )

        poller = await client.begin_create_analyzer(
            analyzer_id=analyzer_id,
            resource=custom_analyzer,
        )
        await poller.result()
        print(f"Custom analyzer '{analyzer_id}' created successfully!")

        # Now retrieve the custom analyzer
        print(f"\nRetrieving custom analyzer '{analyzer_id}'...")
        retrieved_analyzer: ContentAnalyzer = await client.get_analyzer(analyzer_id=analyzer_id)
        print(f"Custom analyzer '{analyzer_id}' retrieved successfully!")
        print(f"   Description: {retrieved_analyzer.description}")
        print(f"   Status: {retrieved_analyzer.status}")
        print(f"   Created at: {retrieved_analyzer.created_at}")

        # Dump custom analyzer as JSON
        print("\n" + "=" * 80)
        print(f"Dump ContentAnalyzer object for {analyzer_id}")
        print("=" * 80)
        custom_json = json.dumps(retrieved_analyzer.as_dict(), indent=2, default=str)
        print(custom_json)
        print("=" * 80 + "\n")

        # Clean up: delete the analyzer (demo purposes only)
        # Note: You can leave the analyzer for later use if desired
        print(f"Deleting analyzer '{analyzer_id}' (demo cleanup)...")
        await client.delete_analyzer(analyzer_id=analyzer_id)
        print(f"Analyzer '{analyzer_id}' deleted successfully!")

    # Manually close DefaultAzureCredential if it was used
    if isinstance(credential, DefaultAzureCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
