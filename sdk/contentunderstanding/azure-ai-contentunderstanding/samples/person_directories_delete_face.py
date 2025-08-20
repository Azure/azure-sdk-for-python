# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: delete a face from a person directory using the delete_face API.

The sample performs the following high-level steps:
1. Authenticate with Azure AI Content Understanding
2. Create a temporary person directory and add one person
3. (Optionally) add a face to that person - obtaining a face_id
4. Delete that face using delete_face
5. Clean up the directory

Dependencies:
    pip install azure-ai-contentunderstanding python-dotenv

Environment variables expected:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - falls back to DefaultAzureCredential)
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from typing import Optional
import uuid

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import PersonDirectory


from azure.core.credentials import AzureKeyCredential
from azure.identity.aio import DefaultAzureCredential

load_dotenv()


async def main():
    """
    Delete face from person directory using delete_face API.

    High-level steps:
    1. Create a temporary person directory and add one person
    2. Add a face to that person from a local image file
    3. Delete that face using delete_face
    4. Clean up the directory
    """
    endpoint = os.getenv("AZURE_CONTENT_UNDERSTANDING_ENDPOINT") or ""
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(
        endpoint=endpoint, credential=credential
    ) as client, credential:
        directory_id = f"sdk-sample-dir-{datetime.now(timezone.utc):%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:8]}"

        # Create person directory
        print(f"🔧 Creating directory '{directory_id}'...")
        await client.person_directories.create(
            person_directory_id=directory_id,
            resource=PersonDirectory(description="Temp directory for delete_face demo"),
        )

        # Add a person so we can attach a face
        person_response = await client.person_directories.add_person(
            person_directory_id=directory_id,
            tags={"name": "Demo User"},
        )
        person_id = person_response.person_id
        print(f"👤 Person created (id={person_id}) - adding face…")

        # Load image as bytes (using the new overloaded method)
        sample_file_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(
            sample_file_dir,
            "sample_files",
            "face",
            "enrollment_data",
            "Alex",
            "Family1-Son1.jpg",
        )
        
        # Read image as bytes directly
        with open(image_path, "rb") as image_file:
            image_bytes = image_file.read()

        face_add_response = await client.person_directories.add_face(
            directory_id,
            person_id,
            image_bytes,
        )
        face_id = face_add_response.face_id
        print(f"😀 Face added (id={face_id}) - deleting now…")

        # Delete the face
        await client.person_directories.delete_face(
            person_directory_id=directory_id,
            face_id=face_id,
        )
        print("✅ Face deleted - cleaning up directory")

        # Clean up the created directory (demo cleanup)
        await client.person_directories.delete(person_directory_id=directory_id)
        print("✅ Directory deleted - sample complete")


if __name__ == "__main__":
    asyncio.run(main())
