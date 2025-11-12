# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create an AI agent with Browser Automation capabilities
    using the BrowserAutomationAgentTool and synchronous Azure AI Projects client. The agent can
    perform automated web browsing tasks and provide responses based on web interactions.

USAGE:
    python sample_agent_browser_automation.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity openai python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) BROWSER_AUTOMATION_PROJECT_CONNECTION_ID - The browser automation project connection ID,
       as found in the "Connections" tab in your Microsoft Foundry project.
"""

import os
import json
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    BrowserAutomationAgentTool,
    BrowserAutomationToolParameters,
    BrowserAutomationToolConnectionParameters,
)
load_dotenv()

project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

openai_client = project_client.get_openai_client()

browser_automation_tool = BrowserAutomationAgentTool(
    browser_automation_preview=BrowserAutomationToolParameters(
        connection=BrowserAutomationToolConnectionParameters(
            project_connection_id=os.environ["BROWSER_AUTOMATION_PROJECT_CONNECTION_ID"],
        )
    )
)

with project_client:
    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="""You are an Agent helping with browser automation tasks. 
            You can answer questions, provide information, and assist with various tasks 
            related to web browsing using the Browser Automation tool available to you.""",
            tools=[browser_automation_tool],
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    stream_response = openai_client.responses.create(
        stream=True,
        tool_choice="required",
        input="""
            Your goal is to report the percent of Microsoft year-to-date stock price change.
            To do that, go to the website finance.yahoo.com.
            At the top of the page, you will find a search bar.
            Enter the value 'MSFT', to get information about the Microsoft stock price.
            At the top of the resulting page you will see a default chart of Microsoft stock price.
            Click on 'YTD' at the top of that chart, and report the percent value that shows up just below it.""",
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )

    for event in stream_response:
        if event.type == "response.created":
            print(f"Follow-up response created with ID: {event.response.id}")
        elif event.type == "response.output_text.delta":
            print(f"Delta: {event.delta}")
        elif event.type == "response.text.done":
            print(f"\nFollow-up response done!")
        elif event.type == "response.output_item.done":
            item = event.item
            if item.type == "browser_automation_preview_call":  # TODO: support browser_automation_preview_call schema
                arguments_str = getattr(item, "arguments", "{}")

                # Parse the arguments string into a dictionary
                arguments = json.loads(arguments_str)
                query = arguments.get("query")

                print(f"Call ID: {getattr(item, 'call_id')}")
                print(f"Query arguments: {query}")
        elif event.type == "response.completed":
            print(f"\nFollow-up completed!")
            print(f"Full response: {event.response.output_text}")

    print("\nCleaning up...")
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
