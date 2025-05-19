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
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""
import asyncio
import os, time, base64
from typing import List
from azure.ai.agents.aio import AgentsClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.models import (
    ListSortOrder,
    MessageTextContent,
    MessageInputContentBlock,
    MessageImageUrlParam,
    MessageInputTextBlock,
    MessageInputImageUrlBlock,
)

asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/image_file.png"))


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


async def main():
    async with DefaultAzureCredential() as creds:
        async with AgentsClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=creds) as agents_client:

            agent = await agents_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-agent",
                instructions="You are helpful agent",
            )
            print(f"Created agent, agent ID: {agent.id}")

            thread = await agents_client.threads.create()
            print(f"Created thread, thread ID: {thread.id}")

            input_message = "Hello, what is in the image ?"
            image_base64 = image_to_base64(asset_file_path)
            img_url = f"data:image/png;base64,{image_base64}"
            url_param = MessageImageUrlParam(url=img_url, detail="high")
            content_blocks: List[MessageInputContentBlock] = [
                MessageInputTextBlock(text=input_message),
                MessageInputImageUrlBlock(image_url=url_param),
            ]
            message = await agents_client.messages.create(thread_id=thread.id, role="user", content=content_blocks)
            print(f"Created message, message ID: {message.id}")

            run = await agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)

            # Poll the run as long as run status is queued or in progress
            while run.status in ["queued", "in_progress", "requires_action"]:
                # Wait for a second
                time.sleep(1)
                run = await agents_client.runs.get(thread_id=thread.id, run_id=run.id)
                print(f"Run status: {run.status}")

            if run.status == "failed":
                print(f"Run failed: {run.last_error}")

            await agents_client.delete_agent(agent.id)
            print("Deleted agent")

            messages = agents_client.messages.list(
                thread_id=thread.id,
                order=ListSortOrder.ASCENDING,
            )

            async for msg in messages:
                last_part = msg.content[-1]
                if isinstance(last_part, MessageTextContent):
                    print(f"{msg.role}: {last_part.text.value}")


if __name__ == "__main__":
    asyncio.run(main())
