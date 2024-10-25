# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_openai_assistants_functions.py

DESCRIPTION:
    This sample demonstrates how to use function tool with assistant using the AzureOpenAI client

USAGE:
    python sample_openai_assistants_functions.py

    Before running the sample:

    pip install openai azure-identity

"""

import os, time
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI
from openai.types.beta.threads.required_action_function_tool_call import RequiredActionFunctionToolCall
from azure.ai.projects.models import FunctionTool
from user_functions import user_functions


with AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
) as project_client:

    # Explicit type hinting for IntelliSense
    client: AzureOpenAI = project_client.inference.get_azure_openai_client()

    # Initialize function tool with user functions
    functions = FunctionTool(functions=user_functions)

    with client:
        agent = client.beta.assistants.create(
            model="gpt-4-1106-preview", name="my-assistant", instructions="You are a helpful assistant", tools=functions.get_openai_definitions()
        )
        print(f"Created agent, agent ID: {agent.id}")

        thread = client.beta.threads.create()
        print(f"Created thread, thread ID: {thread.id}")

        message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content="Hello, send an email with the datetime and weather information in New York?")
        print(f"Created message, message ID: {message.id}")

        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=agent.id)

        # Poll the run while run status is queued or in progress
        while run.status in ["queued", "in_progress", "requires_action"]:
            time.sleep(1)  # Wait for a second
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            print(f"Run status: {run.status}")

            if run.status == "requires_action" and run.required_action is not None:

                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                if not tool_calls:
                    print("No tool calls provided - cancelling run")
                    client.beta.threads.runs.cancel(thread_id=thread.id, run_id=run.id)
                    break

                tool_outputs = []
                for tool_call in tool_calls:
                    if isinstance(tool_call, RequiredActionFunctionToolCall):
                        try:
                            output = functions.execute(tool_call)
                            tool_outputs.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "output": output,
                                }
                            )
                        except Exception as e:
                            print(f"Error executing tool_call {tool_call.id}: {e}")

                print(f"Tool outputs: {tool_outputs}")
                if tool_outputs:
                    client.beta.threads.runs.submit_tool_outputs(
                        thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                    )

        client.beta.assistants.delete(agent.id)
        print("Deleted agent")

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        print(f"Messages: {messages}")
