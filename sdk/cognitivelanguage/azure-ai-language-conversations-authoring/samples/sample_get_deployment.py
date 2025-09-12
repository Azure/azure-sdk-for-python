# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_deployment.py
DESCRIPTION:
    This sample demonstrates how to retrieve details of a deployment in a Conversation Authoring project.
USAGE:
    python sample_get_deployment.py

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
    PROJECT_NAME      # defaults to "<project-name>"
    DEPLOYMENT_NAME   # defaults to "<deployment-name>"
"""

# [START conversation_authoring_get_deployment]
import os
from azure.identity import DefaultAzureCredential
from azure.ai.language.conversations.authoring import ConversationAuthoringClient


def sample_get_deployment():
    # settings
    endpoint = os.environ["AZURE_CONVERSATIONS_AUTHORING_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    deployment_name = os.environ.get("DEPLOYMENT_NAME", "<deployment-name>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = ConversationAuthoringClient(endpoint, credential=credential)
    project_client = client.get_project_client(project_name)

    # get deployment details
    deployment = project_client.deployment.get_deployment(deployment_name=deployment_name)

    print("=== Deployment Details ===")
    print(f"Deployment Name: {deployment.deployment_name}")
    print(f"Model Id: {deployment.model_id}")
    print(f"Last Trained On: {deployment.last_trained_on}")
    print(f"Last Deployed On: {deployment.last_deployed_on}")
    print(f"Deployment Expired On: {deployment.deployment_expired_on}")
    print(f"Model Training Config Version: {deployment.model_training_config_version}")

    # print assigned resources (direct attribute access; no getattr)
    if deployment.assigned_resources:
        for ar in deployment.assigned_resources:
            print(f"Resource ID: {ar.resource_id}")
            print(f"Region: {ar.region}")
            if ar.assigned_aoai_resource:
                aoai = ar.assigned_aoai_resource
                print(f"AOAI Kind: {aoai.kind}")
                print(f"AOAI Resource ID: {aoai.resource_id}")
                print(f"AOAI Deployment Name: {aoai.deployment_name}")


# [END conversation_authoring_get_deployment]


def main():
    sample_get_deployment()


if __name__ == "__main__":
    main()
