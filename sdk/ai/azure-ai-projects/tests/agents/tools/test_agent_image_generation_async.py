# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import os
import base64
import pytest
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import RecordedTransport
from azure.ai.projects.models import PromptAgentDefinition, ImageGenTool
from azure.core.exceptions import ResourceNotFoundError


class TestAgentImageGenerationAsync(TestBase):

    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_agent_image_generation_async(self, **kwargs):

        model = kwargs.get("azure_ai_model_deployment_name")
        image_model = kwargs.get("image_generation_model_deployment_name")
        agent_name = "image-gen-agent"

        async with (
            self.create_async_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Check if the image model deployment exists in the project
            try:
                deployment = await project_client.deployments.get(image_model)
                print(f"Image model deployment found: {deployment.name}")
            except ResourceNotFoundError:
                pytest.fail(f"Image generation model '{image_model}' not available in this project")
            except Exception as e:
                pytest.fail(f"Unable to verify image model deployment: {e}")

            # Disable retries for faster failure when service returns 500
            openai_client.max_retries = 0

            # Create agent with image generation tool
            agent = await project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="Generate images based on user prompts",
                    tools=[ImageGenTool(model=image_model, quality="low", size="1024x1024")],  # type: ignore
                ),
                description="Agent for testing image generation.",
            )
            print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
            self._validate_agent_version(agent, expected_name=agent_name)

            # Request image generation
            print("\nAsking agent to generate an image of a simple geometric shape...")

            response = await openai_client.responses.create(
                input="Generate an image of a blue circle on a white background.",
                extra_headers={"x-ms-oai-image-generation-deployment": image_model},  # Required for image generation
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            print(f"Response created (id: {response.id})")
            assert response.id
            assert response.output is not None
            assert len(response.output) > 0

            # Extract image data from response
            image_data = [output.result for output in response.output if output.type == "image_generation_call"]

            # Verify image was generated
            assert len(image_data) > 0, "Expected at least one image to be generated"
            assert image_data[0], "Expected image data to be non-empty"

            print(f"✓ Image data received ({len(image_data[0])} base64 characters)")

            # Decode the base64 image
            image_bytes = b""
            try:
                image_bytes = base64.b64decode(image_data[0])
                assert len(image_bytes) > 0, "Decoded image should have content"
                print(f"✓ Image decoded successfully ({len(image_bytes)} bytes)")
            except Exception as e:
                pytest.fail(f"Failed to decode base64 image data: {e}")

            # Verify it's a PNG image (check magic bytes)
            # PNG files start with: 89 50 4E 47 (‰PNG)
            assert image_bytes[:4] == b"\x89PNG", "Image does not appear to be a valid PNG"
            print("✓ Image is a valid PNG")

            # Verify reasonable image size (should be > 1KB for a 1024x1024 image)
            assert len(image_bytes) > 1024, f"Image seems too small ({len(image_bytes)} bytes)"
            print(f"✓ Image size is reasonable ({len(image_bytes):,} bytes)")

            print("\n✓ Agent successfully generated and returned a valid image")

            # Save the image to a file in the .assets directory (which is .gitignored)
            os.makedirs(".assets", exist_ok=True)
            with open(".assets/generated_image_async.png", "wb") as f:
                f.write(image_bytes)
            print("✓ Image saved to .assets/generated_image_async.png")

            # Teardown
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")
