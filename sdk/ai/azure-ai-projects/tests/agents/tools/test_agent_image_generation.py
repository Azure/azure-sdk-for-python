# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import base64
import pytest
from test_base import TestBase, servicePreparer
from devtools_testutils import is_live_and_not_recording
from azure.ai.projects.models import PromptAgentDefinition, ImageGenTool


class TestAgentImageGeneration(TestBase):

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_agent_image_generation(self, **kwargs):
        """
        Test agent with Image Generation tool.

        This test verifies that an agent can:
        1. Use ImageGenTool to generate images from text prompts
        2. Return base64-encoded image data
        3. Decode and validate the image format

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------
        # Setup:
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()

        # Test focus:
        POST   /openai/responses                             openai_client.responses.create() (with ImageGenTool)

        # Teardown:
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        """
        
        # Skip for usw21 - image model not deployed there
        endpoint = kwargs.get("azure_ai_projects_tests_agents_project_endpoint", "")
        if "usw2" in endpoint.lower():
            pytest.skip("Image generation not available in usw21 (image model not deployed)")

        model = self.test_agents_params["model_deployment_name"]

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()
        
        # Disable retries for faster failure when service returns 500
        openai_client.max_retries = 0

        # Create agent with image generation tool
        agent = project_client.agents.create_version(
            agent_name="image-gen-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="Generate images based on user prompts",
                tools=[ImageGenTool(quality="low", size="1024x1024")],
            ),
            description="Agent for testing image generation.",
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
        assert agent.id is not None
        assert agent.name == "image-gen-agent"
        assert agent.version is not None

        # Request image generation
        print("\nAsking agent to generate an image of a simple geometric shape...")
        
        response = openai_client.responses.create(
            input="Generate an image of a blue circle on a white background.",
            extra_headers={
                "x-ms-oai-image-generation-deployment": "gpt-image-1-mini"
            },  # Required for image generation
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
        
        print(f"Response created (id: {response.id})")
        assert response.id is not None
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
        assert image_bytes[:4] == b'\x89PNG', "Image does not appear to be a valid PNG"
        print("✓ Image is a valid PNG")

        # Verify reasonable image size (should be > 1KB for a 1024x1024 image)
        assert len(image_bytes) > 1024, f"Image seems too small ({len(image_bytes)} bytes)"
        print(f"✓ Image size is reasonable ({len(image_bytes):,} bytes)")

        print("\n✓ Agent successfully generated and returned a valid image")

        # Teardown
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        print("Agent deleted")
