# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the asynchronous
    file operations using the OpenAI client: create, wait_for_processing, retrieve, content, list, and delete.

USAGE:
    python sample_files_async.py

    Before running the sample:

    pip install azure-ai-projects>=2.0.0b1 azure-identity openai python-dotenv aiohttp

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) FILE_PATH - Optional. Path to the file to upload. Defaults to the `data` folder.
"""

import asyncio
import os
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from pathlib import Path

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
script_dir = Path(__file__).parent
file_path = os.environ.get("FILE_PATH", os.path.join(script_dir, "data", "test_file.jsonl"))


async def main() -> None:

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        await project_client.get_openai_client() as openai_client,
    ):
        print("Uploading file")
        with open(file_path, "rb") as f:
            uploaded_file = await openai_client.files.create(file=f, purpose="fine-tune")
        print(uploaded_file)

        print("Waits for the given file to be processed, default timeout is 30 mins")
        processed_file = await openai_client.files.wait_for_processing(uploaded_file.id)
        print(processed_file)

        print(f"Retrieving file metadata with ID: {processed_file.id}")
        retrieved_file = await openai_client.files.retrieve(processed_file.id)
        print(retrieved_file)

        print(f"Retrieving file content with ID: {processed_file.id}")
        file_content = await openai_client.files.content(processed_file.id)
        print(file_content.content)

        print("Listing all files:")
        async for file in openai_client.files.list():
            print(file)

        print(f"Deleting file with ID: {processed_file.id}")
        deleted_file = await openai_client.files.delete(processed_file.id)
        print(f"Successfully deleted file: {deleted_file.id}")


if __name__ == "__main__":
    asyncio.run(main())
