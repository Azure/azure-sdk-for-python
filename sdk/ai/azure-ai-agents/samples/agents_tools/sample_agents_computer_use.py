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

import os, time, base64
from typing import List
from azure.ai.agents.models._models import SubmitToolApprovalAction
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    MessageRole,
    RunStepToolCallDetails,
    RunStepComputerUseToolCall,
    ComputerUseTool,
    MessageInputContentBlock,
    MessageImageUrlParam,
    MessageInputTextBlock,
    MessageInputImageUrlBlock,
)
from azure.identity import DefaultAzureCredential

def image_to_base64(image_path: str) -> str:
    """
    Convert an image file to a Base64-encoded string.

    :param image_path: The path to the image file (e.g. 'image_file.png')
    :return: A Base64-encoded string representing the image.
    :raises FileNotFoundError: If the provided file path does not exist.
    :raises OSError: If there's an error reading the file.
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"File not found at: {image_path}")

    try:
        with open(image_path, "rb") as image_file:
            file_data = image_file.read()
        return base64.b64encode(file_data).decode("utf-8")
    except Exception as exc:
        raise OSError(f"Error reading file '{image_path}'") from exc

asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "./cua_screenshot.jpg"))
endpoint = ""
project_client = AIProjectClient(endpoint=endpoint, credential=DefaultAzureCredential())

# Initialize Computer Use tool with a browser-sized viewport
environment = os.environ.get("COMPUTER_USE_ENVIRONMENT", "windows")
computer_use = ComputerUseTool(display_width=1026, display_height=768, environment=environment)

with project_client:

    agents_client = project_client.agents

    # Create a new Agent that has the Computer Use tool attached.
    agent = agents_client.create_agent(
        #model=os.environ["MODEL_DEPLOYMENT_NAME"],
        model="computer-use-preview",
        name="my-agent-computer-use",
        instructions="""
            You are an computer automation assistant. 
            Use the computer_use_preview tool to interact with the screen when needed.
            """,
        tools=computer_use.definitions,
    )


    print(f"Created agent, ID: {agent.id}")

    # Create thread for communication
    thread = agents_client.threads.create()
    print(f"Created thread, ID: {thread.id}")

    input_message = ("I can see a web browser with bing.com open and the cursor in the search box."
                     "Type 'movies near me' without pressing Enter or any other key. Only type 'movies near me'.")
    image_base64 = image_to_base64(asset_file_path)
    img_url = f"data:image/jpeg;base64,{image_base64}"
    url_param = MessageImageUrlParam(url=img_url, detail="high")
    content_blocks: List[MessageInputContentBlock] = [
        MessageInputTextBlock(text=input_message),
        MessageInputImageUrlBlock(image_url=url_param),
    ]
    # Create message to thread
    message = agents_client.messages.create(
        thread_id=thread.id,
        role=MessageRole.USER,
        content=content_blocks
    )
    print(f"Created message, ID: {message.id}")

    run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)
    print(f"Created run, ID: {run.id}")

    while run.status in ["queued", "in_progress", "requires_action"]:
        time.sleep(1)
        run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)

        if run.status == "requires_action":# and isinstance(run.required_action, SubmitToolApprovalAction):
            print("Run requires action:")
            print(run)

        print(f"Current run status: {run.status}")

    print(f"Run completed with status: {run.status}")
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")
    # Create and process agent run in thread with tools
    #print("Waiting for Agent run to complete. Please wait...")
    #run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    #print(f"Run finished with status: {run.status}")


    # Fetch run steps to get the details of the agent run
    run_steps = agents_client.run_steps.list(thread_id=thread.id, run_id=run.id)
    for step in run_steps:
        print(f"Step {step.id} status: {step.status}")
        print(step)

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

