# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import asyncio
import os
from datetime import datetime, timezone
import uuid

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import PersonDirectory

from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()

"""
# PREREQUISITES
    pip install azure-ai-contentunderstanding python-dotenv
# USAGE
    python person_directories_update.py
"""


async def main():
    """
    Update person directory using update API.

    High-level steps:
    1. Create a person directory with initial description and tags
    2. Display initial directory state
    3. Update the directory with new description and tags
    4. Display updated directory state
    5. Save updated directory details to file
    6. Clean up the created directory
    """
    endpoint = os.getenv("AZURE_CONTENT_UNDERSTANDING_ENDPOINT") or ""
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(
        endpoint=endpoint, credential=credential
    ) as client, credential:
        directory_id = f"sdk-sample-dir-{datetime.now(timezone.utc):%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:8]}"

        # Create person directory with initial data
        print(f"🔧 Creating directory '{directory_id}' with initial data...")
        await client.person_directories.create(
            person_directory_id=directory_id,
            resource=PersonDirectory(
                description="Initial description for update demo",
                tags={
                    "created_by": "SDK Sample",
                    "demo_type": "update",
                    "version": "1.0",
                },
            ),
        )
        print("✅ Directory created successfully!")

        # Get initial state
        initial_state = await client.person_directories.get(
            person_directory_id=directory_id
        )
        print(f"📋 Initial directory state:")
        print(f"   Description: {getattr(initial_state, 'description', 'N/A')}")
        print(f"   Tags: {getattr(initial_state, 'tags', 'N/A')}")

        # Update the directory
        print(f"🔄 Updating directory '{directory_id}'...")
        response = await client.person_directories.update(
            person_directory_id=directory_id,
            resource={
                "description": "Updated description for update demo",
                "tags": {
                    "updated_by": "SDK Sample",
                    "demo_type": "update",
                    "version": "2.0",
                    "last_modified": datetime.now(timezone.utc).isoformat(),
                },
            },
            content_type="application/json",
        )

        print(f"✅ Directory updated successfully!")
        print(f"   Updated Description: {getattr(response, 'description', 'N/A')}")
        print(f"   Updated Tags: {getattr(response, 'tags', 'N/A')}")

        # Clean up the created directory (demo cleanup)
        print(f"🗑️  Deleting directory '{directory_id}' (demo cleanup)...")
        await client.person_directories.delete(person_directory_id=directory_id)
        print(f"✅ Directory '{directory_id}' deleted successfully!")


# x-ms-original-file: 2025-05-01-preview/PersonDirectories_Update.json
if __name__ == "__main__":
    asyncio.run(main())
