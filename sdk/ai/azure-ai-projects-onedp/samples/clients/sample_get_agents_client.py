# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    AgentsClient from the azure.ai.agents package. For more information on 
    the azure.ai.agents package see https://pypi.org/project/azure-ai-agents/.

USAGE:
    python sample_get_agents_client.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity

    Set this environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects.onedp import AIProjectClient

endpoint = os.environ["PROJECT_ENDPOINT"]

with AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(exclude_interactive_browser_credential=False),
) as project_client:

    # [START agents_sample]
    with project_client.clients.get_agents_client() as client:
        # TODO: Do something with the agents client...
        pass
    # [END sample]
