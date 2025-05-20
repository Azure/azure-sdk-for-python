# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use an AgentTeam to execute a multi-step
    user request with automatic function calling and trace collection.

    The team consists of
        • one leader agent - created automatically from the configuration in
          `utils/agent_team_config.yaml`
        • three worker agents - `TimeWeatherAgent`, `SendEmailAgent`, and
          `TemperatureAgent`, each defined in the code below with its own tools

    IMPORTANT - leader-agent model configuration
        `utils/agent_team_config.yaml` contains the key TEAM_LEADER_MODEL.
        Its value must be the name of a **deployed** model in your Azure AI
        project (e.g. "gpt-4o-mini").
        If this deployment does not exist, AgentTeam cannot instantiate the
        leader agent and the sample will fail.

USAGE:
    python sample_agents_multi_agent_team.py

    Before running the sample:

    1. pip install azure-ai-agents azure-identity
    2. Ensure `utils/agent_team_config.yaml` is present and TEAM_LEADER_MODEL points
       to a valid model deployment.
    3. Set these environment variables with your own values:
         PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                            page of your Azure AI Foundry portal.
         MODEL_DEPLOYMENT_NAME - The model deployment name used for the worker agents.
"""

import os
from typing import Set

from utils.user_functions_with_traces import (
    fetch_current_datetime,
    fetch_weather,
    send_email_using_recipient_name,
    convert_temperature,
)

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import ToolSet, FunctionTool
from azure.identity import DefaultAzureCredential
from utils.agent_team import AgentTeam, _create_task
from utils.agent_trace_configurator import AgentTraceConfigurator

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

user_function_set_1: Set = {fetch_current_datetime, fetch_weather}

user_function_set_2: Set = {send_email_using_recipient_name}

user_function_set_3: Set = {convert_temperature}

agents_client.enable_auto_function_calls(
    {
        _create_task,
        fetch_current_datetime,
        fetch_weather,
        send_email_using_recipient_name,
        convert_temperature,
    }
)

model_deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME")

if model_deployment_name is not None:
    AgentTraceConfigurator(agents_client=agents_client).setup_tracing()
    with agents_client:

        functions = FunctionTool(functions=user_function_set_1)
        toolset1 = ToolSet()
        toolset1.add(functions)

        agent_team = AgentTeam("test_team", agents_client=agents_client)

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
