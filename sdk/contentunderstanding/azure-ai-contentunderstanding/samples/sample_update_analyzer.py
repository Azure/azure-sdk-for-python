# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_update_analyzer.py

DESCRIPTION:
    This sample demonstrates how to update an existing custom analyzer, including updating
    its description and tags.

    The update_analyzer method allows you to modify certain properties of an existing analyzer.
    The following properties can be updated:
    - Description: Update the analyzer's description
    - Tags: Add or update tags

USAGE:
    python sample_update_analyzer.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).
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
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    client = ContentUnderstandingClient(endpoint=endpoint, credential=credential)

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

    poller = client.begin_create_analyzer(
        analyzer_id=analyzer_id,
        resource=analyzer,
    )
    poller.result()
    print(f"Analyzer '{analyzer_id}' created successfully!")

    # [START update_analyzer]
    # First, get the current analyzer to preserve base analyzer ID
    current_analyzer = client.get_analyzer(analyzer_id=analyzer_id)

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
            "tag3": "tag3_value",  # Add new tag
        },
    )

    # Update the analyzer
    print(f"\nUpdating analyzer '{analyzer_id}'...")
    client.update_analyzer(analyzer_id=analyzer_id, resource=updated_analyzer)

    # Verify the update
    updated = client.get_analyzer(analyzer_id=analyzer_id)
    print("\nUpdated analyzer information:")
    print(f"  Description: {updated.description}")
    if updated.tags:
        tags_str = ", ".join(f"{k}={v}" for k, v in updated.tags.items())
        print(f"  Tags: {tags_str}")
    # [END update_analyzer]

    # Clean up - delete the analyzer
    print(f"\nCleaning up: deleting analyzer '{analyzer_id}'...")
    client.delete_analyzer(analyzer_id=analyzer_id)
    print(f"Analyzer '{analyzer_id}' deleted successfully.")


if __name__ == "__main__":
    main()
