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

    pip install azure-ai-projects azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""
import asyncio
from typing import Any

import os
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    AsyncAgentEventHandler,
    AsyncFunctionTool,
    MessageDeltaChunk,
    RequiredFunctionToolCall,
    RunStep,
    SubmitToolOutputsAction,
    ThreadMessage,
    ThreadRun,
    ToolOutput,
)
from azure.identity.aio import DefaultAzureCredential
from user_async_functions import user_async_functions


class MyEventHandler(AsyncAgentEventHandler[str]):

    def __init__(self, functions: AsyncFunctionTool, project_client: AIProjectClient) -> None:
        super().__init__()
        self.functions = functions
        self.project_client = project_client

    async def on_message_delta(self, delta: "MessageDeltaChunk") -> str:
        return f"Text delta received: {delta.text}"

    async def on_thread_message(self, message: "ThreadMessage") -> str:
        return f"ThreadMessage created. ID: {message.id}, Status: {message.status}"

    async def on_thread_run(self, run: "ThreadRun") -> str:
        result = f"ThreadRun status: {run.status}\n"

        if run.status == "failed":
            result += f"Run failed. Error: {run.last_error}\n"

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
                        result += f"Error executing tool_call {tool_call.id}: {e}\n"

            result += f"Tool outputs: {tool_outputs}\n"
            if tool_outputs:
                # Once we receive 'requires_action' status, the next event will be DONE.
                # Here we associate our existing event handler to the next stream.
                await self.project_client.agents.submit_tool_outputs_to_stream(
                    thread_id=run.thread_id, run_id=run.id, tool_outputs=tool_outputs, event_handler=self
                )
        return result

    async def on_run_step(self, step: "RunStep") -> str:
        return f"RunStep type: {step.type}, Status: {step.status}"

    async def on_error(self, data: str) -> str:
        return f"An error occurred. Data: {data}"

    async def on_done(self) -> str:
        return "Stream completed."

    async def on_unhandled_event(self, event_type: str, event_data: Any) -> str:
        return f"Unhandled Event Type: {event_type}, Data: {event_data}"


async def main() -> None:
    async with DefaultAzureCredential() as creds:
        async with AIProjectClient.from_connection_string(
            credential=creds, conn_str=os.environ["PROJECT_CONNECTION_STRING"]
        ) as project_client:

            # [START create_agent_with_function_tool]
            functions = AsyncFunctionTool(functions=user_async_functions)

            agent = await project_client.agents.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-assistant",
                instructions="You are a helpful assistant",
                tools=functions.definitions,
            )
            # [END create_agent_with_function_tool]
            print(f"Created agent, ID: {agent.id}")

            thread = await project_client.agents.create_thread()
            print(f"Created thread, thread ID {thread.id}")

            message = await project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content="Hello, send an email with the datetime and weather information in New York? Also let me know the details.",
            )
            print(f"Created message, message ID {message.id}")

            async with await project_client.agents.create_stream(
                thread_id=thread.id, assistant_id=agent.id, event_handler=MyEventHandler(functions, project_client)
            ) as stream:
                async for event_type, event_data, func_return in stream:
                    print(f"Received data.")
                    print(f"Streaming receive Event Type: {event_type}")
                    print(f"Event Data: {str(event_data)[:100]}...")
                    print(f"Event Function return: {func_return}\n")

            await project_client.agents.delete_agent(agent.id)
            print("Deleted agent")

            messages = await project_client.agents.list_messages(thread_id=thread.id)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
