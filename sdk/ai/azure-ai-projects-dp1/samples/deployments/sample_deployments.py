
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
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects.dp1 import AIProjectClient

endpoint = os.environ["PROJECT_ENDPOINT"]

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

print("Get a single deployment by its name:")
deployment = project_client.deployments.get("gpt-4o-mini")
print(deployment)

print("List all deployments:")
for deployment in project_client.deployments.list():
    print(deployment)

print("List all deployments by publisher `OpenAI`:")
for deployment in project_client.deployments.list(model_publisher="OpenAI"):
    print(deployment)