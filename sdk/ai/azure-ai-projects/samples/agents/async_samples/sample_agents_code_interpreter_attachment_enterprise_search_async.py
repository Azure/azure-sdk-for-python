# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with code interpreter from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_code_interpreter_attachment_enterprise_search_async.py

    Before running the sample:

    pip install azure-ai-projects azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""
import asyncio
import os
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    CodeInterpreterTool,
    MessageAttachment,
    VectorStoreDataSource,
    VectorStoreDataSourceAssetType,
)
from azure.identity.aio import DefaultAzureCredential


async def main():
    async with DefaultAzureCredential() as credential:
        async with AIProjectClient.from_connection_string(
            credential=credential, conn_str=os.environ["PROJECT_CONNECTION_STRING"]
        ) as project_client:

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

            # We will upload the local file to Azure and will use it for vector store creation.
            _, asset_uri = project_client.upload_file("../product_info_1.md")
            ds = VectorStoreDataSource(asset_identifier=asset_uri, asset_type=VectorStoreDataSourceAssetType.URI_ASSET)

            # Create a message with the attachment
            attachment = MessageAttachment(data_source=ds, tools=code_interpreter.definitions)
            message = await project_client.agents.create_message(
                thread_id=thread.id, role="user", content="What does the attachment say?", attachments=[attachment]
            )
            print(f"Created message, message ID: {message.id}")

            run = await project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
            print(f"Run finished with status: {run.status}")

            if run.status == "failed":
                # Check if you got "Rate limit is exceeded.", then you want to get more quota
                print(f"Run failed: {run.last_error}")

            await project_client.agents.delete_agent(agent.id)
            print("Deleted agent")

            messages = await project_client.agents.list_messages(thread_id=thread.id)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
