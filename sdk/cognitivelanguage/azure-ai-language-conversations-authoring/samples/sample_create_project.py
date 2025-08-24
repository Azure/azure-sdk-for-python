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
REQUIRED ENV VARS:
    AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
    AZURE_CONVERSATIONS_AUTHORING_KEY
    (Optional) PROJECT_NAME   # defaults to "<project-name>"
"""

# [START conversation_authoring_create_project]
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import CreateProjectOptions, ProjectKind, ProjectDetails


def sample_create_project():
    # get secrets
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    key = os.environ["AZURE_CONVERSATIONS_AUTHORING_KEY"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # create a client
    client = ConversationAuthoringClient(endpoint, AzureKeyCredential(key))

    # build project definition
    body = CreateProjectOptions(
        project_kind=ProjectKind.CONVERSATION,
        project_name=project_name,
        language="<language-tag>",  # e.g. "en-us"
        multilingual=True,
        description="Sample project created via Python SDK",
    )

    # create project
    result: ProjectDetails = client.create_project(project_name=project_name, body=body)

    # print project details
    print("=== Create Project Result ===")
    print(f"Project Name: {result.project_name}")
    print(f"Language: {result.language}")
    print(f"Kind: {result.project_kind}")
    print(f"Multilingual: {result.multilingual}")
    print(f"Description: {result.description}")


if __name__ == "__main__":
    sample_create_project()
# [END conversation_authoring_create_project]
