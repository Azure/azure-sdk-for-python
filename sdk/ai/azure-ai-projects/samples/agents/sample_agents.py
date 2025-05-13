# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to access an authenticated
    AgentsClient from the azure-ai-agents, associated with your AI Foundry project.
    For more information on the azure-ai-agents see https://pypi.org/project/azure-ai-agents.
    Find Agent samples here: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents/samples.

USAGE:
    python sample_agents.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set this environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The AI model deployment name, to be used by your Agent, as found
       in your AI Foundry project.
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

endpoint = os.environ["PROJECT_ENDPOINT"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

    with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

        # [START agents_sample]
        agent = project_client.agents.create_agent(
            model=model_deployment_name,
            name="my-agent",
            instructions="You are helpful agent",
        )
        print(f"Created agent, agent ID: {agent.id}")

        # Do something with your Agent!
        # See samples here https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-agents/samples

        project_client.agents.delete_agent(agent.id)
        print("Deleted agent")
        # [END connection_sample]
