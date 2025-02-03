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

    pip install azure-ai-projects azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""
import asyncio
import os
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool
from azure.ai.projects.models import FilePurpose
from azure.ai.projects.models import MessageAttachment
from azure.identity.aio import DefaultAzureCredential


async def main():
    async with DefaultAzureCredential() as creds:
        async with AIProjectClient.from_connection_string(
            credential=creds, conn_str=os.environ["PROJECT_CONNECTION_STRING"]
        ) as project_client:
            # Upload a file and wait for it to be processed
            file = await project_client.agents.upload_file_and_poll(
                file_path="../product_info_1.md", purpose=FilePurpose.AGENTS
            )
            print(f"Uploaded file, file ID: {file.id}")

            code_interpreter = CodeInterpreterTool()

            # Notice that CodeInterpreter must be enabled in the agent creation, otherwise the agent will not be able to see the file attachment
            agent = await project_client.agents.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-assistant",
                instructions="You are helpful assistant",
                tools=code_interpreter.definitions,
            )
            print(f"Created agent, agent ID: {agent.id}")

            thread = await project_client.agents.create_thread()
            print(f"Created thread, thread ID: {thread.id}")

            # Create a message with the attachment
            attachment = MessageAttachment(file_id=file.id, tools=code_interpreter.definitions)
            message = await project_client.agents.create_message(
                thread_id=thread.id, role="user", content="What does the attachment say?", attachments=[attachment]
            )
            print(f"Created message, message ID: {message.id}")

            run = await project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
            print(f"Run finished with status: {run.status}")

            if run.status == "failed":
                # Check if you got "Rate limit is exceeded.", then you want to get more quota
                print(f"Run failed: {run.last_error}")

            await project_client.agents.delete_file(file.id)
            print("Deleted file")

            await project_client.agents.delete_agent(agent.id)
            print("Deleted agent")

            messages = await project_client.agents.list_messages(thread_id=thread.id)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
