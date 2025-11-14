# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create an AI agent with image generation capabilities
    using the ImageGenTool and synchronous Azure AI Projects client. The agent can generate
    images based on text prompts and save them to files.

    The sample shows:
    - Creating an agent with ImageGenTool configured for image generation
    - Making requests to generate images from text prompts
    - Extracting base64-encoded image data from the response
    - Decoding and saving the generated image to a local file
    - Proper cleanup of created resources

USAGE:
    python sample_agent_image_generation.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity openai python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the chat model (e.g., gpt-4o, gpt-4o-mini, gpt-5o, gpt-5o-mini)
       used by the agent for understanding and responding to prompts. This is NOT the image generation model.

    NOTE:
    - Image generation requires a separate "gpt-image-1" deployment which is specified in the
      x-ms-oai-image-generation-deployment header when creating the response.
    - AZURE_AI_MODEL_DEPLOYMENT_NAME should be set to your chat model (e.g., gpt-4o), NOT "gpt-image-1".
    - The generated image will be saved as "microsoft.png" in the current directory.
"""

import base64
import os
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, ImageGenTool

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):

    # [START tool_declaration]
    tool = ImageGenTool(quality="low", size="1024x1024")
    # [END tool_declaration]

    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="Generate images based on user prompts",
            tools=[tool],
        ),
        description="Agent for image generation.",
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    response = openai_client.responses.create(
        input="Generate an image of Microsoft logo.",
        extra_headers={
            "x-ms-oai-image-generation-deployment": "gpt-image-1"
        },  # this is required at the moment for image generation
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )
    print(f"Response created: {response.id}")

    # Save the image to a file
    # [START download_image]
    image_data = [output.result for output in response.output if output.type == "image_generation_call"]

    if image_data and image_data[0]:
        print("Downloading generated image...")
        filename = "microsoft.png"
        file_path = os.path.abspath(filename)

        with open(file_path, "wb") as f:
            f.write(base64.b64decode(image_data[0]))
        # [END download_image]
        print(f"Image downloaded and saved to: {file_path}")

    print("\nCleaning up...")
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
