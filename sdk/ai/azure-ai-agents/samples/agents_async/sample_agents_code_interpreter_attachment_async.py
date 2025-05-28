# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with code interpreter from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_code_interpreter_attachment_async.py

    Before running the sample:

    pip install azure-ai-agents azure-identity aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""
import asyncio
import os
from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import (
    CodeInterpreterTool,
    FilePurpose,
    MessageAttachment,
    ListSortOrder,
    MessageTextContent,
)
from azure.identity.aio import DefaultAzureCredential

asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/product_info_1.md"))


async def main():
    async with DefaultAzureCredential() as creds:
        async with AgentsClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=creds) as agents_client:
            # Upload a file and wait for it to be processed
            file = await agents_client.files.upload_and_poll(file_path=asset_file_path, purpose=FilePurpose.AGENTS)
            print(f"Uploaded file, file ID: {file.id}")

            code_interpreter = CodeInterpreterTool()

            # Notice that CodeInterpreter must be enabled in the agent creation, otherwise the agent will not be able to see the file attachment
            agent = await agents_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-agent",
                instructions="You are helpful agent",
                tools=code_interpreter.definitions,
            )
            print(f"Created agent, agent ID: {agent.id}")

            thread = await agents_client.threads.create()
            print(f"Created thread, thread ID: {thread.id}")

            # Create a message with the attachment
            attachment = MessageAttachment(file_id=file.id, tools=code_interpreter.definitions)
            message = await agents_client.messages.create(
                thread_id=thread.id, role="user", content="What does the attachment say?", attachments=[attachment]
            )
            print(f"Created message, message ID: {message.id}")

            run = await agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
            print(f"Run finished with status: {run.status}")

            if run.status == "failed":
                # Check if you got "Rate limit is exceeded.", then you want to get more quota
                print(f"Run failed: {run.last_error}")

            await agents_client.files.delete(file.id)
            print("Deleted file")

            await agents_client.delete_agent(agent.id)
            print("Deleted agent")

            messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            async for msg in messages:
                last_part = msg.content[-1]
                if isinstance(last_part, MessageTextContent):
                    print(f"{msg.role}: {last_part.text.value}")


if __name__ == "__main__":
    asyncio.run(main())
