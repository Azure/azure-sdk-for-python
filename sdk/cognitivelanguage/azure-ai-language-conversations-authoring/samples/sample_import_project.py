# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_import_project.py
DESCRIPTION:
    This sample demonstrates how to import a Conversation Authoring project.
USAGE:
    python sample_import_project.py

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

# [START conversation_authoring_import_project]
import os
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
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


def sample_import_project():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = ConversationAuthoringClient(endpoint, credential=credential)
    project_client = client.get_project_client(project_name)

    # ----- Build assets using objects -----
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
        language="<language-tag>",  # e.g., "en-us"
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
        project_name=project_name,  # required
        language="<language-tag>",  # required (e.g., "en-us")
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

    # ----- begin import (long-running operation) -----
    poller = project_client.project.begin_import(
        body=exported_project,
        exported_project_format=ExportedProjectFormat.CONVERSATION,
    )

    try:
        poller.result()
        print("Import completed.")
        print(f"done: {poller.done()}")
        print(f"status: {poller.status()}")
    except HttpResponseError as e:
        print(f"Operation failed: {e.message}")
        print(e.error)


# [END conversation_authoring_import_project]


def main():
    sample_import_project()


if __name__ == "__main__":
    main()
