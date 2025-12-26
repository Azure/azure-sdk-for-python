# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_update_analyzer_async.py

DESCRIPTION:
    This sample demonstrates how to update an existing custom analyzer, including updating
    its description and tags.

    The update_analyzer method allows you to modify certain properties of an existing analyzer:
    - Description: Update the analyzer's description
    - Tags: Add, update, or remove tags (set tag value to empty string to remove)

    Note: Not all analyzer properties can be updated. Field schemas, models, and configuration
    typically cannot be changed after creation. To change these, you may need to delete and
    recreate the analyzer.

USAGE:
    python sample_update_analyzer_async.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_CONTENT_UNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) AZURE_CONTENT_UNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).
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
        # Create initial analyzer
        analyzer_id = f"my_analyzer_for_update_{int(time.time())}"

        print(f"Creating initial analyzer '{analyzer_id}'...")

        analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Initial description",
            config=ContentAnalyzerConfig(return_details=True),
            field_schema=ContentFieldSchema(
                name="demo_schema",
                description="Schema for update demo",
                fields={
                    "company_name": ContentFieldDefinition(
                        type=ContentFieldType.STRING,
                        method=GenerationMethod.EXTRACT,
                        description="Name of the company",
                    ),
                },
            ),
            models={"completion": "gpt-4.1"},
            tags={"tag1": "tag1_initial_value", "tag2": "tag2_initial_value"},
        )

        poller = await client.begin_create_analyzer(
            analyzer_id=analyzer_id,
            resource=analyzer,
        )
        await poller.result()
        print(f"Analyzer '{analyzer_id}' created successfully!")

        # [START update_analyzer]
        # First, get the current analyzer to preserve base analyzer ID
        current_analyzer = await client.get_analyzer(analyzer_id=analyzer_id)

        # Display current analyzer information
        print("\nCurrent analyzer information:")
        print(f"  Description: {current_analyzer.description}")
        if current_analyzer.tags:
            tags_str = ", ".join(f"{k}={v}" for k, v in current_analyzer.tags.items())
            print(f"  Tags: {tags_str}")

        # Create an updated analyzer with new description and tags
        updated_analyzer = ContentAnalyzer(
            base_analyzer_id=current_analyzer.base_analyzer_id,
            description="Updated description",
            tags={
                "tag1": "tag1_updated_value",  # Update existing tag
                "tag2": "",  # Remove tag2 (empty string removes the tag)
                "tag3": "tag3_value",  # Add new tag
            },
        )

        # Update the analyzer
        print(f"\nUpdating analyzer '{analyzer_id}'...")
        await client.update_analyzer(analyzer_id=analyzer_id, resource=updated_analyzer)

        # Verify the update
        updated = await client.get_analyzer(analyzer_id=analyzer_id)
        print("\nUpdated analyzer information:")
        print(f"  Description: {updated.description}")
        if updated.tags:
            tags_str = ", ".join(f"{k}={v}" for k, v in updated.tags.items())
            print(f"  Tags: {tags_str}")
        # [END update_analyzer]

        # Clean up - delete the analyzer
        print(f"\nCleaning up: deleting analyzer '{analyzer_id}'...")
        await client.delete_analyzer(analyzer_id=analyzer_id)
        print(f"Analyzer '{analyzer_id}' deleted successfully.")

    if not isinstance(credential, AzureKeyCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
