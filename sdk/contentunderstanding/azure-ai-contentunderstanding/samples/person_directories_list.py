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
Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python person_directories_list.py
"""

async def main():
    """
    List person directories using list API.
    
    High-level steps:
    1. Create a few temporary person directories (for demo purposes)
    2. List all directories using list API
    3. Display directory details
    4. Clean up the created directories
    """
    endpoint = os.getenv("AZURE_CONTENT_UNDERSTANDING_ENDPOINT") or ""
    credential = get_credential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client, credential:
        created_directories = []
        
        # Create a few directories for the list demo
        print("🔧 Creating sample directories for list demo...")
        for i in range(3):
            directory_id = f"sdk-sample-dir-{datetime.now(timezone.utc):%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:8]}"
            await client.person_directories.create(
                person_directory_id=directory_id,
                resource=PersonDirectory(
                    description=f"Sample directory {i+1} for list demo",
                    tags={"demo_type": "list", "index": str(i+1)}
                ),
            )
            created_directories.append(directory_id)
            print(f"   ✅ Created directory {i+1}: {directory_id}")

        # List all directories
        print(f"📋 Listing all person directories...")
        response = client.person_directories.list()
        directories = [directory async for directory in response]
        
        print(f"✅ Found {len(directories)} directories:")
        for i, directory in enumerate(directories, 1):
            print(f"   Directory {i}:")
            print(f"      ID: {getattr(directory, 'person_directory_id', 'N/A')}")
            print(f"      Description: {getattr(directory, 'description', 'N/A')}")
            print(f"      Created at: {getattr(directory, 'created_at', 'N/A')}")
            print(f"      Tags: {getattr(directory, 'tags', 'N/A')}")
            print()

        # Clean up the created directories (demo cleanup)
        print(f"🗑️  Deleting {len(created_directories)} directories (demo cleanup)...")
        for directory_id in created_directories:
            await client.person_directories.delete(person_directory_id=directory_id)
            print(f"   ✅ Deleted directory: {directory_id}")
        print("✅ All demo directories deleted successfully!")

# x-ms-original-file: 2025-05-01-preview/PersonDirectories_List.json
if __name__ == "__main__":
    asyncio.run(main())
