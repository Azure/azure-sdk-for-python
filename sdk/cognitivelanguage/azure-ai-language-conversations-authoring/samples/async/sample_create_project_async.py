# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_create_project_async.py
DESCRIPTION:
    This sample demonstrates how to create a Conversation Authoring project (async).
USAGE:
    python sample_create_project_async.py

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

# [START conversation_authoring_create_project_async]
import os
import asyncio
from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    CreateProjectOptions,
    ProjectKind,
)


async def sample_create_project_async():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    credential = DefaultAzureCredential()
    async with ConversationAuthoringClient(endpoint, credential=credential) as client:
        # build project definition
        body = CreateProjectOptions(
            project_kind=ProjectKind.CONVERSATION,
            project_name=project_name,
            language="<language-tag>",  # e.g. "en-us"
            multilingual=True,
            description="Sample project created via Python SDK",
        )

        # create project (no explicit type variables)
        result = await client.create_project(project_name=project_name, body=body)

        # print project details (direct attribute access; no getattr)
        print("=== Create Project Result ===")
        print(f"Project Name: {result.project_name}")
        print(f"Language: {result.language}")
        print(f"Kind: {result.project_kind}")
        print(f"Multilingual: {result.multilingual}")
        print(f"Description: {result.description}")


# [END conversation_authoring_create_project_async]


async def main():
    await sample_create_project_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
