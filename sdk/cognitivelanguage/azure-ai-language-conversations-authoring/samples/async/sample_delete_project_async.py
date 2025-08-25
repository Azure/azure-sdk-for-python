# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_delete_project_async.py
DESCRIPTION:
    This sample demonstrates how to delete a Conversation Authoring project (async).
USAGE:
    python sample_delete_project_async.py

REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET

NOTE:
    If you want to use AzureKeyCredential instead, set:
      - AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
      - AZURE_CONVERSATIONS_AUTHORING_KEY

OPTIONAL ENV VARS:
    PROJECT_NAME   # defaults to "<project-name>"
"""

# [START conversation_authoring_delete_project_async]
import os
import asyncio
from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient


async def sample_delete_project_async():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    credential = DefaultAzureCredential()
    async with ConversationAuthoringClient(endpoint, credential=credential) as client:
        # start delete (async long-running operation)
        poller = await client.begin_delete_project(project_name)

        # wait for completion and get the result (no explicit type variables)
        result = await poller.result()

        # print deletion details (direct attribute access; no getattr)
        print("=== Delete Project Result ===")
        print(f"Job ID: {result.job_id}")
        print(f"Status: {result.status}")
        print(f"Created on: {result.created_on}")
        print(f"Last updated on: {result.last_updated_on}")
        print(f"Expires on: {result.expires_on}")
        print(f"Warnings: {result.warnings}")
        print(f"Errors: {result.errors}")

# [END conversation_authoring_delete_project_async]

async def main():
    await sample_delete_project_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
