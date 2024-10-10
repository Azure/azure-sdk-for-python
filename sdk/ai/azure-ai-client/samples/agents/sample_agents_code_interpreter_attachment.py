# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os, time, logging
from azure.ai.client import AzureAIClient
from azure.ai.client.models import CodeInterpreterTool
from azure.ai.client.models._enums import FilePurpose
from azure.ai.client.models._models import MessageAttachment
from azure.identity import DefaultAzureCredential

# Set logging level
logging.basicConfig(level=logging.INFO)

# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

connection_string = os.environ["AI_CLIENT_CONNECTION_STRING"]

ai_client = AzureAIClient.from_connection_string(
    credential=DefaultAzureCredential(),
    connection=connection_string,
)

# Or, you can create the Azure AI Client by giving all required parameters directly
"""
ai_client = AzureAIClient(
    credential=DefaultAzureCredential(),
    host_name=os.environ["AI_CLIENT_HOST_NAME"],
    subscription_id=os.environ["AI_CLIENT_SUBSCRIPTION_ID"],
    resource_group_name=os.environ["AI_CLIENT_RESOURCE_GROUP_NAME"],
    workspace_name=os.environ["AI_CLIENT_WORKSPACE_NAME"],
    logging_enable=True, # Optional. Remove this line if you don't want to show how to enable logging
)
"""

with ai_client:
    # upload a file and wait for it to be processed
    file = ai_client.agents.upload_file_and_poll(file_path="product_info_1.md", purpose=FilePurpose.AGENTS, sleep_interval=4)
    logging.info(f"Uploaded file, file ID: {file.id}")
        
    code_interpreter = CodeInterpreterTool
    code_interpreter.add_file(file.id)
    
    # notices that CodeInterpreterToolDefinition as tool must be added or the assistant unable to view the file
    agent = ai_client.agents.create_agent(
        model="gpt-4-1106-preview", name="my-assistant", instructions="You are helpful assistant",
        tools=[code_interpreter]
    )
    logging.info(f"Created assistant, assistant ID: {agent.id}")

    thread = ai_client.agents.create_thread()
    logging.info(f"Created thread, thread ID: {thread.id}")    

    # create a message with the attachment
    attachment = MessageAttachment(file_id=file.id, tools=[code_interpreter])
    message = ai_client.agents.create_message(thread_id=thread.id, role="user", content="What does the attachment say?", attachments=[attachment])
    logging.info(f"Created message, message ID: {message.id}")

    run = ai_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id, sleep_interval=4)
    logging.info(f"Created run, run ID: {run.id}")
    
    
    ai_client.agents.delete_file(file.id)
    logging.info("Deleted file")

    ai_client.agents.delete_agent(agent.id)
    logging.info("Deleted assistant")

    messages = ai_client.agents.list_messages(thread_id=thread.id)
    logging.info(f"Messages: {messages}")

