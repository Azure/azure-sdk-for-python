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

from sample_helper import get_credential, read_image_to_base64

load_dotenv()

"""
# PREREQUISITES
    pip install azure-ai-contentunderstanding python-dotenv
# USAGE
    python person_directories_update_person.py
"""


async def main():
    """
    Update person in person directory using update_person API.

    High-level steps:
    1. Create a temporary person directory and add a person
    2. Add a face to the person from a local image file
    3. Display initial person state with face association
    4. Update the person with new tags and face associations
    5. Display updated person state
    6. Save updated person details to file
    7. Clean up the directory
    """
    endpoint = os.getenv("AZURE_CONTENT_UNDERSTANDING_ENDPOINT") or ""
    credential = get_credential()

    async with ContentUnderstandingClient(
        endpoint=endpoint, credential=credential
    ) as client:
        directory_id = f"sdk-sample-dir-{datetime.now(timezone.utc):%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:8]}"

        # Create person directory
        print(f"🔧 Creating directory '{directory_id}'...")
        await client.person_directories.create(
            person_directory_id=directory_id,
            resource=PersonDirectory(
                description="Temp directory for update_person demo"
            ),
        )

        # Add a person with initial tags
        person_response = await client.person_directories.add_person(
            person_directory_id=directory_id,
            body={
                "tags": {
                    "name": "Demo User",
                    "role": "test_subject",
                    "department": "engineering",
                }
            },
        )
        person_id = person_response.person_id
        print(f"👤 Person created (id={person_id})")

        # Add a face to the person
        sample_file_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(
            sample_file_dir,
            "sample_files",
            "face",
            "enrollment_data",
            "Alex",
            "Family1-Son1.jpg",
        )
        image_b64 = read_image_to_base64(image_path)

        face_add_response = await client.person_directories.add_face(
            person_directory_id=directory_id,
            body={
                "faceSource": {"data": image_b64},
                "personId": person_id,
            },
        )
        face_id = face_add_response.face_id
        print(f"😀 Face added (face_id={face_id})")

        # Get initial person state
        initial_person = await client.person_directories.get_person(
            person_directory_id=directory_id, person_id=person_id
        )
        print(f"📋 Initial person state:")
        print(f"   Tags: {getattr(initial_person, 'tags', 'N/A')}")
        print(f"   Face IDs: {getattr(initial_person, 'face_ids', 'N/A')}")

        # Update the person with new tags
        print(f"🔄 Updating person with new tags...")
        response = await client.person_directories.update_person(
            person_directory_id=directory_id,
            person_id=person_id,
            resource={
                "tags": {
                    "name": "Demo User - Updated",
                    "role": "senior_test_subject",
                    "department": "research",
                    "location": "Building A",
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                }
            },
            content_type="application/json",
        )

        print(f"✅ Person updated successfully!")
        print(f"   Person ID: {getattr(response, 'person_id', 'N/A')}")
        print(f"   Updated Tags: {getattr(response, 'tags', 'N/A')}")
        print(f"   Face IDs: {getattr(response, 'face_ids', 'N/A')}")

        # Clean up the created directory (demo cleanup)
        print(f"🗑️  Deleting directory '{directory_id}' (demo cleanup)...")
        await client.person_directories.delete(person_directory_id=directory_id)
        print("✅ Directory deleted - sample complete")


# x-ms-original-file: 2025-05-01-preview/PersonDirectories_UpdatePerson.json
if __name__ == "__main__":
    asyncio.run(main())
