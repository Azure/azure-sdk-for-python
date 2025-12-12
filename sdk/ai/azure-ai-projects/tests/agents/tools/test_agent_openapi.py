# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import os

import pytest
import jsonref
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, RecordedTransport
from azure.ai.projects.models import (
    PromptAgentDefinition,
    OpenApiAgentTool,
    OpenApiFunctionDefinition,
    OpenApiAnonymousAuthDetails,
)


class TestAgentOpenApi(TestBase):

    # To run this test:
    # pytest tests/agents/tools/test_agent_openapi.py::TestAgentOpenApi::test_agent_openapi -s
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agent_openapi(self, **kwargs):
        """
        Test agent with OpenAPI tool capabilities.

        This test verifies that an agent can:
        1. Use OpenApiAgentTool to call external APIs defined by OpenAPI specifications
        2. Load and parse OpenAPI spec from JSON file
        3. Make API calls and incorporate results into responses

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------
        # Setup:
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()

        # Test focus:
        POST   /openai/responses                             openai_client.responses.create() (with OpenApiAgentTool)

        # Teardown:
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        """

        model = kwargs.get("azure_ai_projects_tests_model_deployment_name")

        with (
            self.create_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Load OpenAPI spec from assets folder
            weather_asset_file_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../../samples/agents/assets/weather_openapi.json")
            )

            assert os.path.exists(weather_asset_file_path), f"OpenAPI spec file not found at: {weather_asset_file_path}"
            print(f"Using OpenAPI spec file: {weather_asset_file_path}")

            with open(weather_asset_file_path, "r") as f:
                openapi_weather = jsonref.loads(f.read())

            # Create OpenAPI tool
            tool = OpenApiAgentTool(
                openapi=OpenApiFunctionDefinition(
                    name="get_weather",
                    spec=openapi_weather,
                    description="Retrieve weather information for a location.",
                    auth=OpenApiAnonymousAuthDetails(),
                )
            )

            agent_name = "openapi-agent"

            # Create agent with OpenAPI tool
            agent = project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a helpful assistant.",
                    tools=[tool],
                ),
                description="Agent for testing OpenAPI tool capabilities.",
            )
            self._validate_agent_version(agent, expected_name=agent_name)

            # Ask the agent to use the OpenAPI tool
            print("\nAsking agent to use OpenAPI tool to get weather...")

            response = openai_client.responses.create(
                input="Use the OpenAPI tool to print out, what is the weather in Seattle, WA today.",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )
            self.validate_response(response)

            # Get the response text
            response_text = response.output_text
            print(f"\nAgent's response: {response_text[:300]}...")

            # Verify we got a meaningful response
            assert len(response_text) > 30, f"Expected a substantial response from the agent. Got '{response_text}'"

            # The response should mention weather or Seattle (indicating the OpenAPI tool was used)
            response_lower = response_text.lower()
            assert any(
                keyword in response_lower for keyword in ["weather", "seattle", "temperature", "forecast"]
            ), f"Expected response to contain weather information, but got: {response_text[:200]}"

            print("\n✓ Agent successfully used OpenAPI tool to call external API")

            # Teardown
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")

    # To run this test:
    # pytest tests/agents/tools/test_agent_openapi.py::TestAgentOpenApi::test_agent_openapi_with_auth -s
    @servicePreparer()
    @pytest.mark.skip(reason="Add test here once we have a Foundry Project with a connection with auth credentials")
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agent_openapi_with_auth(self, **kwargs):
        pass
