# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_deployment.py
DESCRIPTION:
    This sample demonstrates how to get a **Text Authoring** deployment and print its details.
USAGE:
    python sample_get_deployment.py
REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_TEXT_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET
NOTE:
    If you want to use AzureKeyCredential instead, set:
      - AZURE_TEXT_ENDPOINT
      - AZURE_TEXT_KEY
OPTIONAL ENV VARS:
    PROJECT_NAME     # defaults to "<project-name>"
    DEPLOYMENT_NAME  # defaults to "<deployment-name>"
"""

# [START text_authoring_get_deployment]
import os
from azure.identity import DefaultAzureCredential
from azure.ai.textanalytics.authoring import TextAuthoringClient


def sample_get_deployment():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    deployment_name = os.environ.get("DEPLOYMENT_NAME", "<deployment-name>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    client = TextAuthoringClient(endpoint, credential=credential)

    # project-scoped client
    project_client = client.get_project_client(project_name)

    # get deployment
    deployment = project_client.deployment.get_deployment(deployment_name=deployment_name)

    # print deployment details (direct attribute access; no getattr)
    print("=== Deployment Details ===")
    print(f"Deployment Name: {deployment.deployment_name}")
    print(f"Model Id: {deployment.model_id}")
    print(f"Last Trained On: {deployment.last_trained_on}")
    print(f"Last Deployed On: {deployment.last_deployed_on}")
    print(f"Deployment Expired On: {deployment.deployment_expired_on}")
    print(f"Model Training Config Version: {deployment.model_training_config_version}")

    # Assigned resources (if any)
    if deployment.assigned_resources:
        print("Assigned Resources:")
        for resource in deployment.assigned_resources:
            print(f"  Resource ID: {resource.resource_id}")
            print(f"  Region: {resource.region}")


# [END text_authoring_get_deployment]


def main():
    sample_get_deployment()


if __name__ == "__main__":
    main()
