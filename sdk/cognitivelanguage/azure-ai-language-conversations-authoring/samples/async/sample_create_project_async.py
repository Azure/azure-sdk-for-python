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
REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
    AZURE_CONVERSATIONS_AUTHORING_KEY
    (Optional) PROJECT_NAME   # defaults to "<project-name>"
"""

# [START conversation_authoring_create_project_async]
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import CreateProjectOptions, ProjectKind, ProjectDetails


async def sample_create_project_async():
    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_AUTHORING_KEY"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # create an async client
    client = ConversationAuthoringClient(endpoint, AzureKeyCredential(key))

    try:
        # build project definition
        body = CreateProjectOptions(
            project_kind=ProjectKind.CONVERSATION,
            project_name=project_name,
            language="<language-tag>",  # e.g. "en-us"
            multilingual=True,
            description="Sample project created via Python SDK",
        )

        # create project
        result: ProjectDetails = await client.create_project(project_name=project_name, body=body)

        # print project details
        print("=== Create Project Result ===")
        print(f"Project Name: {result.project_name}")
        print(f"Language: {result.language}")
        print(f"Kind: {result.project_kind}")
        print(f"Multilingual: {result.multilingual}")
        print(f"Description: {result.description}")
    finally:
        await client.close()


async def main():
    await sample_create_project_async()


if __name__ == "__main__":
    asyncio.run(main())
# [END conversation_authoring_create_project_async]
