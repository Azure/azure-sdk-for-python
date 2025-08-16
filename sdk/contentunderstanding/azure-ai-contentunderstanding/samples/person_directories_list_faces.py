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
    python person_directories_list_faces.py
"""


async def main():
    """
    List faces in person directory using list_faces API.

    High-level steps:
    1. Create a temporary person directory and add persons
    2. Add multiple faces to those persons from local image files
    3. List all faces in the directory
    4. Display face details
    5. Save face list to file
    6. Clean up the directory
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
            resource=PersonDirectory(description="Temp directory for list_faces demo"),
        )

        # Add persons and faces
        sample_file_dir = os.path.dirname(os.path.abspath(__file__))
        face_files = [
            "enrollment_data/Alex/Family1-Son1.jpg",
            "enrollment_data/Bill/Family1-Dad1.jpg",
            "enrollment_data/Clare/Family1-Mom1.jpg",
        ]

        face_ids = []
        for i, face_file in enumerate(face_files):
            # Add a person
            person_response = await client.person_directories.add_person(
                person_directory_id=directory_id,
                body={"tags": {"name": f"Demo User {i+1}"}},
            )
            person_id = person_response.person_id
            print(f"👤 Person {i+1} created (id={person_id})")

            # Add face to person
            image_path = os.path.join(
                sample_file_dir, "sample_files", "face", face_file
            )
            image_b64 = read_image_to_base64(image_path)

            face_add_response = await client.person_directories.add_face(
                person_directory_id=directory_id,
                body={
                    "faceSource": {"data": image_b64},
                    "personId": person_id,
                },
            )
            face_ids.append(face_add_response.face_id)
            print(f"😀 Face {i+1} added (id={face_add_response.face_id})")

        # List all faces in the directory
        print(f"📋 Listing all faces in directory '{directory_id}'...")
        response = client.person_directories.list_faces(
            person_directory_id=directory_id,
        )
        faces = [face async for face in response]

        print(f"✅ Found {len(faces)} faces:")
        for i, face in enumerate(faces, 1):
            print(f"   Face {i}:")
            print(f"      Face ID: {getattr(face, 'face_id', 'N/A')}")
            print(f"      Person ID: {getattr(face, 'person_id', 'N/A')}")
            print(f"      Bounding Box: {getattr(face, 'bounding_box', 'N/A')}")
            print()

        # Clean up the created directory (demo cleanup)
        print(f"🗑️  Deleting directory '{directory_id}' (demo cleanup)...")
        await client.person_directories.delete(person_directory_id=directory_id)
        print("✅ Directory deleted - sample complete")


# x-ms-original-file: 2025-05-01-preview/PersonDirectories_ListFaces.json
if __name__ == "__main__":
    asyncio.run(main())
