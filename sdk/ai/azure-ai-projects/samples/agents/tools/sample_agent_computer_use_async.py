# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use Computer Use Agent (CUA) functionality
    with the Azure AI Projects client using async/await. It simulates browser automation by
    creating an agent that can interact with computer interfaces through
    simulated actions and screenshots.

    The sample creates a Computer Use Agent that performs a web search simulation,
    demonstrating how to handle computer actions like typing, clicking, and
    taking screenshots in a controlled environment using asynchronous operations.

USAGE:
    python sample_agent_computer_use_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity openai python-dotenv aiohttp

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import asyncio
import os
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import AgentReference, PromptAgentDefinition, ComputerUsePreviewTool
from computer_use_util import (
    SearchState,
    load_screenshot_assets,
    handle_computer_action_and_take_screenshot,
    print_final_output,
)

load_dotenv()


async def main():
    """Main async function to demonstrate Computer Use Agent functionality."""
    # Initialize state machine
    current_state = SearchState.INITIAL

    # Load screenshot assets
    try:
        screenshots = load_screenshot_assets()
        print("Successfully loaded screenshot assets")
    except FileNotFoundError:
        print("Failed to load required screenshot assets. Please ensure the asset files exist in ../assets/")
        return

    credential = DefaultAzureCredential()
    async with credential:
        project_client = AIProjectClient(
            endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
            credential=credential,
        )

        computer_use_tool = ComputerUsePreviewTool(display_width=1026, display_height=769, environment="windows")

        async with project_client:
            agent = await project_client.agents.create_version(
                agent_name="ComputerUseAgent",
                definition=PromptAgentDefinition(
                    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                    instructions="""
                    You are a computer automation assistant. 
                    
                    Be direct and efficient. When you reach the search results page, read and describe the actual search result titles and descriptions you can see.
                    """,
                    tools=[computer_use_tool],
                ),
                description="Computer automation agent with screen interaction capabilities.",
            )
            print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

            openai_client = project_client.get_openai_client()

            # Initial request with screenshot - start with Bing search page
            print("Starting computer automation session (initial screenshot: cua_browser_search.png)...")
            response = await openai_client.responses.create(
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": "I need you to help me search for 'OpenAI news'. Please type 'OpenAI news' and submit the search. Once you see search results, the task is complete.",
                            },
                            {
                                "type": "input_image",
                                "image_url": screenshots["browser_search"]["url"],
                                "detail": "high",
                            },  # Start with Bing search page
                        ],
                    }
                ],
                extra_body={"agent": AgentReference(name=agent.name).as_dict()},
                truncation="auto",
            )

            print(f"Initial response received (ID: {response.id})")

            # Main interaction loop with deterministic completion
            max_iterations = 10  # Allow enough iterations for completion
            iteration = 0

            while True:
                if iteration >= max_iterations:
                    print(f"\nReached maximum iterations ({max_iterations}). Stopping.")
                    break

                iteration += 1
                print(f"\n--- Iteration {iteration} ---")

                # Check for computer calls in the response
                computer_calls = [item for item in response.output if item.type == "computer_call"]

                if not computer_calls:
                    print_final_output(response)
                    break

                # Process the first computer call
                computer_call = computer_calls[0]
                action = computer_call.action
                call_id = computer_call.call_id

                print(f"Processing computer call (ID: {call_id})")

                # Handle the action and get the screenshot info
                screenshot_info, current_state = handle_computer_action_and_take_screenshot(
                    action, current_state, screenshots
                )

                print(f"Sending action result back to agent (using {screenshot_info['filename']})...")

                # Regular response with just the screenshot
                response = await openai_client.responses.create(
                    previous_response_id=response.id,
                    input=[
                        {
                            "call_id": call_id,
                            "type": "computer_call_output",
                            "output": {
                                "type": "computer_screenshot",
                                "image_url": screenshot_info["url"],
                            },
                        }
                    ],
                    extra_body={"agent": AgentReference(name=agent.name).as_dict()},
                    truncation="auto",
                )

                print(f"Follow-up response received (ID: {response.id})")

            print("\nCleaning up...")
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")


if __name__ == "__main__":
    asyncio.run(main())
