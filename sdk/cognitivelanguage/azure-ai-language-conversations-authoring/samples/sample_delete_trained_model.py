# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_delete_trained_model.py
DESCRIPTION:
    This sample demonstrates how to delete a trained model from a Conversation Authoring project.
USAGE:
    python sample_delete_trained_model.py

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

# [START conversation_authoring_delete_trained_model]
import os
from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient


def sample_delete_trained_model():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    trained_model_label = os.environ.get("TRAINED_MODEL", "<trained-model-label>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = ConversationAuthoringClient(endpoint, credential=credential)
    project_client = client.get_project_client(project_name)

    captured = {}

    def capture_response(pipeline_response):
        # capture the raw HTTP response status code
        captured["status_code"] = pipeline_response.http_response.status_code

    # delete trained model
    project_client.trained_model.delete_trained_model(
        trained_model_label,
        raw_response_hook=capture_response,
    )

    # print response
    status = captured.get("status_code")
    print(f"Delete Trained Model Response Status: {status}")


# [END conversation_authoring_delete_trained_model]


def main():
    sample_delete_trained_model()


if __name__ == "__main__":
    main()
