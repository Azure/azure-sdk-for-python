# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_list_assigned_resource_deployments.py
DESCRIPTION:
    This sample demonstrates how to list all assigned resource deployments for Conversation Authoring projects.

USAGE:
    python sample_list_assigned_resource_deployments.py

REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET

NOTE:
    If you want to use AzureKeyCredential instead, set:
      - AZURE_CONVERSATIONS_AUTHORING_ENDPOINT
      - AZURE_CONVERSATIONS_AUTHORING_KEY
"""

# [START conversation_authoring_list_assigned_resource_deployments]
import os
from datetime import date, datetime
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.language.conversations.authoring import ConversationAuthoringClient


def sample_list_assigned_resource_deployments():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]

    credential = DefaultAzureCredential()
    client = ConversationAuthoringClient(endpoint, credential=credential)

    # list assigned resource deployments
    try:
        paged = client.list_assigned_resource_deployments()
        print("Assigned resource deployments retrieved successfully.")

        for meta in paged:
            print(f"\nProject Name: {meta.project_name}")
            for d in meta.deployments_metadata:
                print(f"  Deployment Name: {d.deployment_name}")
                print(f"  Last Deployed On: {d.last_deployed_on}")
                print(f"  Expires On: {d.deployment_expires_on}")
    except HttpResponseError as e:
        print(f"Operation failed: {e.message}")
        print(e.error)


# [END conversation_authoring_list_assigned_resource_deployments]


def main():
    sample_list_assigned_resource_deployments()


if __name__ == "__main__":
    main()
