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
    python sample_agents_code_interpreter_attachment_enterprise_search_async.py

    Before running the sample:

    pip install azure-ai-agents azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_ENDPOINT - the Azure AI Agents endpoint.
"""
import asyncio
import os
from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import (
    CodeInterpreterTool,
    ListSortOrder,
    MessageAttachment,
    VectorStoreDataSource,
    VectorStoreDataSourceAssetType,
)
from azure.identity.aio import DefaultAzureCredential


async def main():
    async with DefaultAzureCredential() as credential:
        async with AgentsClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=credential) as agents_client:

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

            # We will upload the local file to Azure and will use it for vector store creation.
            asset_uri = os.environ["AZURE_BLOB_URI"]
            ds = VectorStoreDataSource(asset_identifier=asset_uri, asset_type=VectorStoreDataSourceAssetType.URI_ASSET)

            # Create a message with the attachment
            attachment = MessageAttachment(data_source=ds, tools=code_interpreter.definitions)
            message = await agents_client.messages.create(
                thread_id=thread.id, role="user", content="What does the attachment say?", attachments=[attachment]
            )
            print(f"Created message, message ID: {message.id}")

            run = await agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
            print(f"Run finished with status: {run.status}")

            if run.status == "failed":
                # Check if you got "Rate limit is exceeded.", then you want to get more quota
                print(f"Run failed: {run.last_error}")

            await agents_client.delete_agent(agent.id)
            print("Deleted agent")

            messages = await agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
