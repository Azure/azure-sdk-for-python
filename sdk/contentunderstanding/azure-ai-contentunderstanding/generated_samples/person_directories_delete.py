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

Dependencies:
    pip install azure-ai-contentunderstanding python-dotenv

Environment variables expected:
    AZURE_CONTENT_UNDERSTANDING_ENDPOINT   (required)
    AZURE_CONTENT_UNDERSTANDING_KEY        (optional – falls back to DefaultAzureCredential)
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
from azure.ai.contentunderstanding.aio import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import PersonDirectory

from sample_helper import get_credential

# Load environment variables from .env file, if present
load_dotenv()


def _generate_person_directory_id() -> str:
    """Return a unique person directory ID."""
    import uuid

    now = datetime.now(timezone.utc)
    return f"sdk-sample-directory-{now:%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:8]}"


async def main() -> None:  # noqa: D401 – simple function signature is fine for sample
    """Run the delete person directory sample."""
    endpoint: str = os.environ["AZURE_CONTENT_UNDERSTANDING_ENDPOINT"]
    credential = get_credential()

    # Create a temporary directory first so we have something to delete
    async with ContentUnderstandingClient(endpoint=endpoint, credential=credential) as client, credential:
        directory_id = _generate_person_directory_id()
        print(f"🔧 Creating temporary directory '{directory_id}'...")
        await client.person_directories.create(
            person_directory_id=directory_id,
            resource=PersonDirectory(description="Temporary directory for delete demo"),
        )
        print("✅ Directory created – proceeding to delete")

        # Delete the directory
        print(f"🗑️  Deleting directory '{directory_id}'...")
        await client.person_directories.delete(person_directory_id=directory_id)
        print("✅ Directory deleted successfully")


if __name__ == "__main__":
    asyncio.run(main())
