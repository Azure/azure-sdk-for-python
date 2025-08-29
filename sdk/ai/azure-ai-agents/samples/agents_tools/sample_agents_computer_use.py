# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with the Computer Use tool (preview)
    using a synchronous client.

USAGE:
    python sample_agents_computer_use.py

    Before running the sample:

    pip install azure-ai-agents --pre
    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.

    Optional:
    - To target a specific environment, set COMPUTER_USE_ENVIRONMENT to one of: windows, mac, linux, browser
      Otherwise defaults to 'browser'.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    MessageRole,
    RunStepToolCallDetails,
    RunStepComputerUseToolCall,
    ComputerUseTool,
)
from azure.identity import DefaultAzureCredential

project_client = AIProjectClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=DefaultAzureCredential())

# [START create_agent_with_computer_use]
# Initialize Computer Use tool with a browser-sized viewport
environment = os.environ.get("COMPUTER_USE_ENVIRONMENT", "browser")
computer_use = ComputerUseTool(display_width=1280, display_height=800, environment=environment)

with project_client:

    agents_client = project_client.agents

    # Create a new Agent that has the Computer Use tool attached.
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent-computer-use",
        instructions=(
            "You are an Agent helping with computer use tasks. "
            "You can perform actions and browse as needed using the Computer Use tool available to you."
        ),
        tools=computer_use.definitions,
    )

    # [END create_agent_with_computer_use]

    print(f"Created agent, ID: {agent.id}")

    # Create thread for communication
    thread = agents_client.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = agents_client.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=(
            "Open the Microsoft homepage and take a screenshot of the landing page."
        ),
    )
    print(f"Created message, ID: {message.id}")

    # Create and process agent run in thread with tools
    print("Waiting for Agent run to complete. Please wait...")
    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Fetch run steps to get the details of the agent run
    run_steps = agents_client.run_steps.list(thread_id=thread.id, run_id=run.id)
    for step in run_steps:
        print(f"Step {step.id} status: {step.status}")

        if isinstance(step.step_details, RunStepToolCallDetails):
            print("  Tool calls:")
            tool_calls = step.step_details.tool_calls

            for call in tool_calls:
                print(f"    Tool call ID: {call.id}")
                print(f"    Tool call type: {call.type}")

                if isinstance(call, RunStepComputerUseToolCall):
                    details = call.computer_use_preview
                    print(f"    Computer use action type: {details.action.type}")
                    # The output is a ComputerScreenshot, which may include a file_id or image_url
                    print(f"    Screenshot file_id: {call.output.file_id}")
                    print(f"    Screenshot image_url: {call.output.image_url}")

                print()  # extra newline between tool calls

        print()  # extra newline between run steps

    # Optional: Delete the agent once the run is finished.
    agents_client.delete_agent(agent.id)
    print("Deleted agent")

