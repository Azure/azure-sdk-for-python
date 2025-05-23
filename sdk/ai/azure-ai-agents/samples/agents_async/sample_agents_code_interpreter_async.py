# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use code interpreter tool with agent from
    the Azure Agents service using a asynchronous client.

USAGE:
    python sample_agents_code_interpreter_async.py

    Before running the sample:

    pip install azure-ai-agents azure-identity aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""
import asyncio

from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import CodeInterpreterTool, FilePurpose, ListSortOrder, MessageRole
from azure.identity.aio import DefaultAzureCredential
from pathlib import Path

import os

asset_file_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../assets/synthetic_500_quarterly_results.csv")
)


async def main() -> None:

    async with DefaultAzureCredential() as creds:

        async with AgentsClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=creds) as agents_client:
            # Upload a file and wait for it to be processed
            file = await agents_client.files.upload_and_poll(file_path=asset_file_path, purpose=FilePurpose.AGENTS)
            print(f"Uploaded file, file ID: {file.id}")

            code_interpreter = CodeInterpreterTool(file_ids=[file.id])

            agent = await agents_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-agent",
                instructions="You are helpful agent",
                tools=code_interpreter.definitions,
                tool_resources=code_interpreter.resources,
            )
            print(f"Created agent, agent ID: {agent.id}")

            thread = await agents_client.threads.create()
            print(f"Created thread, thread ID: {thread.id}")

            message = await agents_client.messages.create(
                thread_id=thread.id,
                role="user",
                content="Could you please create bar chart in TRANSPORTATION sector for the operating profit from the uploaded csv file and provide file to me?",
            )
            print(f"Created message, message ID: {message.id}")

            run = await agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
            print(f"Run finished with status: {run.status}")

            if run.status == "failed":
                # Check if you got "Rate limit is exceeded.", then you want to get more quota
                print(f"Run failed: {run.last_error}")

            messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)

            last_msg = await agents_client.messages.get_last_message_text_by_role(
                thread_id=thread.id, role=MessageRole.AGENT
            )
            if last_msg:
                print(f"Last Message: {last_msg.text.value}")

            async for msg in messages:
                # Save every image file in the message
                for img in msg.image_contents:
                    file_id = img.image_file.file_id
                    file_name = f"{file_id}_image_file.png"
                    await agents_client.files.save(file_id=file_id, file_name=file_name)
                    print(f"Saved image file to: {Path.cwd() / file_name}")

                # Print details of every file-path annotation
                for ann in msg.file_path_annotations:
                    print("File Paths:")
                    print(f"  Type: {ann.type}")
                    print(f"  Text: {ann.text}")
                    print(f"  File ID: {ann.file_path.file_id}")
                    print(f"  Start Index: {ann.start_index}")
                    print(f"  End Index: {ann.end_index}")

            await agents_client.delete_agent(agent.id)
            print("Deleted agent")


if __name__ == "__main__":
    asyncio.run(main())
