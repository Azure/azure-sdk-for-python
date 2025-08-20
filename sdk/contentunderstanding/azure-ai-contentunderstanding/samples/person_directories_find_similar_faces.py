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
    python person_directories_find_similar_faces.py
"""


async def main():
    """
    Find similar faces in person directory using find_similar_faces API.

    High-level steps:
    1. Create a temporary person directory and add a person (Bill)
    2. Add two different faces from Bill (Family1-Dad1.jpg and Family1-Dad2.jpg)
    3. Test 1: Query with Family1-Dad3.jpg (same person) - should find matches
    4. Test 2: Query with Family1-Mom1.jpg (different person - Clare) - should find no matches
    5. Display results and explain the differences
    6. Clean up the directory

    This demonstrates both positive and negative cases of face similarity:
    - Positive: Searching for the same person should return high-confidence matches
    - Negative: Searching for a different person should return no matches
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
                description="Temp directory for find_similar_faces demo"
            ),
        )

        # Add a person
        person_response = await client.person_directories.add_person(
            person_directory_id=directory_id,
            body={"tags": {"name": "Demo User"}},
        )
        person_id = person_response.person_id
        print(f"👤 Person created (id={person_id})")

        # Add two different faces to the person from Bill's family
        sample_file_dir = os.path.dirname(os.path.abspath(__file__))

        # Face images to add to the directory
        face_images = [
            "enrollment_data/Bill/Family1-Dad1.jpg",
            "enrollment_data/Bill/Family1-Dad2.jpg",
        ]

        face_ids = []
        print("😀 Adding different faces to person...")
        for i, face_file in enumerate(face_images):
            image_path = os.path.join(
                sample_file_dir, "sample_files", "face", face_file
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
            face_ids.append(face_id)
            print(f"   ✅ Face {i+1} added from {face_file} (id={face_id})")

        # Test 1: Find similar faces using Family1-Dad3.jpg as query
        # This should find matches since Dad3 is from the same person (Bill) as Dad1 and Dad2
        print(f"\n🔍 Test 1: Finding faces similar to Family1-Dad3.jpg...")
        print(
            f"   Expected: Should find matches with enrolled Dad1 and Dad2 faces (same person)"
        )
        query_image_path = os.path.join(
            sample_file_dir,
            "sample_files",
            "face",
            "enrollment_data",
            "Bill",
            "Family1-Dad3.jpg",
        )
        query_image_base64 = read_image_to_base64(query_image_path)

        response = await client.person_directories.find_similar_faces(
            person_directory_id=directory_id,
            face_source=FaceSource(data=query_image_base64),
            max_similar_faces=10,
        )

        # Display results for Dad3 query
        if hasattr(response, "similar_faces") and response.similar_faces:
            print(f"✅ Found {len(response.similar_faces)} similar faces:")
            for i, similar_face in enumerate(response.similar_faces, 1):
                print(f"   Face {i}:")
                print(f"      Face ID: {getattr(similar_face, 'face_id', 'N/A')}")
                print(f"      Confidence: {getattr(similar_face, 'confidence', 'N/A')}")
                print(f"      Person ID: {getattr(similar_face, 'person_id', 'N/A')}")
                print()
        else:
            print("ℹ️  No similar faces found")

        # Test 2: Find similar faces using Family1-Mom1.jpg as query (different person - Clare)
        # This should find NO matches since Clare (Mom) is a different person than Bill (Dad)
        print(f"\n🔍 Test 2: Finding faces similar to Family1-Mom1.jpg...")
        print(
            f"   Expected: Should find NO matches (Clare is a different person than Bill)"
        )
        mom_query_path = os.path.join(
            sample_file_dir,
            "sample_files",
            "face",
            "enrollment_data",
            "Clare",
            "Family1-Mom1.jpg",
        )
        mom_query_b64 = read_image_to_base64(mom_query_path)

        mom_response = await client.person_directories.find_similar_faces(
            person_directory_id=directory_id,
            body={"faceSource": {"data": mom_query_b64}, "maxSimilarFaces": 10},
        )

        # Display results for Mom1 query
        if hasattr(mom_response, "similar_faces") and mom_response.similar_faces:
            print(
                f"⚠️  Unexpected: Found {len(mom_response.similar_faces)} similar faces:"
            )
            for i, similar_face in enumerate(mom_response.similar_faces, 1):
                print(f"   Face {i}:")
                print(f"      Face ID: {getattr(similar_face, 'face_id', 'N/A')}")
                print(f"      Confidence: {getattr(similar_face, 'confidence', 'N/A')}")
                print(f"      Person ID: {getattr(similar_face, 'person_id', 'N/A')}")
                print()
        else:
            print("✅ No similar faces found (as expected - different person)")

        print(f"\n💡 Summary:")
        print(
            f"   - Dad3 query: Demonstrates finding similar faces within the same person"
        )
        print(
            f"   - Mom1 query: Demonstrates no matches when searching for a different person"
        )

        # Clean up the created directory (demo cleanup)
        print(f"🗑️  Deleting directory '{directory_id}' (demo cleanup)...")
        await client.person_directories.delete(person_directory_id=directory_id)
        print("✅ Directory deleted - sample complete")


# x-ms-original-file: 2025-05-01-preview/PersonDirectories_FindSimilarFaces.json
if __name__ == "__main__":
    asyncio.run(main())
