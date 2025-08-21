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
REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
    AZURE_CONVERSATIONS_AUTHORING_KEY
    (Optional) PROJECT_NAME   # defaults to "<project-name>"
"""

# [START conversation_authoring_get_project_async]
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import ProjectDetails

async def sample_get_project_async():
    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_AUTHORING_KEY"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # create an async client
    client = ConversationAuthoringClient(endpoint, AzureKeyCredential(key))

    try:
        # get project details
        details: ProjectDetails = await client.get_project(project_name=project_name)

        # print result details
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
    finally:
        await client.close()

async def main():
    await sample_get_project_async()

if __name__ == "__main__":
    asyncio.run(main())
# [END conversation_authoring_get_project_async]
