# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use multiple agents using AgentTeam with traces.

USAGE:
    python sample_agents_agent_team.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
    MODEL_DEPLOYMENT_NAME - the name of the model deployment to use.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from agent_team import AgentTeam, _create_task
from agent_trace_configurator import AgentTraceConfigurator

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

model_deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME")

if model_deployment_name is not None:
    AgentTraceConfigurator(project_client=project_client).setup_tracing()
    with project_client:
        project_client.agents.enable_auto_function_calls(functions={_create_task})
        agent_team = AgentTeam("test_team", project_client=project_client)
        agent_team.add_agent(
            model=model_deployment_name,
            name="Coder",
            instructions="You are software engineer who writes great code. Your name is Coder.",
        )
        agent_team.add_agent(
            model=model_deployment_name,
            name="Reviewer",
            instructions="You are software engineer who reviews code. Your name is Reviewer.",
        )
        agent_team.assemble_team()

        print("A team of agents specialized in software engineering is available for requests.")
        while True:
            user_input = input("Input (type 'quit' or 'exit' to exit): ")
            if user_input.lower() == "quit":
                break
            elif user_input.lower() == "exit":
                break
            agent_team.process_request(request=user_input)

        agent_team.dismantle_team()
else:
    print("Error: Please define the environment variable MODEL_DEPLOYMENT_NAME.")
