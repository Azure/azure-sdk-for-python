# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_export_project_async.py
DESCRIPTION:
    This sample demonstrates how to export a Conversation Authoring project (async).
USAGE:
    python sample_export_project_async.py
REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
    AZURE_CONVERSATIONS_AUTHORING_KEY
    (Optional) PROJECT_NAME   # defaults to "<project-name>"
"""

# [START conversation_authoring_export_project_async]
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import ExportedProjectFormat, ExportProjectState

async def sample_export_project_async():
    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_AUTHORING_KEY"]

    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # create an async client
    client = ConversationAuthoringClient(endpoint, AzureKeyCredential(key))

    try:
        project_client = client.get_project_client(project_name)

        # start export (async long-running operation)
        poller = await project_client.project.begin_export(
            string_index_type="Utf16CodeUnit",
            exported_project_format=ExportedProjectFormat.CONVERSATION,
        )

        # wait for completion and get the result
        result: ExportProjectState = await poller.result()

        # print export details
        print("=== Export Project Result ===")
        print(f"Job ID: {result.job_id}")
        print(f"Status: {result.status}")
        print(f"Created on: {result.created_on}")
        print(f"Last updated on: {result.last_updated_on}")
        print(f"Expires on: {result.expires_on}")
        print(f"Warnings: {result.warnings}")
        print(f"Errors: {result.errors}")
    finally:
        await client.close()

async def main():
    await sample_export_project_async()

if __name__ == "__main__":
    asyncio.run(main())
# [END conversation_authoring_export_project_async]
