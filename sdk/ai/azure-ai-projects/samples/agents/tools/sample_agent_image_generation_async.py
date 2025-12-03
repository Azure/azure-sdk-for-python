# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create an AI agent with image generation capabilities
    using the ImageGenTool and asynchronous Azure AI Projects client. The agent can generate
    images based on text prompts and save them to files.

    The sample shows:
    - Creating an agent with ImageGenTool configured for image generation
    - Making requests to generate images from text prompts
    - Extracting base64-encoded image data from the response
    - Decoding and saving the generated image to a local file
    - Proper cleanup of created resources

USAGE:
    python sample_agent_image_generation_async.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv aiohttp

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.

    NOTE:
    - Image generation requires a separate "gpt-image-1-mini" deployment which is specified when constructing
      the `ImageGenTool`, as well as providing it in the `x-ms-oai-image-generation-deployment` header when
      calling `.responses.create`.
    - AZURE_AI_MODEL_DEPLOYMENT_NAME should be set to your chat model (e.g., gpt-4o), NOT "gpt-image-1-mini".
    - The generated image will be saved as "microsoft.png" in the current directory.
"""

import asyncio
import base64
import os
from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential
from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, ImageGenTool

load_dotenv()
endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]


async def main():
    async with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        agent = await project_client.agents.create_version(
            agent_name="MyAgent",
            definition=PromptAgentDefinition(
                model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                instructions="Generate images based on user prompts",
                tools=[ImageGenTool(model="gpt-image-1-mini", quality="low", size="1024x1024")],  # type: ignore
            ),
            description="Agent for image generation.",
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

        response = await openai_client.responses.create(
            input="Generate an image of Microsoft logo.",
            extra_headers={
                "x-ms-oai-image-generation-deployment": "gpt-image-1-mini"
            },  # this is required at the moment for image generation
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
        print(f"Response created: {response.id}")

        # Save the image to a file
        image_data = [output.result for output in response.output if output.type == "image_generation_call"]

        if image_data and image_data[0]:
            print("Downloading generated image...")
            filename = "microsoft.png"
            file_path = os.path.abspath(filename)

            with open(file_path, "wb") as f:
                f.write(base64.b64decode(image_data[0]))

            # Print result (should contain "file")
            print(f"==> Result: Image downloaded and saved to file: {file_path}")

        print("\nCleaning up...")
        await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        print("Agent deleted")


if __name__ == "__main__":
    asyncio.run(main())
