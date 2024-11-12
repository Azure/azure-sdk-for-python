# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_code_interpreter_attachment_async.py

DESCRIPTION:
    This sample demonstrates how to use agent operations with code interpreter from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_code_interpreter_attachment_async.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""
import asyncio
import os
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool
from azure.ai.projects.models import FilePurpose
from azure.ai.projects.models import MessageAttachment
from azure.identity.aio import DefaultAzureCredential


# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables
async def main():
    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
    )

    async with project_client:
        # upload a file and wait for it to be processed
        file = await project_client.agents.upload_file_and_poll(
            file_path="../product_info_1.md", purpose=FilePurpose.AGENTS
        )
        print(f"Uploaded file, file ID: {file.id}")

        code_interpreter = CodeInterpreterTool()

        # notice that CodeInterpreter must be enabled in the agent creation, otherwise the agent will not be able to see the file attachment
        agent = await project_client.agents.create_agent(
            model="gpt-4-1106-preview",
            name="my-assistant",
            instructions="You are helpful assistant",
            tools=code_interpreter.definitions,
        )
        print(f"Created agent, agent ID: {agent.id}")

        thread = await project_client.agents.create_thread()
        print(f"Created thread, thread ID: {thread.id}")

        # create a message with the attachment
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
