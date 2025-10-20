# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the asynchronous
    file operations using the OpenAI client: create, retrieve, content, list, and delete.

USAGE:
    python sample_files_async.py

    Before running the sample:

    pip install azure-ai-projects azure-identity aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) FILE_PATH - Required. Path to the file to upload.
"""

import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from pathlib import Path


async def main() -> None:

    endpoint = os.environ["PROJECT_ENDPOINT"]
    script_dir = Path(__file__).parent
    file_path = os.environ.get("FILE_PATH", os.path.join(script_dir, "data", "training_set.jsonl"))

    async with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

        async with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

            # Get OpenAI client from project client
            async with await project_client.get_openai_client(api_version="2025-04-01-preview") as open_ai_client:

                # [START files_async_sample]
                # Create (upload) a file.
                print("Uploading file")
                with open(file_path, "rb") as f:
                    uploaded_file = await open_ai_client.files.create(file=f, purpose="fine-tune")
                print(uploaded_file)

                # Retrieve file metadata by ID
                print(f"Retrieving file metadata with ID: {uploaded_file.id}")
                retrieved_file = await open_ai_client.files.retrieve(uploaded_file.id)
                print(retrieved_file)

                # Retrieve file content
                print(f"Retrieving file content with ID: {uploaded_file.id}")
                file_content = await open_ai_client.files.content(uploaded_file.id)
                print(file_content.content)

                # List all files
                print("Listing all files:")
                async for file in open_ai_client.files.list():
                    print(file)

                # Delete a file
                print(f"\nDeleting file with ID: {uploaded_file.id}")
                deleted_file = await open_ai_client.files.delete(uploaded_file.id)
                print(f"Successfully deleted file: {deleted_file.id}")
                # [END files_async_sample]

if __name__ == "__main__":
    asyncio.run(main())
