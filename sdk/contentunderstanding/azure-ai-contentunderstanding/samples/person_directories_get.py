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

from sample_helper import get_credential

load_dotenv()

"""
# PREREQUISITES
    pip install azure-ai-contentunderstanding python-dotenv
# USAGE
    python person_directories_get.py
"""

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
    endpoint = os.getenv("AZURE_CONTENT_UNDERSTANDING_ENDPOINT") or ""
    credential = get_credential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client:
        directory_id = f"sdk-sample-dir-{datetime.now(timezone.utc):%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:8]}"
        
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

        # Clean up the created directory (demo cleanup)
        print(f"🗑️  Deleting directory '{directory_id}' (demo cleanup)...")
        await client.person_directories.delete(person_directory_id=directory_id)
        print(f"✅ Directory '{directory_id}' deleted successfully!")

# x-ms-original-file: 2025-05-01-preview/PersonDirectories_Get.json
if __name__ == "__main__":
    asyncio.run(main())
