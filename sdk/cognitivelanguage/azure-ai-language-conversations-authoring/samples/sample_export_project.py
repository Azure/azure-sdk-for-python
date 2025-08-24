# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_export_project.py
DESCRIPTION:
    This sample demonstrates how to export a Conversation Authoring project.
USAGE:
    python sample_export_project.py

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

# [START conversation_authoring_export_project]
import os
from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    ExportedProjectFormat,
    ExportProjectState,
)


def sample_export_project():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = ConversationAuthoringClient(endpoint, credential=credential)
    project_client = client.get_project_client(project_name)

    # start export (long-running operation)
    poller = project_client.project.begin_export(
        string_index_type="Utf16CodeUnit",
        exported_project_format=ExportedProjectFormat.CONVERSATION,
    )

    # wait for completion and get the result (no explicit type variables)
    result = poller.result()

    # print export details (direct attribute access; no getattr)
    print("=== Export Project Result ===")
    print(f"Job ID: {result.job_id}")
    print(f"Status: {result.status}")
    print(f"Created on: {result.created_on}")
    print(f"Last updated on: {result.last_updated_on}")
    print(f"Expires on: {result.expires_on}")
    print(f"Warnings: {result.warnings}")
    print(f"Errors: {result.errors}")

# [END conversation_authoring_export_project]


def main():
    sample_export_project()


if __name__ == "__main__":
    main()
