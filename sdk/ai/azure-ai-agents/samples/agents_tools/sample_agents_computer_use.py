# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with the Computer Use tool (preview)
    using a synchronous client. This sample uses fake screenshot to demonstrate how output actions work,
    but the actual implementation would involve mapping the output action types to their corresponding
    API calls in the user's preferred managed environment framework (e.g. Playwright or Docker).

    NOTE: Usage of the computer-use-preview model currently requires approval. Please see
    https://learn.microsoft.com/azure/ai-foundry/openai/how-to/computer-use for more information.

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
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    ComputerScreenshot,
    TypeAction,
    MessageRole,
    RunStepToolCallDetails,
    RunStepComputerUseToolCall,
    ComputerUseTool,
    ComputerToolOutput,
    MessageInputContentBlock,
    MessageImageUrlParam,
    MessageInputTextBlock,
    MessageInputImageUrlBlock,
    RequiredComputerUseToolCall,
    ScreenshotAction,
    SubmitToolOutputsAction,
    ListSortOrder,
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


asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/cua_screenshot.jpg"))
action_result_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/cua_screenshot_next.jpg"))
project_client = AIProjectClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=DefaultAzureCredential())

# Initialize Computer Use tool with a browser-sized viewport
environment = os.environ.get("COMPUTER_USE_ENVIRONMENT", "windows")
computer_use = ComputerUseTool(display_width=1026, display_height=769, environment=environment)

with project_client:

    agents_client = project_client.agents

    # Create a new Agent that has the Computer Use tool attached.
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
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

    input_message = (
        "I can see a web browser with bing.com open and the cursor in the search box."
        "Type 'movies near me' without pressing Enter or any other key. Only type 'movies near me'."
    )
    image_base64 = image_to_base64(asset_file_path)
    img_url = f"data:image/jpeg;base64,{image_base64}"
    url_param = MessageImageUrlParam(url=img_url, detail="high")
    content_blocks: List[MessageInputContentBlock] = [
        MessageInputTextBlock(text=input_message),
        MessageInputImageUrlBlock(image_url=url_param),
    ]
    # Create message to thread
    message = agents_client.messages.create(thread_id=thread.id, role=MessageRole.USER, content=content_blocks)
    print(f"Created message, ID: {message.id}")

    run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)
    print(f"Created run, ID: {run.id}")

    # create a fake screenshot showing the text typed in
    result_image_base64 = image_to_base64(action_result_file_path)
    result_img_url = f"data:image/jpeg;base64,{result_image_base64}"
    computer_screenshot = ComputerScreenshot(image_url=result_img_url)

    while run.status in ["queued", "in_progress", "requires_action"]:
        time.sleep(1)
        run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)

        if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
            print("Run requires action:")
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            if not tool_calls:
                print("No tool calls provided - cancelling run")
                agents_client.runs.cancel(thread_id=thread.id, run_id=run.id)
                break

            tool_outputs = []
            for tool_call in tool_calls:
                if isinstance(tool_call, RequiredComputerUseToolCall):
                    print(tool_call)
                    try:
                        action = tool_call.computer_use_preview.action
                        print(f"Executing computer use action: {action.type}")
                        if isinstance(action, TypeAction):
                            print(f"  Text to type: {action.text}")
                            # (add hook to input text in managed environment API here)

                            tool_outputs.append(
                                ComputerToolOutput(tool_call_id=tool_call.id, output=computer_screenshot)
                            )
                        if isinstance(action, ScreenshotAction):
                            print(f"  Screenshot requested")
                            # (add hook to take screenshot in managed environment API here)

                            tool_outputs.append(
                                ComputerToolOutput(tool_call_id=tool_call.id, output=computer_screenshot)
                            )
                    except Exception as e:
                        print(f"Error executing tool_call {tool_call.id}: {e}")

            print(f"Tool outputs: {tool_outputs}")
            if tool_outputs:
                agents_client.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs)

        print(f"Current run status: {run.status}")

    print(f"Run completed with status: {run.status}")
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Fetch run steps to get the details of the agent run
    run_steps = agents_client.run_steps.list(thread_id=thread.id, run_id=run.id)
    for step in run_steps:
        print(f"Step {step.id} status: {step.status}")
        print(step)

        if isinstance(step.step_details, RunStepToolCallDetails):
            print("  Tool calls:")
            run_step_tool_calls = step.step_details.tool_calls

            for call in run_step_tool_calls:
                print(f"    Tool call ID: {call.id}")
                print(f"    Tool call type: {call.type}")

                if isinstance(call, RunStepComputerUseToolCall):
                    details = call.computer_use_preview
                    print(f"    Computer use action type: {details.action.type}")

                print()  # extra newline between tool calls

        print()  # extra newline between run steps

    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")

    # Optional: Delete the agent once the run is finished.
    agents_client.delete_agent(agent.id)
    print("Deleted agent")
