# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use basic agent operations using image url input for the
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_image_input_url.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os, time
from typing import List
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    MessageTextContent,
    MessageInputContentBlock,
    MessageImageUrlParam,
    MessageInputTextBlock,
    MessageInputImageUrlBlock,
)


agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with agents_client:

    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are helpful agent",
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = agents_client.threads.create()
    print(f"Created thread, thread ID: {thread.id}")

    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    input_message = "Hello, what is in the image ?"
    url_param = MessageImageUrlParam(url=image_url, detail="high")
    content_blocks: List[MessageInputContentBlock] = [
        MessageInputTextBlock(text=input_message),
        MessageInputImageUrlBlock(image_url=url_param),
    ]
    message = agents_client.messages.create(thread_id=thread.id, role="user", content=content_blocks)
    print(f"Created message, message ID: {message.id}")

    run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)

    # Poll the run as long as run status is queued or in progress
    while run.status in ["queued", "in_progress", "requires_action"]:
        # Wait for a second
        time.sleep(1)
        run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)
        print(f"Run status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    messages = agents_client.messages.list(thread_id=thread.id)

    # The messages are following in the reverse order,
    # we will iterate them and output only text contents.
    for msg in messages:
        last_part = msg.content[-1]
        if isinstance(last_part, MessageTextContent):
            print(f"{msg.role}: {last_part.text.value}")

    print(f"Messages: {messages}")
