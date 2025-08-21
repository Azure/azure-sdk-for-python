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
REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
    AZURE_CONVERSATIONS_AUTHORING_KEY
    (Optional) PROJECT_NAME       # defaults to "<project-name>"
    (Optional) TRAINED_MODEL      # defaults to "<trained-model-label>"
"""

# [START conversation_authoring_load_snapshot_async]
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import LoadSnapshotState

async def sample_load_snapshot_async():
    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_AUTHORING_KEY"]

    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    trained_model_label = os.environ.get("TRAINED_MODEL", "<trained-model-label>")

    # create an async client
    client = ConversationAuthoringClient(endpoint, AzureKeyCredential(key))

    try:
        project_client = client.get_project_client(project_name)

        # start load snapshot operation (async long-running operation)
        poller = await project_client.trained_model.begin_load_snapshot(trained_model_label)

        # wait for job completion and get the result
        result: LoadSnapshotState = await poller.result()

        # print result details
        print("=== Load Snapshot Result ===")
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
    await sample_load_snapshot_async()

if __name__ == "__main__":
    asyncio.run(main())
# [END conversation_authoring_load_snapshot_async]
