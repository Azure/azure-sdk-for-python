# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to multiple assistants using AssistantTeam with traces.

USAGE:
    python sample_assistants_assistant_team_custom_team_leader.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity

    Set these environment variables with your own values:
    PROJECT_ENDPOINT - the Azure AI Assistants endpoint.
    MODEL_DEPLOYMENT_NAME - the name of the model deployment to use.
"""

import os
from typing import Optional, Set
from azure.ai.assistants import AssistantsClient
from azure.identity import DefaultAzureCredential
from assistant_team import AssistantTeam, AssistantTask
from assistant_trace_configurator import AssistantTraceConfigurator
from azure.ai.assistants.models import FunctionTool, ToolSet

assistants_client = AssistantsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

model_deployment_name = os.getenv("MODEL_DEPLOYMENT_NAME")


def create_task(team_name: str, recipient: str, request: str, requestor: str) -> str:
    """
    Requests another assistant in the team to complete a task.

    :param team_name (str): The name of the team.
    :param recipient (str): The name of the assistant that is being requested to complete the task.
    :param request (str): A description of the to complete. This can also be a question.
    :param requestor (str): The name of the assistant who is requesting the task.
    :return: True if the task was successfully received, False otherwise.
    :rtype: str
    """
    task = AssistantTask(recipient=recipient, task_description=request, requestor=requestor)
    team: Optional[AssistantTeam] = None
    try:
        team = AssistantTeam.get_team(team_name)
    except:
        pass
    if team is not None:
        team.add_task(task)
        return "True"
    return "False"


# Any additional functions that might be used by the assistants:
assistant_team_default_functions: Set = {
    create_task,
}

default_function_tool = FunctionTool(functions=assistant_team_default_functions)


if model_deployment_name is not None:
    AssistantTraceConfigurator(assistants_client=assistants_client).setup_tracing()
    with assistants_client:
        assistant_team = AssistantTeam("test_team", assistants_client=assistants_client)
        toolset = ToolSet()
        toolset.add(default_function_tool)
        assistant_team.set_team_leader(
            model=model_deployment_name,
            name="TeamLeader",
            instructions="You are an assistant named 'TeamLeader'. You are a leader of a team of assistants. The name of your team is 'test_team'."
            "You are an assistant that is responsible for receiving requests from user and utilizing a team of assistants to complete the task. "
            "When you are passed a request, the only thing you will do is evaluate which team member should do which task next to complete the request. "
            "You will use the provided create_task function to create a task for the assistant that is best suited for handling the task next. "
            "You will respond with the description of who you assigned the task and why. When you think that the original user request is "
            "processed completely utilizing all the talent available in the team, you do not have to create anymore tasks. "
            "Using the skills of all the team members when applicable is highly valued. "
            "Do not create parallel tasks. "
            "Here are the other assistants in your team: "
            "- Coder: You are software engineer who writes great code. Your name is Coder. "
            "- Reviewer: You are software engineer who reviews code. Your name is Reviewer.",
            toolset=toolset,
        )
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
