# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import asyncio
import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import PersonDirectory

from sample_helper import get_credential, save_response_to_file

load_dotenv()

"""
# PREREQUISITES
    pip install azure-ai-contentunderstanding python-dotenv
# USAGE
    python person_directories_get.py
"""


def _generate_person_directory_id() -> str:
    """Generate a unique person directory ID with current date, time, and GUID."""
    import uuid
    now = datetime.now(timezone.utc)
    return f"sdk-sample-directory-{now:%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:8]}"


async def main():
    """
    Get person directory using get API.
    
    High-level steps:
    1. Create a temporary person directory (for demo purposes)
    2. Retrieve the directory using get API
    3. Display directory details
    4. Save directory details to file
    5. Clean up the created directory
    """
    endpoint = os.getenv("AZURE_CONTENT_UNDERSTANDING_ENDPOINT")
    credential = get_credential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client, credential:
        directory_id = _generate_person_directory_id()
        
        # Create person directory for retrieval demo
        print(f"🔧 Creating directory '{directory_id}' for retrieval demo...")
        await client.person_directories.create(
            person_directory_id=directory_id,
            resource=PersonDirectory(
                description=f"Sample directory for get demo: {directory_id}",
                tags={"demo_type": "get", "created_by": "SDK Sample"}
            ),
        )
        print("✅ Directory created successfully!")

        # Get the directory
        print(f"📋 Retrieving directory '{directory_id}'...")
        response = await client.person_directories.get(
            person_directory_id=directory_id,
        )
        
        print(f"✅ Directory retrieved successfully!")
        print(f"   ID: {getattr(response, 'person_directory_id', 'N/A')}")
        print(f"   Description: {getattr(response, 'description', 'N/A')}")
        print(f"   Created at: {getattr(response, 'created_at', 'N/A')}")
        print(f"   Tags: {getattr(response, 'tags', 'N/A')}")

        # Save the directory details to a file
        saved_file_path = save_response_to_file(
            result=response,
            filename_prefix="person_directories_get"
        )
        print(f"💾 Directory details saved to: {saved_file_path}")

        # Clean up the created directory (demo cleanup)
        print(f"🗑️  Deleting directory '{directory_id}' (demo cleanup)...")
        await client.person_directories.delete(person_directory_id=directory_id)
        print(f"✅ Directory '{directory_id}' deleted successfully!")


# x-ms-original-file: 2025-05-01-preview/PersonDirectories_Get.json
if __name__ == "__main__":
    asyncio.run(main())
