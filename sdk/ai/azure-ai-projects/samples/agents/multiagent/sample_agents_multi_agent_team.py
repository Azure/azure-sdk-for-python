# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use multiple agents to execute tasks.

USAGE:
    python sample_agents_multi_agent_team.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
    MODEL_DEPLOYMENT_NAME - the name of the model deployment to use.
"""

import os

from typing import Set
from user_functions_with_traces import *
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential
from agent_team import AgentTeam
from agent_trace_configurator import AgentTraceConfigurator

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

user_function_set_1: Set = {fetch_current_datetime, fetch_weather}

user_function_set_2: Set = {send_email_using_recipient_name}

user_function_set_3: Set = {convert_temperature}

model_deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME")

project_client.agents.enable_auto_function_calls(
    function_tool=FunctionTool(
        {fetch_current_datetime, fetch_weather, send_email_using_recipient_name, convert_temperature}
    )
)

if model_deployment_name is not None:
    AgentTraceConfigurator(project_client=project_client).setup_tracing()
    with project_client:

        functions = FunctionTool(functions=user_function_set_1)
        toolset1 = ToolSet()
        toolset1.add(functions)

        agent_team = AgentTeam("test_team", project_client=project_client)

        agent_team.add_agent(
            model=model_deployment_name,
            name="TimeWeatherAgent",
            instructions="You are a specialized agent for time and weather queries.",
            toolset=toolset1,
            can_delegate=True,
        )

        functions = FunctionTool(functions=user_function_set_2)
        toolset2 = ToolSet()
        toolset2.add(functions)

        agent_team.add_agent(
            model=model_deployment_name,
            name="SendEmailAgent",
            instructions="You are a specialized agent for sending emails.",
            toolset=toolset2,
            can_delegate=False,
        )

        functions = FunctionTool(functions=user_function_set_3)
        toolset3 = ToolSet()
        toolset3.add(functions)

        agent_team.add_agent(
            model=model_deployment_name,
            name="TemperatureAgent",
            instructions="You are a specialized agent for temperature conversion.",
            toolset=toolset3,
            can_delegate=False,
        )

        agent_team.assemble_team()

        user_request = (
            "Hello, Please provide me current time in '%Y-%m-%d %H:%M:%S' format, and the weather in New York. "
            "Finally, convert the Celsius to Fahrenheit and send an email to Example Recipient with summary of results."
        )

        # Once process_request is called, the TeamLeader will coordinate.
        # The loop in process_request will pick up tasks from the queue, assign them, and so on.
        agent_team.process_request(request=user_request)

        agent_team.dismantle_team()
else:
    print("Error: Please define the environment variable MODEL_DEPLOYMENT_NAME.")
