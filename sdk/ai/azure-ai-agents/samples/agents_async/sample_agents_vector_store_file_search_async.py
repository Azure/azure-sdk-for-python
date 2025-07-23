# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to add files to agent during the vector store creation.

USAGE:
    python sample_agents_vector_store_file_search_async.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model.
"""
import asyncio
import os

from azure.ai.projects.aio import AIProjectClient
from azure.ai.agents.models import (
    FilePurpose,
    FileSearchTool,
    ListSortOrder,
    RunAdditionalFieldList,
    RunStepFileSearchToolCall,
    RunStepToolCallDetails,
)
from azure.identity.aio import DefaultAzureCredential

asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/product_info_1.md"))


async def main():
    project_client = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    async with project_client:
        agents_client = project_client.agents

        # Upload a file and wait for it to be processed
        file = await agents_client.files.upload_and_poll(file_path=asset_file_path, purpose=FilePurpose.AGENTS)
        print(f"Uploaded file, file ID: {file.id}")

        # Create a vector store with no file and wait for it to be processed
        vector_store = await agents_client.vector_stores.create_and_poll(file_ids=[file.id], name="sample_vector_store")
        print(f"Created vector store, vector store ID: {vector_store.id}")

        # Create a file search tool
        file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

        # Notices that FileSearchTool as tool and tool_resources must be added or the agent unable to search the file
        agent = await agents_client.create_agent(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            name="my-agent",
            instructions="You are helpful agent",
            tools=file_search_tool.definitions,
            tool_resources=file_search_tool.resources,
        )
        print(f"Created agent, agent ID: {agent.id}")

        thread = await agents_client.threads.create()
        print(f"Created thread, thread ID: {thread.id}")

        message = await agents_client.messages.create(
            thread_id=thread.id, role="user", content="What feature does Smart Eyewear offer?"
        )
        print(f"Created message, message ID: {message.id}")

        run = await agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
        print(f"Created run, run ID: {run.id}")

        await agents_client.vector_stores.delete(vector_store.id)
        print("Deleted vector store")

        await agents_client.delete_agent(agent.id)
        print("Deleted agent")

        async for run_step in agents_client.run_steps.list(
            thread_id=thread.id, run_id=run.id, include=[RunAdditionalFieldList.FILE_SEARCH_CONTENTS]
        ):
            if isinstance(run_step.step_details, RunStepToolCallDetails):
                for tool_call in run_step.step_details.tool_calls:
                    if (
                        isinstance(tool_call, RunStepFileSearchToolCall)
                        and tool_call.file_search
                        and tool_call.file_search.results
                        and tool_call.file_search.results[0].content
                        and tool_call.file_search.results[0].content[0].text
                    ):
                        print(
                            "The search tool has found the next relevant content in "
                            f"the file {tool_call.file_search.results[0].file_name}:"
                        )
                        # Note: technically we may have several search results, however in our example
                        # we only have one file, so we are taking the only result.
                        print(tool_call.file_search.results[0].content[0].text)
                        print("===============================================================")

        file_name = os.path.split(asset_file_path)[-1]
        messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
        async for msg in messages:
            if msg.text_messages:
                last_text = msg.text_messages[-1].text.value
                for annotation in msg.text_messages[-1].text.annotations:
                    citation = (
                        file_name if annotation.file_citation.file_id == file.id else annotation.file_citation.file_id
                    )
                    last_text = last_text.replace(annotation.text, f" [{citation}]")
                print(f"{msg.role}: {last_text}")


if __name__ == "__main__":
    asyncio.run(main())
