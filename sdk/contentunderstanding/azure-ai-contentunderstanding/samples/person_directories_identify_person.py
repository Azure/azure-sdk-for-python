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
from azure.ai.contentunderstanding.models import PersonDirectory, FaceSource

from sample_helper import read_image_to_base64
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
    python person_directories_identify_person.py
"""


async def main():
    """
    Identify persons in an image using the identify_person API.

    High-level steps:
    1. Create a temporary person directory
    2. Add two persons: Bill and Clare
    3. Enroll multiple faces for each person from enrollment data
    4. Use identify_person API with family.jpg to identify detected persons
    5. Display identification results with confidence scores
    6. Clean up the directory

    This demonstrates person identification capabilities:
    - Creating a person directory with multiple enrolled persons
    - Enrolling multiple faces per person for better recognition
    - Identifying persons in a group photo using the identify_person API
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
            resource=PersonDirectory(
                description="Temp directory for identify_person demo"
            ),
        )

        # Add Bill as a person
        print(f"👤 Adding Bill to directory...")
        bill_response = await client.person_directories.add_person(
            person_directory_id=directory_id,
            body={"tags": {"name": "Bill", "role": "Father"}},
        )
        bill_id = bill_response.person_id
        print(f"   ✅ Bill added (id={bill_id})")

        # Add Clare as a person
        print(f"👤 Adding Clare to directory...")
        clare_response = await client.person_directories.add_person(
            person_directory_id=directory_id,
            body={"tags": {"name": "Clare", "role": "Mother"}},
        )
        clare_id = clare_response.person_id
        print(f"   ✅ Clare added (id={clare_id})")

        # Enroll faces for Bill
        sample_file_dir = os.path.dirname(os.path.abspath(__file__))
        bill_faces = [
            "enrollment_data/Bill/Family1-Dad1.jpg",
            "enrollment_data/Bill/Family1-Dad2.jpg",
            "enrollment_data/Bill/Family1-Dad3.jpg",
        ]

        print(f"😀 Enrolling faces for Bill...")
        for i, face_file in enumerate(bill_faces):
            image_path = os.path.join(
                sample_file_dir, "sample_files", "face", face_file
            )
            # Read image as bytes directly
            with open(image_path, "rb") as image_file:
                image_bytes = image_file.read()

            face_add_response = await client.person_directories.add_face(
                directory_id,
                image_bytes,
                person_id=bill_id,
            )
            face_id = face_add_response.face_id
            print(f"   ✅ Face {i+1} enrolled from {face_file} (id={face_id})")

        # Enroll faces for Clare
        clare_faces = [
            "enrollment_data/Clare/Family1-Mom1.jpg",
            "enrollment_data/Clare/Family1-Mom2.jpg",
        ]

        print(f"😀 Enrolling faces for Clare...")
        for i, face_file in enumerate(clare_faces):
            image_path = os.path.join(
                sample_file_dir, "sample_files", "face", face_file
            )
            # Read image as bytes directly
            with open(image_path, "rb") as image_file:
                image_bytes = image_file.read()

            face_add_response = await client.person_directories.add_face(
                directory_id,
                image_bytes,
                person_id=clare_id,
            )
            face_id = face_add_response.face_id
            print(f"   ✅ Face {i+1} enrolled from {face_file} (id={face_id})")

        # Now identify persons in the family.jpg image
        print(f"\n🔍 Identifying persons in family.jpg...")
        family_image_path = os.path.join(
            sample_file_dir, "sample_files", "face", "family.jpg"
        )
        family_image_b64 = read_image_to_base64(family_image_path)

        # Use identify_person API to identify persons in the image
        response = await client.person_directories.identify_person(
            person_directory_id=directory_id,
            face_source=FaceSource(data=family_image_b64),
            max_person_candidates=5,
        )

        # Display identification results
        if hasattr(response, "person_candidates") and response.person_candidates:
            print(f"✅ Identified {len(response.person_candidates)} person(s):")
            for i, candidate in enumerate(response.person_candidates, 1):
                person_id = getattr(candidate, "person_id", "N/A")
                confidence = getattr(candidate, "confidence", "N/A")
                
                # Map person ID to name for better display
                person_name = "Unknown"
                if person_id == bill_id:
                    person_name = "Bill"
                elif person_id == clare_id:
                    person_name = "Clare"
                
                print(f"   Person {i}:")
                print(f"      Name: {person_name}")
                print(f"      Person ID: {person_id}")
                print(f"      Confidence: {confidence}")
                print()
        else:
            print("ℹ️  No persons identified in the image")

        print(f"\n💡 Summary:")
        print(f"   - Created person directory with Bill and Clare")
        print(f"   - Enrolled {len(bill_faces)} faces for Bill")
        print(f"   - Enrolled {len(clare_faces)} faces for Clare")
        print(f"   - Used identify_person API to identify persons in family.jpg")

        # Clean up the created directory (demo cleanup)
        print(f"\n🗑️  Deleting directory '{directory_id}' (demo cleanup)...")
        await client.person_directories.delete(person_directory_id=directory_id)
        print("✅ Directory deleted - sample complete")


# x-ms-original-file: 2025-05-01-preview/PersonDirectories_IdentifyPerson.json
if __name__ == "__main__":
    asyncio.run(main())
