# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_project_async.py
DESCRIPTION:
    This sample demonstrates how to retrieve details of a Conversation Authoring project (async).
USAGE:
    python sample_get_project_async.py

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

# [START conversation_authoring_get_project_async]
import os
import asyncio
from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient


async def sample_get_project_async():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    credential = DefaultAzureCredential()
    async with ConversationAuthoringClient(endpoint, credential=credential) as client:
        # get project details (no explicit type variables)
        details = await client.get_project(project_name=project_name)

        # print result details (direct attribute access)
        print("=== Project Details ===")
        print(f"Created DateTime: {details.created_on}")
        print(f"Last Modified DateTime: {details.last_modified_on}")
        print(f"Last Trained DateTime: {details.last_trained_on}")
        print(f"Last Deployed DateTime: {details.last_deployed_on}")
        print(f"Project Kind: {details.project_kind}")
        print(f"Project Name: {details.project_name}")
        print(f"Multilingual: {details.multilingual}")
        print(f"Description: {details.description}")
        print(f"Language: {details.language}")

# [END conversation_authoring_get_project_async]

async def main():
    await sample_get_project_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
