# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import os
import pytest
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, RecordedTransport
from azure.ai.projects.models import (
    PromptAgentDefinition,
    CodeInterpreterTool,
    CodeInterpreterToolAuto,
)


class TestAgentCodeInterpreter(TestBase):

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agent_code_interpreter_simple_math(self, **kwargs):
        """
        Test agent with Code Interpreter for simple Python code execution.

        This test verifies that an agent can execute simple Python code
        without any file uploads or downloads - just pure code execution.

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------
        # Setup:
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()

        # Test focus:
        POST   /openai/responses                             openai_client.responses.create() (with Code Interpreter)

        # Teardown:
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        """

        model = self.test_agents_params["model_deployment_name"]
        agent_name = "code-interpreter-simple-agent"

        with (
            self.create_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Create agent with code interpreter tool (no files)
            agent = project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a helpful assistant that can execute Python code.",
                    tools=[CodeInterpreterTool(container=CodeInterpreterToolAuto(file_ids=[]))],
                ),
                description="Simple code interpreter agent for basic Python execution.",
            )
            self._validate_agent_version(agent, expected_name=agent_name)

            # Ask the agent to execute a complex Python calculation
            # Problem: Calculate the sum of cubes from 1 to 50, then add 12!/(8!)
            # Expected answer: 1637505
            print("\nAsking agent to calculate: sum of cubes from 1 to 50, plus 12!/(8!)")

            response = openai_client.responses.create(
                input="Calculate this using Python: First, find the sum of cubes from 1 to 50 (1³ + 2³ + ... + 50³). Then add 12 factorial divided by 8 factorial (12!/8!). What is the final result?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            print(f"Response completed (id: {response.id})")
            assert response.id is not None
            assert response.output is not None
            assert len(response.output) > 0

            # Get the response text
            last_message = response.output[-1]
            response_text = ""

            if last_message.type == "message":
                for content_item in last_message.content:
                    if content_item.type == "output_text":
                        response_text += content_item.text

            print(f"Agent's response: {response_text}")

            # Verify the response contains the correct answer (1637505)
            # Note: sum of cubes 1-50 = 1,625,625; 12!/8! = 11,880; total = 1,637,505
            assert (
                "1637505" in response_text or "1,637,505" in response_text
            ), f"Expected answer 1637505 to be in response, but got: {response_text}"

            print("✓ Code interpreter successfully executed Python code and returned correct answer")

            # Teardown
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")

    @servicePreparer()
    @pytest.mark.skip(
        reason="Skipped due to known server bug. Enable once https://msdata.visualstudio.com/Vienna/_workitems/edit/4841313 is resolved"
    )
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agent_code_interpreter_file_generation(self, **kwargs):
        """
        Test agent with Code Interpreter for file upload, processing, and download.

        This test verifies that an agent can:
        1. Work with uploaded CSV files
        2. Execute Python code to generate a chart
        3. Return a downloadable file

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------
        # Setup:
        POST   /files                                        openai_client.files.create()
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()

        # Test focus:
        POST   /openai/responses                             openai_client.responses.create() (with Code Interpreter + file)
        GET    /containers/{container_id}/files/{file_id}    openai_client.containers.files.content.retrieve()

        # Teardown:
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        DELETE /files/{file_id}                              openai_client.files.delete()
        """

        model = self.test_agents_params["model_deployment_name"]

        with (
            self.create_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Get the path to the test CSV file
            asset_file_path = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__), "../../../samples/agents/assets/synthetic_500_quarterly_results.csv"
                )
            )

            assert os.path.exists(asset_file_path), f"Test CSV file not found at: {asset_file_path}"
            print(f"Using test CSV file: {asset_file_path}")

            # Upload the CSV file
            with open(asset_file_path, "rb") as f:
                file = openai_client.files.create(purpose="assistants", file=f)

            print(f"File uploaded (id: {file.id})")
            assert file.id is not None

            # Create agent with code interpreter tool and the uploaded file
            agent = project_client.agents.create_version(
                agent_name="code-interpreter-file-agent",
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a helpful assistant that can analyze data and create visualizations.",
                    tools=[CodeInterpreterTool(container=CodeInterpreterToolAuto(file_ids=[file.id]))],
                ),
                description="Code interpreter agent for file processing and chart generation.",
            )
            print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
            assert agent.id is not None
            assert agent.name == "code-interpreter-file-agent"
            assert agent.version is not None

            # Ask the agent to create a chart from the CSV
            print("\nAsking agent to create a bar chart...")

            response = openai_client.responses.create(
                input="Create a bar chart showing operating profit by sector from the uploaded CSV file. Save it as a PNG file.",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            print(f"Response completed (id: {response.id})")
            assert response.id is not None
            assert response.output is not None
            assert len(response.output) > 0

            # Extract file information from response annotations
            file_id = ""
            filename = ""
            container_id = ""

            last_message = response.output[-1]
            if last_message.type == "message":
                for content_item in last_message.content:
                    if content_item.type == "output_text":
                        if content_item.annotations:
                            for annotation in content_item.annotations:
                                if annotation.type == "container_file_citation":
                                    file_id = annotation.file_id
                                    filename = annotation.filename
                                    container_id = annotation.container_id
                                    print(
                                        f"Found generated file: {filename} (ID: {file_id}, Container: {container_id})"
                                    )
                                    break

            # Verify that a file was generated
            assert file_id, "Expected a file to be generated but no file ID found in response"
            assert filename, "Expected a filename but none found in response"
            assert container_id, "Expected a container ID but none found in response"

            print(f"✓ File generated successfully: {filename}")

            # Download the generated file
            print(f"Downloading file {filename}...")
            file_content = openai_client.containers.files.content.retrieve(file_id=file_id, container_id=container_id)

            # Read the content
            content_bytes = file_content.read()
            assert len(content_bytes) > 0, "Expected file content but got empty bytes"

            print(f"✓ File downloaded successfully ({len(content_bytes)} bytes)")

            # Verify it's a PNG file (check magic bytes)
            if filename.endswith(".png"):
                # PNG files start with: 89 50 4E 47 (‰PNG)
                assert content_bytes[:4] == b"\x89PNG", "File does not appear to be a valid PNG"
                print("✓ File is a valid PNG image")

            # Teardown
            print("\nCleaning up...")
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")

            openai_client.files.delete(file.id)
            print("Uploaded file deleted")
