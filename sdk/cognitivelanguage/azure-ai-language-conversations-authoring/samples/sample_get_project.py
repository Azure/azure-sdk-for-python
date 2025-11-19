# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_project.py
DESCRIPTION:
    This sample demonstrates how to retrieve details of a Conversation Authoring project.
USAGE:
    python sample_get_project.py

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

# [START conversation_authoring_get_project]
import os
from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient


def sample_get_project():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = ConversationAuthoringClient(endpoint, credential=credential)

    # get project details (no explicit type variables)
    details = client.get_project(project_name=project_name)

    # print result details (direct attribute access; no getattr)
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


# [END conversation_authoring_get_project]


def main():
    sample_get_project()


if __name__ == "__main__":
    main()
