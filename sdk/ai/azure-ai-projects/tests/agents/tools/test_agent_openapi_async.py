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
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import RecordedTransport
from azure.ai.projects.models import (
    PromptAgentDefinition,
    OpenApiTool,
    OpenApiFunctionDefinition,
    OpenApiAnonymousAuthDetails,
)


class TestAgentOpenApiAsync(TestBase):

    # To run this test:
    # pytest tests/agents/tools/test_agent_openapi_async.py::TestAgentOpenApiAsync::test_agent_openapi_async -s
    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_agent_openapi_async(self, **kwargs):

        model = kwargs.get("azure_ai_model_deployment_name")

        async with (
            self.create_async_client(operation_group="agents", **kwargs) as project_client,
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
            tool = OpenApiTool(
                openapi=OpenApiFunctionDefinition(
                    name="get_weather",
                    spec=openapi_weather,
                    description="Retrieve weather information for a location.",
                    auth=OpenApiAnonymousAuthDetails(),
                )
            )

            agent_name = "openapi-agent"

            # Create agent with OpenAPI tool
            agent = await project_client.agents.create_version(
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

            response = await openai_client.responses.create(
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
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")

    # To run this test:
    # pytest tests/agents/tools/test_agent_openapi_async.py::TestAgentOpenApiAsync::test_agent_openapi_with_auth_async -s
    @servicePreparer()
    @pytest.mark.skip(reason="Add test here once we have a Foundry Project with a connection with auth credentials")
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_agent_openapi_with_auth_async(self, **kwargs):
        pass
