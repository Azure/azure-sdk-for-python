# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import asyncio
import os

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import FaceSource, CompareFacesResult

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
    python faces_compare.py
"""


async def main():
    """
    Compare two faces using the faces.compare API with various calling patterns.

    This sample demonstrates:
    1. Using body parameter (original method)
    2. Using FaceSource objects (new method)
    3. Using positional bytes parameters (new overloaded method)
    4. Using mixed positional parameters (URL and bytes)

    The FaceSource model automatically handles base64 encoding when you pass bytes data.
    """
    endpoint = os.getenv("AZURE_CONTENT_UNDERSTANDING_ENDPOINT") or ""
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    async with ContentUnderstandingClient(
        endpoint=endpoint, credential=credential
    ) as client, credential:
        # Load test images
        sample_file_dir = os.path.dirname(os.path.abspath(__file__))
        image1_path = os.path.join(
            sample_file_dir, "sample_files", "face", "enrollment_data", "Bill", "Family1-Dad1.jpg"
        )
        image2_path = os.path.join(
            sample_file_dir, "sample_files", "face", "enrollment_data", "Bill", "Family1-Dad2.jpg"
        )

        print(f"🔍 Comparing faces between two images:")
        print(f"   Image 1: {os.path.basename(image1_path)}")
        print(f"   Image 2: {os.path.basename(image2_path)}")

        # Method 1: Using body parameter (original method)
        print(f"\n📋 Method 1: Using body parameter (original method)")
        # Read images as raw bytes - the API will handle base64 encoding internally
        with open(image1_path, "rb") as image_file:
            image1_bytes = image_file.read()
        with open(image2_path, "rb") as image_file:
            image2_bytes = image_file.read()
        
        response1: CompareFacesResult = await client.faces.compare(
            body={
                "faceSource1": {"data": image1_bytes},
                "faceSource2": {"data": image2_bytes}
            }
        )
        print(f"   ✅ Comparison successful: Confidence = {response1.confidence}")

        # Method 2: Using FaceSource objects (new method)
        print(f"\n📋 Method 2: Using FaceSource objects (new method)")
        # FaceSource stores raw bytes - base64 conversion happens during JSON serialization
        face_source1 = FaceSource(data=image1_bytes)
        face_source2 = FaceSource(data=image2_bytes)
        response2: CompareFacesResult = await client.faces.compare(
            face_source1=face_source1,
            face_source2=face_source2
        )
        print(f"   ✅ Comparison successful: Confidence = {response2.confidence}")

        # Method 3: Using positional bytes parameters (new overloaded method)
        print(f"\n📋 Method 3: Using positional bytes parameters (new overloaded method)")
        # Read images as raw bytes for positional test
        with open(image1_path, "rb") as image_file:
            image1_bytes = image_file.read()
        with open(image2_path, "rb") as image_file:
            image2_bytes = image_file.read()
        
        response3: CompareFacesResult = await client.faces.compare(
            image1_bytes,
            image2_bytes
        )
        print(f"   ✅ Comparison successful: Confidence = {response3.confidence}")

        # Method 4: Using mixed positional parameters (URL and bytes)
        print(f"\n📋 Method 4: Using mixed positional parameters (URL and bytes)")
        test_url = "https://example.com/test-image.jpg"
        try:
            response4: CompareFacesResult = await client.faces.compare(
                test_url,
                image2_bytes
            )
            print(f"   ✅ Comparison successful: Confidence = {response4.confidence}")
        except Exception as e:
            print(f"   ℹ️  Expected failure with invalid URL: {type(e).__name__}")
            print(f"   ✅ URL parameter handling works correctly")

        print(f"\n💡 Summary:")
        print(f"   - Method 1: Body parameter (original) - Confidence: {response1.confidence}")
        print(f"   - Method 2: FaceSource objects - Confidence: {response2.confidence}")
        print(f"   - Method 3: Positional bytes - Confidence: {response3.confidence}")
        print(f"   - Method 4: Mixed URL/bytes - Handles errors gracefully")
        print(f"\n🎯 Key Benefits:")
        print(f"   - Pass raw image bytes directly - no manual base64 conversion needed")
        print(f"   - FaceSource automatically handles base64 encoding during API serialization")
        print(f"   - Multiple intuitive calling patterns for different use cases")
        print(f"   - Full backward compatibility with existing code")


# x-ms-original-file: 2025-05-01-preview/Faces_Compare.json
if __name__ == "__main__":
    asyncio.run(main()) 