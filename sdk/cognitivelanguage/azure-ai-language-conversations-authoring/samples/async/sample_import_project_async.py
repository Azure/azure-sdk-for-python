# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_import_project_async.py
DESCRIPTION:
    This sample demonstrates how to import a Conversation Authoring project (async).
USAGE:
    python sample_import_project_async.py
REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
    AZURE_CONVERSATIONS_AUTHORING_KEY
    (Optional) PROJECT_NAME   # defaults to "<project-name>"
"""

# [START conversation_authoring_import_project_async]
import os
import asyncio
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring.aio import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    ConversationExportedIntent,
    ConversationExportedEntity,
    ConversationExportedUtterance,
    ExportedUtteranceEntityLabel,
    ConversationExportedProjectAsset,
    CreateProjectOptions,
    ProjectKind,
    ProjectSettings,
    ExportedProject,
    ExportedProjectFormat,
)

async def sample_import_project_async():
    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_AUTHORING_KEY"]

    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # create an async client
    client = ConversationAuthoringClient(endpoint, AzureKeyCredential(key))

    try:
        project_client = client.get_project_client(project_name)

        # ----- Build assets using objects (placeholders) -----
        intents = [
            ConversationExportedIntent(category="<intent-a>"),
            ConversationExportedIntent(category="<intent-b>"),
        ]

        entities = [
            ConversationExportedEntity(
                category="<entity-a>",
                composition_mode="combineComponents",
            )
        ]

        u1 = ConversationExportedUtterance(
            text="<utterance-1>",
            intent="<intent-b>",
            language="<language-tag>",
            dataset="Train",
            entities=[ExportedUtteranceEntityLabel(category="<entity-a>", offset=0, length=5)],
        )

        u2 = ConversationExportedUtterance(
            text="<utterance-2>",
            intent="<intent-b>",
            language="<language-tag>",
            dataset="Train",
            entities=[ExportedUtteranceEntityLabel(category="<entity-a>", offset=0, length=5)],
        )

        u3 = ConversationExportedUtterance(
            text="<utterance-3>",
            intent="<intent-b>",
            language="<language-tag>",
            dataset="Train",
            entities=[ExportedUtteranceEntityLabel(category="<entity-a>", offset=0, length=4)],
        )

        assets = ConversationExportedProjectAsset(
            intents=intents,
            entities=entities,
            utterances=[u1, u2, u3],
        )

        metadata = CreateProjectOptions(
            project_kind=ProjectKind.CONVERSATION,
            project_name=project_name,              # required
            language="<language-tag>",              # required (e.g., "en-us")
            settings=ProjectSettings(confidence_threshold=0.0),
            multilingual=False,
            description="",
        )

        exported_project = ExportedProject(
            project_file_version="<project-file-version>",  # e.g., "2025-05-15-preview"
            string_index_type="Utf16CodeUnit",
            metadata=metadata,
            assets=assets,
        )

        # ----- begin import (async long-running operation) -----
        poller = await project_client.project.begin_import(
            body=exported_project,
            exported_project_format=ExportedProjectFormat.CONVERSATION,
        )

        # wait for completion and get the result (ImportProjectState)
        result = await poller.result()

        # print result details
        print("=== Import Project Result ===")
        print(f"Job ID: {getattr(result, 'job_id', None)}")
        print(f"Status: {getattr(result, 'status', None)}")
        print(f"Created on: {getattr(result, 'created_on', None)}")
        print(f"Last updated on: {getattr(result, 'last_updated_on', None)}")
        print(f"Expires on: {getattr(result, 'expires_on', None)}")
        print(f"Warnings: {getattr(result, 'warnings', None)}")
        print(f"Errors: {getattr(result, 'errors', None)}")
    finally:
        await client.close()

async def main():
    await sample_import_project_async()

if __name__ == "__main__":
    asyncio.run(main())
# [END conversation_authoring_import_project_async]
