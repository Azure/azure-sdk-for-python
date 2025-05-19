# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to multiple agents using AgentTeam with traces.

USAGE:
    python sample_agents_agent_team_custom_team_leader.py

    Before running the sample:

    pip install azure-ai-agents azure-identity

    Set these environment variables with your own values:
    PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                       page of your Azure AI Foundry portal.
    MODEL_DEPLOYMENT_NAME - the name of the model deployment to use.
"""

import os
from typing import Optional, Set
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
from utils.agent_team import AgentTeam, AgentTask
from utils.agent_trace_configurator import AgentTraceConfigurator
from azure.ai.agents.models import FunctionTool, ToolSet

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

model_deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME")


def create_task(team_name: str, recipient: str, request: str, requestor: str) -> str:
    """
    Requests another agent in the team to complete a task.

    :param team_name (str): The name of the team.
    :param recipient (str): The name of the agent that is being requested to complete the task.
    :param request (str): A description of the to complete. This can also be a question.
    :param requestor (str): The name of the agent who is requesting the task.
    :return: True if the task was successfully received, False otherwise.
    :rtype: str
    """
    task = AgentTask(recipient=recipient, task_description=request, requestor=requestor)
    team: Optional[AgentTeam] = None
    try:
        team = AgentTeam.get_team(team_name)
    except:
        pass
    if team is not None:
        team.add_task(task)
        return "True"
    return "False"


# Any additional functions that might be used by the agents:
agent_team_default_functions: Set = {
    create_task,
}

default_function_tool = FunctionTool(functions=agent_team_default_functions)

agents_client.enable_auto_function_calls({create_task})

if model_deployment_name is not None:
    AgentTraceConfigurator(agents_client=agents_client).setup_tracing()
    with agents_client:
        agent_team = AgentTeam("test_team", agents_client=agents_client)
        toolset = ToolSet()
        toolset.add(default_function_tool)
        agent_team.set_team_leader(
            model=model_deployment_name,
            name="TeamLeader",
            instructions="You are an agent named 'TeamLeader'. You are a leader of a team of agents. The name of your team is 'test_team'."
            "You are an agent that is responsible for receiving requests from user and utilizing a team of agents to complete the task. "
            "When you are passed a request, the only thing you will do is evaluate which team member should do which task next to complete the request. "
            "You will use the provided create_task function to create a task for the agent that is best suited for handling the task next. "
            "You will respond with the description of who you assigned the task and why. When you think that the original user request is "
            "processed completely utilizing all the talent available in the team, you do not have to create anymore tasks. "
            "Using the skills of all the team members when applicable is highly valued. "
            "Do not create parallel tasks. "
            "Here are the other agents in your team: "
            "- Coder: You are software engineer who writes great code. Your name is Coder. "
            "- Reviewer: You are software engineer who reviews code. Your name is Reviewer.",
            toolset=toolset,
        )
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
