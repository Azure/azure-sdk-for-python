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

    pip install azure-ai-projects azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""
import asyncio
import time
import os
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    FunctionToolParameterProperty,
    AsyncFunctionTool,
    RequiredFunctionToolCall,
    SubmitToolOutputsAction,
    ToolOutput,
)
from azure.identity.aio import DefaultAzureCredential
from user_async_functions import user_async_functions


async def main() -> None:
    async with DefaultAzureCredential() as creds:
        async with AIProjectClient.from_connection_string(
            credential=creds, conn_str=os.environ["PROJECT_CONNECTION_STRING"]
        ) as project_client:
            # Initialize assistant functions
            functions = AsyncFunctionTool(functions=user_async_functions)

            # fetch_weather function has a parameter named "unit" that can be either "Celsius" or "Fahrenheit"
            # You can specify this constraint in the description of unit parameter to be picked up by the agent.
            # But to ensure this constraint is enforced, we add this enum constraint as well.
            functions.update_parameter_property_value(
                function_name="fetch_weather",
                parameter_name="unit",
                property_name=FunctionToolParameterProperty.ENUM,
                value=["Celsius", "Fahrenheit"],
            )

            # Create agent
            agent = await project_client.agents.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-assistant",
                instructions="You are helpful assistant",
                tools=functions.definitions,
            )
            print(f"Created agent, agent ID: {agent.id}")

            # Create thread for communication
            thread = await project_client.agents.create_thread()
            print(f"Created thread, ID: {thread.id}")

            # Create and send message
            message = await project_client.agents.create_message(
                thread_id=thread.id,
                role="user",
                content="Hello, send an email with the datetime and weather information in both celsius and fahrenheit in New York?",
            )
            print(f"Created message, ID: {message.id}")

            # Create and run assistant task
            run = await project_client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
            print(f"Created run, ID: {run.id}")

            # Polling loop for run status
            while run.status in ["queued", "in_progress", "requires_action"]:
                time.sleep(4)
                run = await project_client.agents.get_run(thread_id=thread.id, run_id=run.id)

                if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
                    tool_calls = run.required_action.submit_tool_outputs.tool_calls
                    if not tool_calls:
                        print("No tool calls provided - cancelling run")
                        await project_client.agents.cancel_run(thread_id=thread.id, run_id=run.id)
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
                        await project_client.agents.submit_tool_outputs_to_run(
                            thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                        )

                print(f"Current run status: {run.status}")

            print(f"Run completed with status: {run.status}")

            # Delete the agent when done
            await project_client.agents.delete_agent(agent.id)
            print("Deleted agent")

            # Fetch and log all messages
            messages = await project_client.agents.list_messages(thread_id=thread.id)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
