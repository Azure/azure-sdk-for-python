# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_load_snapshot.py
DESCRIPTION:
    This sample demonstrates how to load a snapshot of a trained model in a Conversation Authoring project.
USAGE:
    python sample_load_snapshot.py

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
    PROJECT_NAME       # defaults to "<project-name>"
    TRAINED_MODEL      # defaults to "<trained-model-label>"
"""

# [START conversation_authoring_load_snapshot]
import os
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring import ConversationAuthoringClient


def sample_load_snapshot():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    trained_model_label = os.environ.get("TRAINED_MODEL", "<trained-model-label>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = ConversationAuthoringClient(endpoint, credential=credential)
    project_client = client.get_project_client(project_name)

    # start load snapshot operation (long-running operation)
    poller = project_client.trained_model.begin_load_snapshot(trained_model_label)

    try:
        poller.result()
        print("Load completed.")
        print(f"done: {poller.done()}")
        print(f"status: {poller.status()}")
    except HttpResponseError as e:
        print(f"Operation failed: {e.message}")
        print(e.error)


# [END conversation_authoring_load_snapshot]


def main():
    sample_load_snapshot()


if __name__ == "__main__":
    main()
