# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic agent operations using image file input for the
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_image_input_base64.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os, time, base64
from typing import List
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import (
    MessageTextContent,
    MessageInputContentBlock,
    MessageImageUrlParam,
    MessageInputTextBlock,
    MessageInputImageUrlBlock,
)


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


project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

with project_client:

    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are helpful assistant",
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    input_message = "Hello, what is in the image ?"
    image_base64 = image_to_base64("image_file.png")
    img_url = f"data:image/png;base64,{image_base64}"
    url_param = MessageImageUrlParam(url=img_url, detail="high")
    content_blocks: List[MessageInputContentBlock] = [
        MessageInputTextBlock(text=input_message),
        MessageInputImageUrlBlock(image_url=url_param),
    ]
    message = project_client.agents.create_message(thread_id=thread.id, role="user", content=content_blocks)
    print(f"Created message, message ID: {message.id}")

    run = project_client.agents.create_run(thread_id=thread.id, agent_id=agent.id)

    # Poll the run as long as run status is queued or in progress
    while run.status in ["queued", "in_progress", "requires_action"]:
        # Wait for a second
        time.sleep(1)
        run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
        print(f"Run status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    messages = project_client.agents.list_messages(thread_id=thread.id)

    # The messages are following in the reverse order,
    # we will iterate them and output only text contents.
    for data_point in reversed(messages.data):
        last_message_content = data_point.content[-1]
        if isinstance(last_message_content, MessageTextContent):
            print(f"{data_point.role}: {last_message_content.text.value}")

    print(f"Messages: {messages}")
