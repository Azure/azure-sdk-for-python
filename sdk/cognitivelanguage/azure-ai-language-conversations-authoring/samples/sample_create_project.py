# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_create_project.py
DESCRIPTION:
    This sample demonstrates how to create a Conversation Authoring project.
USAGE:
    python sample_create_project.py

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

# [START conversation_authoring_create_project]
import os
from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import (
    CreateProjectOptions,
    ProjectKind,
)


def sample_create_project():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = ConversationAuthoringClient(endpoint, credential=credential)

    # build project definition
    body = CreateProjectOptions(
        project_kind=ProjectKind.CONVERSATION,
        project_name=project_name,
        language="<language-tag>",  # e.g. "en-us"
        multilingual=True,
        description="Sample project created via Python SDK",
    )

    # create project
    result = client.create_project(project_name=project_name, body=body)

    # print project details (direct attribute access; no getattr)
    print("=== Create Project Result ===")
    print(f"Project Name: {result.project_name}")
    print(f"Language: {result.language}")
    print(f"Kind: {result.project_kind}")
    print(f"Multilingual: {result.multilingual}")
    print(f"Description: {result.description}")


# [END conversation_authoring_create_project]


def main():
    sample_create_project()


if __name__ == "__main__":
    main()
