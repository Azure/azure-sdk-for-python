# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with an event handler and toolset from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_stream_eventhandler_with_functions_async.py

    Before running the sample:

    pip install azure-ai-agents azure-identity aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model.
"""
import asyncio
from typing import Any

import os
from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import (
    AsyncAgentEventHandler,
    AsyncFunctionTool,
    ListSortOrder,
    MessageTextContent,
    MessageDeltaChunk,
    RequiredFunctionToolCall,
    RunStep,
    SubmitToolOutputsAction,
    ThreadMessage,
    ThreadRun,
    ToolOutput,
)
from azure.identity.aio import DefaultAzureCredential
from utils.user_async_functions import user_async_functions


class MyEventHandler(AsyncAgentEventHandler[str]):

    def __init__(self, functions: AsyncFunctionTool, agents_client: AgentsClient) -> None:
        super().__init__()
        self.functions = functions
        self.agents_client = agents_client

    async def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        print(f"Text delta received: {delta.text}")

    async def on_thread_message(self, message: "ThreadMessage") -> None:
        print(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    async def on_thread_run(self, run: "ThreadRun") -> None:
        print(f"ThreadRun status: {run.status}")

        if run.status == "failed":
            print(f"Run failed. Error: {run.last_error}")

        if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
            tool_calls = run.required_action.submit_tool_outputs.tool_calls

            tool_outputs = []
            for tool_call in tool_calls:
                if isinstance(tool_call, RequiredFunctionToolCall):
                    try:
                        output = await self.functions.execute(tool_call)
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
                await self.agents_client.runs.submit_tool_outputs_stream(
                    thread_id=run.thread_id, run_id=run.id, tool_outputs=tool_outputs, event_handler=self
                )

    async def on_run_step(self, step: "RunStep") -> None:
        print(f"RunStep type: {step.type}, Status: {step.status}")

    async def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    async def on_done(self) -> None:
        print("Stream completed.")

    async def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")


async def main() -> None:
    async with DefaultAzureCredential() as creds:
        async with AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=creds,
        ) as agents_client:

            # [START create_agent_with_function_tool]
            functions = AsyncFunctionTool(functions=user_async_functions)

            agent = await agents_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-agent",
                instructions="You are a helpful agent",
                tools=functions.definitions,
            )
            # [END create_agent_with_function_tool]
            print(f"Created agent, ID: {agent.id}")

            thread = await agents_client.threads.create()
            print(f"Created thread, thread ID {thread.id}")

            message = await agents_client.messages.create(
                thread_id=thread.id,
                role="user",
                content="Hello, send an email with the datetime and weather information in New York? Also let me know the details.",
            )
            print(f"Created message, message ID {message.id}")

            async with await agents_client.runs.stream(
                thread_id=thread.id,
                agent_id=agent.id,
                event_handler=MyEventHandler(functions, agents_client),
            ) as stream:
                await stream.until_done()

            await agents_client.delete_agent(agent.id)
            print("Deleted agent")

            messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            async for msg in messages:
                last_part = msg.content[-1]
                if isinstance(last_part, MessageTextContent):
                    print(f"{msg.role}: {last_part.text.value}")


if __name__ == "__main__":
    asyncio.run(main())
