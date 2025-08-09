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

from sample_helper import get_credential, generate_person_directory_id, read_image_to_base64

load_dotenv()

"""
# PREREQUISITES
    pip install azure-ai-contentunderstanding python-dotenv
# USAGE
    python person_directories_update_face.py
"""

async def main():
    """
    Update face in person directory using update_face API.
    
    High-level steps:
    1. Create a temporary person directory and add two persons
    2. Add a face to the first person from a local image file
    3. Update the face to associate it with the second person
    4. Verify the face has been reassigned
    5. Save updated face details to file
    6. Clean up the directory
    """
    endpoint = os.getenv("AZURE_CONTENT_UNDERSTANDING_ENDPOINT") or ""
    credential = get_credential()

    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client, credential:
        directory_id = generate_person_directory_id()
        
        # Create person directory
        print(f"🔧 Creating directory '{directory_id}'...")
        await client.person_directories.create(
            person_directory_id=directory_id,
            resource=PersonDirectory(description="Temp directory for update_face demo"),
        )

        # Add two persons
        person1_response = await client.person_directories.add_person(
            person_directory_id=directory_id,
            body={"tags": {"name": "Demo User 1"}},
        )
        person1_id = person1_response.person_id
        print(f"👤 Person 1 created (id={person1_id})")

        person2_response = await client.person_directories.add_person(
            person_directory_id=directory_id,
            body={"tags": {"name": "Demo User 2"}},
        )
        person2_id = person2_response.person_id
        print(f"👤 Person 2 created (id={person2_id})")

        # Add face to person 1
        sample_file_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(sample_file_dir, "sample_files", "face", "enrollment_data", "Alex", "Family1-Son1.jpg")
        image_b64 = read_image_to_base64(image_path)

        face_add_response = await client.person_directories.add_face(
            person_directory_id=directory_id,
            body={
                "faceSource": {"data": image_b64},
                "personId": person1_id,
            },
        )
        face_id = face_add_response.face_id
        print(f"😀 Face added to person 1 (face_id={face_id})")

        # Verify initial face assignment
        initial_face = await client.person_directories.get_face(
            person_directory_id=directory_id,
            face_id=face_id,
        )
        print(f"📋 Initial face assignment: person_id={getattr(initial_face, 'person_id', 'N/A')}")

        # Update the face to associate it with person 2
        print(f"🔄 Updating face to associate with person 2...")
        response = await client.person_directories.update_face(
            person_directory_id=directory_id,
            face_id=face_id,
            resource={"personId": person2_id},
            content_type="application/json"
        )
        
        print(f"✅ Face updated successfully!")
        print(f"   Face ID: {getattr(response, 'face_id', 'N/A')}")
        print(f"   New Person ID: {getattr(response, 'person_id', 'N/A')}")

        # Clean up the created directory (demo cleanup)
        print(f"🗑️  Deleting directory '{directory_id}' (demo cleanup)...")
        await client.person_directories.delete(person_directory_id=directory_id)
        print("✅ Directory deleted – sample complete")

# x-ms-original-file: 2025-05-01-preview/PersonDirectories_UpdateFace.json
if __name__ == "__main__":
    asyncio.run(main())
