# pylint: disable=line-too-long,useless-suppression
# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_deployment_delete_from_resources_status.py
DESCRIPTION:
    This sample demonstrates how to get the status of a deployment deletion job from specific resources in a Conversation Authoring project.

USAGE:
    python sample_get_deployment_delete_from_resources_status.py

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
"""

# [START conversation_authoring_get_deployment_delete_from_resources_status]
import os
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring import ConversationAuthoringClient


def sample_deployment_delete_status():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    deployment_name = "deploysdk02"
    job_id = "00000000-0000-0000-0000-000000000000"

    credential = DefaultAzureCredential()
    client = ConversationAuthoringClient(endpoint, credential=credential)
    project_client = client.get_project_client(project_name)

    # start get-status call
    try:
        state = project_client.deployment.get_deployment_delete_from_resources_status(
            deployment_name=deployment_name,
            job_id=job_id,
        )
        print("Status retrieved successfully.")
        print(f"Job ID: {state.job_id}")
        print(f"Status: {state.status}")
        print(f"Created On: {state.created_on}")
        print(f"Last Updated On: {state.last_updated_on}")
        print(f"Expires On: {state.expires_on}")
    except HttpResponseError as e:
        print(f"Operation failed: {e.message}")
        print(e.error)


# [END conversation_authoring_get_deployment_delete_from_resources_status]


def main():
    sample_deployment_delete_status()


if __name__ == "__main__":
    main()
