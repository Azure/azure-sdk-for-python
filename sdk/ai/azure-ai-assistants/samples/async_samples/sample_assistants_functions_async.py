# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_assistants_functions_async.py

DESCRIPTION:
    This sample demonstrates how to use assistant operations with custom functions from
    the Azure Assistants service using a asynchronous client.

USAGE:
    python sample_assistants_functions_async.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""
import asyncio
import time
import os
from azure.ai.assistants.aio import AssistantsClient
from azure.ai.assistants.models import AsyncFunctionTool, RequiredFunctionToolCall, SubmitToolOutputsAction, ToolOutput
from azure.identity.aio import DefaultAzureCredential
from user_async_functions import user_async_functions


async def main() -> None:
    async with DefaultAzureCredential() as creds:
        async with AssistantsClient.from_connection_string(
            credential=creds, conn_str=os.environ["PROJECT_CONNECTION_STRING"]
        ) as assistants_client:
            # Initialize assistant functions
            functions = AsyncFunctionTool(functions=user_async_functions)

            # Create assistant
            assistant = await assistants_client.create_assistant(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-assistant",
                instructions="You are helpful assistant",
                tools=functions.definitions,
            )
            print(f"Created assistant, assistant ID: {assistant.id}")

            # Create thread for communication
            thread = await assistants_client.create_thread()
            print(f"Created thread, ID: {thread.id}")

            # Create and send message
            message = await assistants_client.create_message(
                thread_id=thread.id, role="user", content="Hello, what's the time?"
            )
            print(f"Created message, ID: {message.id}")

            # Create and run assistant task
            run = await assistants_client.create_run(thread_id=thread.id, assistant_id=assistant.id)
            print(f"Created run, ID: {run.id}")

            # Polling loop for run status
            while run.status in ["queued", "in_progress", "requires_action"]:
                time.sleep(4)
                run = await assistants_client.get_run(thread_id=thread.id, run_id=run.id)

                if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    if not tool_calls:
                        print("No tool calls provided - cancelling run")
                        await assistants_client.cancel_run(thread_id=thread.id, run_id=run.id)
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
                        await assistants_client.submit_tool_outputs_to_run(
                            thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                        )

                print(f"Current run status: {run.status}")

            print(f"Run completed with status: {run.status}")

            # Delete the assistant when done
            await assistants_client.delete_assistant(assistant.id)
            print("Deleted assistant")

            # Fetch and log all messages
            messages = await assistants_client.list_messages(thread_id=thread.id)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
