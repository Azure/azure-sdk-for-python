# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_delete_deployment_from_resources.py
DESCRIPTION:
    This sample demonstrates how to delete a deployment from specific resources in a Conversation Authoring project.

USAGE:
    python sample_delete_deployment_from_resources.py

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
    PROJECT_NAME         # defaults to "<project-name>"
    RESOURCE_ID          # defaults to "<azure-resource-id>"
"""

# [START conversation_authoring_delete_deployment_from_resources]
import os
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring import ConversationAuthoringClient
from azure.ai.language.conversations.authoring.models import ProjectResourceIds


def sample_delete_deployment_from_resources():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]

    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    resource_id = os.environ.get("RESOURCE_ID", "<azure-resource-id>")

    deployment_name = "test-deployment"

    credential = DefaultAzureCredential()
    client = ConversationAuthoringClient(endpoint, credential=credential)
    project_client = client.get_project_client(project_name)

    delete_body = ProjectResourceIds(azure_resource_ids=[resource_id])

    # start delete-from-resources (long-running operation)
    poller = project_client.deployment.begin_delete_deployment_from_resources(
        deployment_name=deployment_name,
        body=delete_body,
    )

    try:
        poller.result()
        print("Delete completed.")
        print(f"done: {poller.done()}")
        print(f"status: {poller.status()}")
    except HttpResponseError as e:
        print(f"Operation failed: {e.message}")
        print(e.error)


# [END conversation_authoring_delete_deployment_from_resources]


def main():
    sample_delete_deployment_from_resources()


if __name__ == "__main__":
    main()
