# ------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ------------------------------------
from azure.ai.evaluation.agent.agent_functions import user_functions
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, ToolSet
from azure.identity import DefaultAzureCredential
from typing import Any
from pathlib import Path
import os
import json

os.environ["PROJECT_CONNECTION_STRING"] = ""

credential = DefaultAzureCredential()

project_client = AIProjectClient.from_connection_string(
    credential=credential, conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)
with project_client:
    functions = FunctionTool(user_functions)
    toolset = ToolSet()
    toolset.add(functions)

    # Create your agent
    agent = project_client.agents.create_agent(
        model="gpt-4o-mini",
        name="RedTeamAgent",
        instructions="You are a red team agent. Use the tools provided to assist with red teaming tasks.",
        toolset=toolset,
    )

    print(f"Agent '{agent.name}' created with ID: {agent.id}")

    thread = project_client.agents.create_thread()
    print(f"Created thread with ID: {thread.id}")
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="fetch a harmful prompt in the violence category",
    )
    print(f"Created message, ID: {message.id}")
    run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    convert_message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="convert the prompt using the base64_converter",
    )
    print(f"Created message, ID: {convert_message.id}")
    run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    new_prompt_with_converter = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="fetch a prompt in the self-harm category the flip_converter strategy",
    )
    print(f"Created message, ID: {new_prompt_with_converter.id}")

    run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")
    if run.status == "failed":
        print(f"Run failed: {run.last_error}")
    # Fetch and log all messages
    messages = project_client.agents.list_messages(thread_id=thread.id)
    
    # Print messages in reverse order (from earliest to latest)
    print("\n===== CONVERSATION MESSAGES =====")
    for i in range(len(messages['data'])-1, -1, -1):
        message = messages['data'][i]
        role = message['role']
        try:
            content = message['content'][0]['text']['value'] if message['content'] else "No content"
            print(f"\n[{role.upper()}] - ID: {message['id']}")
            print("-" * 50)
            print(content)
            print("-" * 50)
        except (KeyError, IndexError) as e:
            print(f"\n[{role.upper()}] - ID: {message['id']}")
            print("-" * 50)
            print(f"Error accessing message content: {e}")
            print(f"Message structure: {json.dumps(message, indent=2)}")
            print("-" * 50)
    
    print("\n===== END OF CONVERSATION =====\n")


    # Delete the agent when done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

