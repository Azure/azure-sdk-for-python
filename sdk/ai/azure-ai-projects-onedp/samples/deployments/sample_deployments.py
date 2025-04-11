# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `.deployments` methods to enumerate AI models deployed to your AI Foundry Project.

USAGE:
    python sample_deployments.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) DEPLOYMENT_NAME - Required. The name of the deployment to retrieve.
    3) MODEL_PUBLISHER - Required. The publisher of the model to filter by.
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects.onedp import AIProjectClient

endpoint = os.environ["PROJECT_ENDPOINT"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]
model_publisher = os.environ["MODEL_PUBLISHER"]

with AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
) as project_client:

    print("List all deployments:")
    for deployment in project_client.deployments.list():
        print(deployment)

    print(f"List all deployments by the model publisher `{model_publisher}`:")
    for deployment in project_client.deployments.list(model_publisher=model_publisher):
        print(deployment)

    print(f"Get a single deployment named `{model_deployment_name}`:")
    deployment = project_client.deployments.get(model_deployment_name)
    print(deployment)
