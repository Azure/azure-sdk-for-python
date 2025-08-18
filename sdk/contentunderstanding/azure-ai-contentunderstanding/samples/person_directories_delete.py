# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""
Async sample: delete a person directory using the delete API.

This sample demonstrates the minimal workflow required to
1. Authenticate with Azure AI Content Understanding
2. Create a temporary person directory (for demo purposes)
3. Delete the person directory using the async delete API

Prerequisites:
    pip install azure-ai-contentunderstanding python-dotenv
    az login  # Used for DefaultAzureCredential(). Alternatively, set the AZURE_CONTENT_UNDERSTANDING_KEY environment variable

Environment variables:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional - DefaultAzureCredential() will be used if not set)
    These variables can be set in a .env file in the samples directory for repeated use. Please see env.sample for an example.

Run:
    python person_directories_delete.py
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

# Load environment variables from .env file, if present
load_dotenv()


async def main() -> None:  # noqa: D401 - simple function signature is fine for sample
    """Run the delete person directory sample."""
    endpoint: str = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    # Return AzureKeyCredential if AZURE_CONTENT_UNDERSTANDING_KEY is set, otherwise DefaultAzureCredential
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY")
    credential = AzureKeyCredential(key) if key else DefaultAzureCredential()

    # Create a temporary directory first so we have something to delete
    async with ContentUnderstandingClient(
        endpoint=endpoint, credential=credential
    ) as client, credential:
        directory_id = f"sdk-sample-dir-{datetime.now(timezone.utc):%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:8]}"
        print(f"🔧 Creating temporary directory '{directory_id}'...")
        await client.person_directories.create(
            person_directory_id=directory_id,
            resource=PersonDirectory(description="Temporary directory for delete demo"),
        )
        print("✅ Directory created - proceeding to delete")

        # Delete the directory
        print(f"🗑️  Deleting directory '{directory_id}'...")
        await client.person_directories.delete(person_directory_id=directory_id)
        print("✅ Directory deleted successfully")


if __name__ == "__main__":
    asyncio.run(main())
