# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use multiple assistants to execute tasks.

USAGE:
    python sample_assistants_multi_assistant_team.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity

    Set these environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
    MODEL_DEPLOYMENT_NAME - the name of the model deployment to use.
"""

import os

from user_functions_with_traces import *
from azure.ai.assistants import AssistantsClient
from azure.ai.assistants.models import ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential
from assistant_team import AssistantTeam
from assistant_trace_configurator import AssistantTraceConfigurator

assistants_client = AssistantsClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

user_function_set_1: Set = {fetch_current_datetime, fetch_weather}

user_function_set_2: Set = {send_email_using_recipient_name}

user_function_set_3: Set = {convert_temperature}

model_deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME")

if model_deployment_name is not None:
    AssistantTraceConfigurator(assistants_client=assistants_client).setup_tracing()
    with assistants_client:

        functions = FunctionTool(functions=user_function_set_1)
        toolset1 = ToolSet()
        toolset1.add(functions)

        assistant_team = AssistantTeam("test_team", assistants_client=assistants_client)

        assistant_team.add_assistant(
            model=model_deployment_name,
            name="TimeWeatherAssistant",
            instructions="You are a specialized assistant for time and weather queries.",
            toolset=toolset1,
            can_delegate=True,
        )

        functions = FunctionTool(functions=user_function_set_2)
        toolset2 = ToolSet()
        toolset2.add(functions)

        assistant_team.add_assistant(
            model=model_deployment_name,
            name="SendEmailAssistant",
            instructions="You are a specialized assistant for sending emails.",
            toolset=toolset2,
            can_delegate=False,
        )

        functions = FunctionTool(functions=user_function_set_3)
        toolset3 = ToolSet()
        toolset3.add(functions)

        assistant_team.add_assistant(
            model=model_deployment_name,
            name="TemperatureAssistant",
            instructions="You are a specialized assistant for temperature conversion.",
            toolset=toolset3,
            can_delegate=False,
        )

        assistant_team.assemble_team()

        user_request = (
            "Hello, Please provide me current time in '%Y-%m-%d %H:%M:%S' format, and the weather in New York. "
            "Finally, convert the Celsius to Fahrenheit and send an email to Example Recipient with summary of results."
        )

        # Once process_request is called, the TeamLeader will coordinate.
        # The loop in process_request will pick up tasks from the queue, assign them, and so on.
        assistant_team.process_request(request=user_request)

        assistant_team.dismantle_team()
else:
    print("Error: Please define the environment variable MODEL_DEPLOYMENT_NAME.")
