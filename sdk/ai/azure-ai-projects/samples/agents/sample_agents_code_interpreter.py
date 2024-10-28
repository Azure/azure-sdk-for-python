# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_code_interpreter_attachment.py

DESCRIPTION:
    This sample demonstrates how to use agent operations with code interpreter from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_code_interpreter_attachment.py

    Before running the sample:

    pip install azure.ai.projects azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import CodeInterpreterTool
from azure.ai.projects.models import FilePurpose
from azure.ai.projects.models import MessageAttachment, MessageTextFileCitationAnnotation, MessageTextFilePathAnnotation
from azure.identity import DefaultAzureCredential
from pathlib import Path

# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

with project_client:

    # upload a file and wait for it to be processed
    file = project_client.agents.upload_file_and_poll(file_path="nifty_500_quarterly_results.csv", purpose=FilePurpose.AGENTS)
    print(f"Uploaded file, file ID: {file.id}")

    code_interpreter = CodeInterpreterTool(file_ids=[file.id])

    # notice that CodeInterpreter must be enabled in the agent creation, otherwise the agent will not be able to see the file attachment
    agent = project_client.agents.create_agent(
        model="gpt-4-1106-preview",
        name="my-assistant",
        instructions="You are helpful assistant",
        tools=code_interpreter.definitions,
        tool_resources=code_interpreter.resources,
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    # create a message
    message = project_client.agents.create_message(
        thread_id=thread.id, role="user", content="Could you please create bar chart in TRANSPORTATION sector for the operating profit and provide file to me?"
    )
    print(f"Created message, message ID: {message.id}")

    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        # Check if you got "Rate limit is exceeded.", then you want to get more quota
        print(f"Run failed: {run.last_error}")

    project_client.agents.delete_file(file.id)
    print("Deleted file")

    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    messages = project_client.agents.get_messages(thread_id=thread.id)
    print(f"Messages: {messages}")

    last_msg = messages.get_last_text_message_by_sender("assistant")
    if last_msg:
        print(f"Last Message: {last_msg.text.value}")

    for image_content in messages.image_contents:
        print(f"Image File ID: {image_content.image_file.file_id}")

    for annotation in messages.file_annotations:
        print(f"File Annotations:")
        if isinstance(annotation, MessageTextFileCitationAnnotation):
            annotation_type = "File Citation"
            print(f"Type: {annotation_type}")
            print(f"Text: {annotation.text}")
            print(f"File ID: {annotation.file_citation.file_id}")
            print(f"Quote: {annotation.file_citation.quote}")
        elif isinstance(annotation, MessageTextFilePathAnnotation):
            annotation_type = "File Path"
            print(f"Type: {annotation_type}")
            print(f"Text: {annotation.text}")
            print(f"File ID: {annotation.file_path.file_id}")
            project_client.agents.save_file(file_id=file.id, file_name=Path(annotation.text).name)
        print(f"Start Index: {annotation.start_index}")
        print(f"End Index: {annotation.end_index}")