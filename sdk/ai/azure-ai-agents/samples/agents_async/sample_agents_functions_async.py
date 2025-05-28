# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_functions_async.py

DESCRIPTION:
    This sample demonstrates how to use agent operations with custom functions from
    the Azure Agents service using a asynchronous client.

USAGE:
    python sample_agents_functions_async.py

    Before running the sample:

    pip install azure-ai-agents azure-identity aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""
import asyncio
import time
import os
from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import (
    AsyncFunctionTool,
    RequiredFunctionToolCall,
    SubmitToolOutputsAction,
    ToolOutput,
    ListSortOrder,
    MessageTextContent,
)
from azure.identity.aio import DefaultAzureCredential
from utils.user_async_functions import user_async_functions


async def main() -> None:
    async with DefaultAzureCredential() as creds:
        async with AgentsClient(endpoint=os.environ["PROJECT_ENDPOINT"], credential=creds) as agents_client:
            # Initialize agent functions
            functions = AsyncFunctionTool(functions=user_async_functions)

            # Create agent
            agent = await agents_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-agent",
                instructions="You are helpful agent",
                tools=functions.definitions,
            )
            print(f"Created agent, agent ID: {agent.id}")

            # Create thread for communication
            thread = await agents_client.threads.create()
            print(f"Created thread, ID: {thread.id}")

            # Create and send message
            message = await agents_client.messages.create(
                thread_id=thread.id, role="user", content="Hello, what's the time?"
            )
            print(f"Created message, ID: {message.id}")

            # Create and run agent task
            run = await agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)
            print(f"Created run, ID: {run.id}")

            # Polling loop for run status
            while run.status in ["queued", "in_progress", "requires_action"]:
                time.sleep(4)
                run = await agents_client.runs.get(thread_id=thread.id, run_id=run.id)

                if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    if not tool_calls:
                        print("No tool calls provided - cancelling run")
                        await agents_client.runs.cancel(thread_id=thread.id, run_id=run.id)
                        break

                    tool_outputs = []
                    for tool_call in tool_calls:
                        if isinstance(tool_call, RequiredFunctionToolCall):
                            try:
                                output = await functions.execute(tool_call)
                                tool_outputs.append(
                                    ToolOutput(
                                        tool_call_id=tool_call.id,
                                        output=output,
                                    )
                                )
                            except Exception as e:
                                print(f"Error executing tool_call {tool_call.id}: {e}")

                    print(f"Tool outputs: {tool_outputs}")
                    if tool_outputs:
                        await agents_client.runs.submit_tool_outputs(
                            thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                        )

                print(f"Current run status: {run.status}")

            print(f"Run completed with status: {run.status}")

            # Delete the agent when done
            await agents_client.delete_agent(agent.id)
            print("Deleted agent")

            # Fetch and log messages
            messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            async for msg in messages:
                last_part = msg.content[-1]
                if isinstance(last_part, MessageTextContent):
                    print(f"{msg.role}: {last_part.text.value}")


if __name__ == "__main__":
    asyncio.run(main())
