# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run Prompt Agent operations
    using the Code Interpreter Tool and an asynchronous client followed by downloading the generated file.

USAGE:
    python sample_agent_code_interpreter_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
import tempfile
import asyncio
from dotenv import load_dotenv
from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, CodeInterpreterTool, CodeInterpreterContainerAuto

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]


async def main() -> None:
    """Main async function to demonstrate code interpreter with async client and credential management."""

    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        try:
            # Load the CSV file to be processed
            asset_file_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../assets/synthetic_500_quarterly_results.csv")
            )

            # Upload the CSV file for the code interpreter to use
            with open(asset_file_path, "rb") as file_data:
                file = await openai_client.files.create(purpose="assistants", file=file_data)
            print(f"File uploaded (id: {file.id})")

            # Create agent with code interpreter tool
            agent = await project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(
                    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                    instructions="You are a helpful assistant.",
                    tools=[CodeInterpreterTool(container=CodeInterpreterContainerAuto(file_ids=[file.id]))],
                ),
                description="Code interpreter agent for data analysis and visualization.",
            )
            print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

            # Create a conversation for the agent interaction
            conversation = await openai_client.conversations.create()
            print(f"Created conversation (id: {conversation.id})")

            # Send request to create a chart and generate a file
            response = await openai_client.responses.create(
                conversation=conversation.id,
                input="Could you please create bar chart in TRANSPORTATION sector for the operating profit from the uploaded csv file and provide file to me?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )
            print(f"Response completed (id: {response.id})")

            # Extract file information from response annotations
            file_id = ""
            filename = ""
            container_id = ""

            # Get the last message which should contain file citations
            last_message = response.output[-1]  # ResponseOutputMessage
            if (
                last_message.type == "message"
                and last_message.content
                and last_message.content[-1].type == "output_text"
                and last_message.content[-1].annotations
            ):
                file_citation = last_message.content[-1].annotations[-1]  # AnnotationContainerFileCitation
                if file_citation.type == "container_file_citation":
                    file_id = file_citation.file_id
                    filename = file_citation.filename
                    container_id = file_citation.container_id
                    print(f"Found generated file: {filename} (ID: {file_id})")

            print("\nCleaning up...")
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")

            # Download the generated file if available
            if file_id and filename:
                file_content = await openai_client.containers.files.content.retrieve(
                    file_id=file_id, container_id=container_id
                )
                print(f"File ready for download: {filename}")
                file_path = os.path.join(tempfile.gettempdir(), filename)
                with open(file_path, "wb") as f:
                    f.write(file_content.read())
                print(f"File downloaded successfully: {file_path}")
            else:
                print("No file generated in response")

        except Exception as e:
            print(f"Error occurred: {str(e)}")
            raise


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
