# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_load_snapshot_async.py
DESCRIPTION:
    This sample demonstrates how to load a snapshot of a trained model in a Conversation Authoring project (async).
USAGE:
    python sample_load_snapshot_async.py

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
    PROJECT_NAME       # defaults to "<project-name>"
    TRAINED_MODEL      # defaults to "<trained-model-label>"
"""

# [START conversation_authoring_load_snapshot_async]
import os
import asyncio
from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient


async def sample_load_snapshot_async():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    trained_model_label = os.environ.get("TRAINED_MODEL", "<trained-model-label>")

    credential = DefaultAzureCredential()
    async with ConversationAuthoringClient(endpoint, credential=credential) as client:
        project_client = client.get_project_client(project_name)

        # start load snapshot operation (async long-running operation)
        poller = await project_client.trained_model.begin_load_snapshot(trained_model_label)

        # wait for job completion and get the result (no explicit type variables)
        result = await poller.result()

        # print result details (direct attribute access; no getattr)
        print("=== Load Snapshot Result ===")
        print(f"Job ID: {result.job_id}")
        print(f"Status: {result.status}")
        print(f"Created on: {result.created_on}")
        print(f"Last updated on: {result.last_updated_on}")
        print(f"Expires on: {result.expires_on}")
        print(f"Warnings: {result.warnings}")
        print(f"Errors: {result.errors}")

# [END conversation_authoring_load_snapshot_async]

async def main():
    await sample_load_snapshot_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
