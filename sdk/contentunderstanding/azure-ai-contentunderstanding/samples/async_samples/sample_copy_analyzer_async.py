# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
FILE: sample_copy_analyzer_async.py

DESCRIPTION:
    This sample demonstrates how to copy an analyzer from source to target within the same
    Microsoft Foundry resource using the begin_copy_analyzer API. This is useful for
    creating copies of analyzers for testing, staging, or production deployment.

    About copying analyzers
    The begin_copy_analyzer API allows you to copy an analyzer within the same Azure resource:
    - Same-resource copy: Copies an analyzer from one ID to another within the same resource
    - Exact copy: The target analyzer is an exact copy of the source analyzer

    Note: For cross-resource copying (copying between different Azure resources or subscriptions),
    use the grant_copy_auth sample instead.

USAGE:
    python sample_copy_analyzer_async.py

    Set the environment variables with your own values before running the sample:
    1) CONTENTUNDERSTANDING_ENDPOINT - the endpoint to your Content Understanding resource.
    2) CONTENTUNDERSTANDING_KEY - your Content Understanding API key (optional if using DefaultAzureCredential).
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
    endpoint = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
    key = os.getenv("CONTENTUNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        base_id = f"my_analyzer_{int(time.time())}"
        source_analyzer_id = f"{base_id}_source"
        target_analyzer_id = f"{base_id}_target"

        # Step 1: Create the source analyzer
        print(f"Creating source analyzer '{source_analyzer_id}'...")

        analyzer = ContentAnalyzer(
            base_analyzer_id="prebuilt-document",
            description="Source analyzer for copying",
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
            ),
            models={"completion": "gpt-4.1"},
            tags={"modelType": "in_development"},
        )

        poller = await client.begin_create_analyzer(
            analyzer_id=source_analyzer_id,
            resource=analyzer,
        )
        await poller.result()
        print(f"Source analyzer '{source_analyzer_id}' created successfully!")

        # Get the source analyzer to see its description and tags before copying
        source_analyzer_info = await client.get_analyzer(analyzer_id=source_analyzer_id)
        print(f"Source analyzer description: {source_analyzer_info.description}")
        if source_analyzer_info.tags:
            print(f"Source analyzer tags: {', '.join(f'{k}={v}' for k, v in source_analyzer_info.tags.items())}")

        # [START copy_analyzer]
        print(f"\nCopying analyzer from '{source_analyzer_id}' to '{target_analyzer_id}'...")

        poller = await client.begin_copy_analyzer(
            analyzer_id=target_analyzer_id,
            source_analyzer_id=source_analyzer_id,
        )
        await poller.result()

        print(f"Analyzer copied successfully!")
        # [END copy_analyzer]

        # [START update_and_verify_analyzer]
        # Get the target analyzer first to get its BaseAnalyzerId
        print(f"\nGetting target analyzer '{target_analyzer_id}'...")
        target_analyzer = await client.get_analyzer(analyzer_id=target_analyzer_id)

        # Update the target analyzer with a production tag
        updated_analyzer = ContentAnalyzer(
            base_analyzer_id=target_analyzer.base_analyzer_id,
            tags={"modelType": "model_in_production"},
        )

        print(f"Updating target analyzer with production tag...")
        await client.update_analyzer(analyzer_id=target_analyzer_id, resource=updated_analyzer)

        # Verify the update
        updated_target = await client.get_analyzer(analyzer_id=target_analyzer_id)
        print(f"Updated target analyzer description: {updated_target.description}")
        if updated_target.tags:
            print(f"Updated target analyzer tag: {updated_target.tags.get('modelType', 'N/A')}")
        # [END update_and_verify_analyzer]

        # [START delete_copied_analyzers]
        print(f"\nCleaning up analyzers...")

        try:
            await client.delete_analyzer(analyzer_id=source_analyzer_id)
            print(f"  Source analyzer '{source_analyzer_id}' deleted successfully.")
        except Exception:
            pass  # Ignore cleanup errors

        try:
            await client.delete_analyzer(analyzer_id=target_analyzer_id)
            print(f"  Target analyzer '{target_analyzer_id}' deleted successfully.")
        except Exception:
            pass  # Ignore cleanup errors
        # [END delete_copied_analyzers]

    if not isinstance(credential, AzureKeyCredential):
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
