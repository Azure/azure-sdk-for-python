# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use multiple assistants using AssistantTeam with traces.

USAGE:
    python sample_assistants_assistant_team.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity

    Set these environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
    MODEL_DEPLOYMENT_NAME - the name of the model deployment to use.
"""

import os
from azure.ai.assistants import AssistantsClient
from azure.identity import DefaultAzureCredential
from assistant_team import AssistantTeam
from assistant_trace_configurator import AssistantTraceConfigurator

assistants_client = AssistantsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

model_deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME")

if model_deployment_name is not None:
    AssistantTraceConfigurator(assistants_client=assistants_client).setup_tracing()
    with assistants_client:
        assistant_team = AssistantTeam("test_team", assistants_client=assistants_client)
        assistant_team.add_assistant(
            model=model_deployment_name,
            name="Coder",
            instructions="You are software engineer who writes great code. Your name is Coder.",
        )
        assistant_team.add_assistant(
            model=model_deployment_name,
            name="Reviewer",
            instructions="You are software engineer who reviews code. Your name is Reviewer.",
        )
        assistant_team.assemble_team()

        print("A team of assistants specialized in software engineering is available for requests.")
        while True:
            user_input = input("Input (type 'quit' or 'exit' to exit): ")
            if user_input.lower() == "quit":
                break
            elif user_input.lower() == "exit":
                break
            assistant_team.process_request(request=user_input)

        assistant_team.dismantle_team()
else:
    print("Error: Please define the environment variable MODEL_DEPLOYMENT_NAME.")
