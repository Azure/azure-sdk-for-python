# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_multi_agent_team.py

DESCRIPTION:
    This sample demonstrates how to use multiple agents to execute tasks.

USAGE:
    python sample_agents_multi_agent_team.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential
from agent_team import AgentTeam
from user_functions import *

# Create an Azure AI Project Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

user_function_set_1 = {
    fetch_current_datetime,
    fetch_weather
}

user_function_set_2 = {
    send_email,
    calculate_sum,
    toggle_flag,
    merge_dicts,
    get_user_info,
    longest_word_in_sentences,
    process_records
}

user_function_set_3 = {
    convert_temperature
}

with project_client:

    functions = FunctionTool(functions=user_function_set_1)
    toolset1 = ToolSet()
    toolset1.add(functions)

    agent_team = AgentTeam()

    agent_team.add_agent(
        model="gpt-4-1106-preview",
        name="TimeWeatherAgent",
        instructions="You are a specialized agent for time and weather queries.",
        toolset=toolset1,
        can_delegate=True
    )

    functions = FunctionTool(functions=user_function_set_2)
    toolset2 = ToolSet()
    toolset2.add(functions)

    agent_team.add_agent(
        model="gpt-4-1106-preview",
        name="SendEmailAgent",
        instructions="You are a specialized agent for sending emails.",
        toolset=toolset2,
        can_delegate=False
    )

    functions = FunctionTool(functions=user_function_set_3)
    toolset3 = ToolSet()
    toolset3.add(functions)

    agent_team.add_agent(
        model="gpt-4-1106-preview",
        name="TemperatureAgent",
        instructions="You are a specialized agent for temperature conversion.",
        toolset=toolset3,
        can_delegate=False
    )

    user_request = (
        "Hello, Please provide me current time in '2023-%m-%d %H:%M:%S' format, and the weather in New York. "
        "Finally, convert the Celsius to Fahrenheit and send an email to me@example.com with summary of results."
    )

    # Once process_request is called, the TeamLeader will coordinate.
    # The loop in process_request will pick up tasks from the queue, assign them, and so on.
    agent_team.process_request(
        project_client=project_client, 
        request=user_request
    )