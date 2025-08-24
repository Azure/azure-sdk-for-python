# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_delete_project.py
DESCRIPTION:
    This sample demonstrates how to delete a Conversation Authoring project.
USAGE:
    python sample_delete_project.py

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

# [START conversation_authoring_delete_project]
import os
from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient


def sample_delete_project():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = ConversationAuthoringClient(endpoint, credential=credential)

    # start delete (long-running operation)
    poller = client.begin_delete_project(project_name=project_name)

    # wait for completion and get the result (no explicit type variables)
    result = poller.result()

    # print deletion details (direct attribute access; no getattr)
    print("=== Delete Project Result ===")
    print(f"Job ID: {result.job_id}")
    print(f"Status: {result.status}")
    print(f"Created on: {result.created_on}")
    print(f"Last updated on: {result.last_updated_on}")
    print(f"Expires on: {result.expires_on}")
    print(f"Warnings: {result.warnings}")
    print(f"Errors: {result.errors}")

# [END conversation_authoring_delete_project]


def main():
    sample_delete_project()


if __name__ == "__main__":
    main()
