# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to multiple agents using AgentTeam.

USAGE:
    python sample_agents_agent_team.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from agent_team import AgentTeam

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

with project_client:
    agent_team = AgentTeam("test_team", project_client=project_client)
    agent_team.add_agent(
        model="gpt-4-1106-preview",
        name="Coder",
        instructions="You are software engineer who writes great code. Your name is Coder.",
    )
    agent_team.add_agent(
        model="gpt-4-1106-preview",
        name="Reviewer",
        instructions="You are software engineer who reviews code. Your name is Reviewer.",
    )
    agent_team.assemble_team()

    print("A team of agents specialized in software engineering is available for requests.")
    while True:
        user_input = input("Input (type 'quit' to exit): ")
        if user_input.lower() == "quit":
            break
        agent_team.process_request(request=user_input)

    agent_team.dismantle_team()
