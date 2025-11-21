# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

"""
Multi-Tool Tests: File Search + Code Interpreter

Tests various scenarios using an agent with File Search and Code Interpreter.
All tests use the same tool combination but different inputs and workflows.
"""

import os
import pytest
from io import BytesIO
from test_base import TestBase, servicePreparer
from devtools_testutils import is_live_and_not_recording
from azure.ai.projects.models import PromptAgentDefinition, FileSearchTool, CodeInterpreterTool, CodeInterpreterToolAuto

class TestAgentFileSearchAndCodeInterpreter(TestBase):
    """Tests for agents using File Search + Code Interpreter combination."""

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_find_and_analyze_data(self, **kwargs):
        """
        Test finding data with File Search and analyzing with Code Interpreter.
        """

        model = self.test_agents_params["model_deployment_name"]

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Create data file
        txt_content = "Sample data: 10, 20, 30, 40, 50"
        vector_store = openai_client.vector_stores.create(name="DataStore")        

        txt_file = BytesIO(txt_content.encode("utf-8"))
        txt_file.name = "data.txt"

        file = openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=txt_file,
        )
        print(f"File uploaded (id: {file.id})")

        # Create agent
        agent = project_client.agents.create_version(
            agent_name="file-search-code-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="Find data and analyze it.",
                tools=[
                    FileSearchTool(vector_store_ids=[vector_store.id]),
                    CodeInterpreterTool(container=CodeInterpreterToolAuto()),
                ],
            ),
            description="Agent with File Search and Code Interpreter.",
        )
        print(f"Agent created (id: {agent.id})")

        # Use the agent
        response = openai_client.responses.create(
            input="Find the data file and calculate the average.",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
        print(f"Response received (id: {response.id})")

        assert response.id is not None
        assert len(response.output_text) > 20
        print("✓ File Search + Code Interpreter works!")

        # Cleanup
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        openai_client.vector_stores.delete(vector_store.id)

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_analyze_code_file(self, **kwargs):
        """
        Test finding code file and analyzing it.
        """

        model = self.test_agents_params["model_deployment_name"]

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Create Python code file
        python_code = """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
print(f"Fibonacci(10) = {result}")
"""

        vector_store = openai_client.vector_stores.create(name="CodeAnalysisStore")

        from io import BytesIO

        code_file = BytesIO(python_code.encode("utf-8"))
        code_file.name = "fibonacci.py"

        file = openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=code_file,
        )
        print(f"Code file uploaded (id: {file.id})")

        # Create agent
        agent = project_client.agents.create_version(
            agent_name="file-search-code-analysis-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="Find code files and analyze them. You can run code to test it.",
                tools=[
                    FileSearchTool(vector_store_ids=[vector_store.id]),
                    CodeInterpreterTool(container=CodeInterpreterToolAuto()),
                ],
            ),
            description="Agent for code analysis.",
        )
        print(f"Agent created (id: {agent.id})")

        # Request analysis
        response = openai_client.responses.create(
            input="Find the fibonacci code and explain what it does. What is the computational complexity?",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )

        response_text = response.output_text
        print(f"Response: {response_text[:300]}...")

        assert len(response_text) > 50
        response_lower = response_lower = response_text.lower()
        assert any(
            keyword in response_lower for keyword in ["fibonacci", "recursive", "complexity", "exponential"]
        ), "Expected analysis of fibonacci algorithm"

        print("✓ Code file analysis completed")

        # Cleanup
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        openai_client.vector_stores.delete(vector_store.id)
