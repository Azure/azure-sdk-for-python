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
    1) PROJECT_ENDPOINT - the Azure AI Agents endpoint.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""
import asyncio
import os, time
from typing import List
from azure.ai.agents.aio import AgentsClient
from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.models import (
    MessageTextContent,
    MessageInputContentBlock,
    MessageImageUrlParam,
    MessageInputTextBlock,
    MessageInputImageUrlBlock,
)


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

            image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
            input_message = "Hello, what is in the image ?"
            url_param = MessageImageUrlParam(url=image_url, detail="high")
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

            messages = await agents_client.messages.list(thread_id=thread.id)

            # The messages are following in the reverse order,
            # we will iterate them and output only text contents.
            for data_point in reversed(messages.data):
                last_message_content = data_point.content[-1]
                if isinstance(last_message_content, MessageTextContent):
                    print(f"{data_point.role}: {last_message_content.text.value}")

            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
