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
Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python person_directories_get_face.py
"""


async def main():
    """
    Get face from person directory using get_face API.

    High-level steps:
    1. Create a temporary person directory and add one person
    2. Add a face to that person from a local image file
    3. Retrieve the face details using get_face API
    4. Display face details
    5. Save face details to file
    6. Clean up the directory
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
            resource=PersonDirectory(description="Temp directory for get_face demo"),
        )

        # Add a person so we can attach a face
        person_response = await client.person_directories.add_person(
            person_directory_id=directory_id,
            body={"tags": {"name": "Demo User"}},
        )
        person_id = person_response.person_id
        print(f"👤 Person created (id={person_id}) - adding face…")

        # Load image and convert to base64
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
        print(f"😀 Face added (id={face_id}) - retrieving face details…")

        # Get the face details
        response = await client.person_directories.get_face(
            person_directory_id=directory_id,
            face_id=face_id,
        )

        print(f"✅ Face details retrieved successfully!")
        print(f"   Face ID: {getattr(response, 'face_id', 'N/A')}")
        print(f"   Person ID: {getattr(response, 'person_id', 'N/A')}")
        print(f"   Bounding Box: {getattr(response, 'bounding_box', 'N/A')}")
        print(
            f"   Image Reference ID: {getattr(response, 'image_reference_id', 'N/A')}"
        )

        # Clean up the created directory (demo cleanup)
        print(f"🗑️  Deleting directory '{directory_id}' (demo cleanup)...")
        await client.person_directories.delete(person_directory_id=directory_id)
        print("✅ Directory deleted - sample complete")


# x-ms-original-file: 2025-05-01-preview/PersonDirectories_GetFace.json
if __name__ == "__main__":
    asyncio.run(main())
