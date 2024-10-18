# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_agent_team.py

DESCRIPTION:
    This sample demonstrates how to multiple agents using AgentTeam.

USAGE:
    python sample_agents_basics.py

    Before running the sample:

    pip install azure.ai.client azure-identity

    Set this environment variables with your own values:
    AI_CLIENT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os, time
from azure.ai.client import AzureAIClient
from azure.identity import DefaultAzureCredential
from agent_team import AgentTeam

# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

ai_client = AzureAIClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["AI_CLIENT_CONNECTION_STRING"],
)

with ai_client:
    agent_team = AgentTeam()
    agent_team.add_agent(
        model="gpt-4-1106-preview", name="Coder", instructions="You are software engineer who writes great code. Your name is Coder."
    )
    agent_team.add_agent(
        model="gpt-4-1106-preview", name="Reviewer", instructions="You are software engineer who reviews code. Your name is Reviewer."
    )
    agent_team.process_request(ai_client=ai_client, request="Write me a python number guessing game.")
