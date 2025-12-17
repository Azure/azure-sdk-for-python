# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import base64
import pytest
from devtools_testutils import recorded_by_proxy, RecordedTransport
from test_base import TestBase, servicePreparer
from azure.ai.projects.models import ImageGenTool


class TestResponsesImageGeneration(TestBase):

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.HTTPX)
    def test_responses_image_generation(self, **kwargs):
        """
        Test creating a responses call with Image Generation tool (no Agents, no Conversation).

        Routes used in this test:

        Action REST API Route                                OpenAI Client Method
        ------+---------------------------------------------+-----------------------------------
        POST   /openai/responses                             client.responses.create() (with ImageGenTool)
        """
        model = kwargs.get("azure_ai_projects_tests_model_deployment_name")
        image_model = kwargs.get("azure_ai_projects_tests_image_generation_model_deployment_name")

        client = self.create_client(operation_group="agents", **kwargs).get_openai_client()

        # Disable retries for faster failure when service returns 500
        client.max_retries = 0

        print("\nAsking for image generation of a blue circle on a white background...")

        response = client.responses.create(
            model=model,
            input="Generate an image of a blue circle on a white background.",
            tools=[ImageGenTool(model=image_model, quality="low", size="1024x1024")],  # type: ignore
            extra_headers={"x-ms-oai-image-generation-deployment": image_model},  # Required for image generation
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

        print("\n✓ Successfully generated and received a valid image")
