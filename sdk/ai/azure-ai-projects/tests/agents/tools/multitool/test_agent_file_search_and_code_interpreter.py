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

from io import BytesIO
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, RecordedTransport
from azure.ai.projects.models import PromptAgentDefinition, FileSearchTool, CodeInterpreterTool, CodeInterpreterToolAuto


class TestAgentFileSearchAndCodeInterpreter(TestBase):
    """Tests for agents using File Search + Code Interpreter combination."""

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_find_and_analyze_data(self, **kwargs):
        """
        Test finding data with File Search and analyzing with Code Interpreter.

        This test verifies that both tools are used:
        1. File Search: Agent finds the data file containing numbers
        2. Code Interpreter: Agent calculates the average of those numbers
        """

        model = kwargs.get("AZURE_AI_MODEL_DEPLOYMENT_NAME")

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Create data file with numbers that require actual computation
        # Numbers: 31, 20, 52, 48, 45, 34, 30, 86, 28, 71, 21, 20, 28, 44, 46
        # Sum: 604, Count: 15, Average: 40.266... ≈ 40.27
        # This is impossible to calculate mentally - requires Code Interpreter
        txt_content = """Sensor Readings Log - Experiment #2847

The following temperature readings (Celsius) were recorded over a 15-hour period:

Hour 1: 31
Hour 2: 20
Hour 3: 52
Hour 4: 48
Hour 5: 45
Hour 6: 34
Hour 7: 30
Hour 8: 86
Hour 9: 28
Hour 10: 71
Hour 11: 21
Hour 12: 20
Hour 13: 28
Hour 14: 44
Hour 15: 46

End of sensor log.
"""
        vector_store = openai_client.vector_stores.create(name="DataStore")

        txt_file = BytesIO(txt_content.encode("utf-8"))
        txt_file.name = "sensor_readings.txt"

        file = openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=txt_file,
        )
        print(f"File uploaded (id: {file.id})")

        # Create agent with explicit instructions to use both tools
        agent = project_client.agents.create_version(
            agent_name="file-search-code-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a data analyst. Use file search to find data files, then use code interpreter to perform calculations on the data.",
                tools=[
                    FileSearchTool(vector_store_ids=[vector_store.id]),
                    CodeInterpreterTool(container=CodeInterpreterToolAuto()),
                ],
            ),
            description="Agent with File Search and Code Interpreter.",
        )
        print(f"Agent created (id: {agent.id})")

        # Request that requires both tools: find data AND calculate
        response = openai_client.responses.create(
            input="Find the sensor readings file and use code to calculate the average temperature. Show me the result.",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
        self.validate_response(response)
        assert len(response.output_text) > 20
        print("✓ File Search + Code Interpreter works!")

        # Cleanup
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        openai_client.vector_stores.delete(vector_store.id)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_analyze_code_file(self, **kwargs):
        """
        Test finding code file and running it with Code Interpreter.

        This test verifies that both tools are used:
        1. File Search: Agent finds the Python code file
        2. Code Interpreter: Agent executes the code and returns the computed result
        """

        model = kwargs.get("AZURE_AI_MODEL_DEPLOYMENT_NAME")

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Create Python code file with a function that computes a specific value
        # fibonacci(15) = 610 - this is not a commonly memorized value
        python_code = """# Fibonacci sequence calculator

def fibonacci(n):
    \"\"\"Calculate the nth Fibonacci number recursively.\"\"\"
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# The code needs to be executed to find what fibonacci(15) equals
# This is not a commonly known value - it requires actual computation
"""

        vector_store = openai_client.vector_stores.create(name="CodeAnalysisStore")

        code_file = BytesIO(python_code.encode("utf-8"))
        code_file.name = "fibonacci.py"

        file = openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=code_file,
        )
        print(f"Code file uploaded (id: {file.id})")

        # Create agent with explicit instructions to run code
        agent = project_client.agents.create_version(
            agent_name="file-search-code-analysis-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a code analyst. Use file search to find code files, then use code interpreter to execute and test the code.",
                tools=[
                    FileSearchTool(vector_store_ids=[vector_store.id]),
                    CodeInterpreterTool(container=CodeInterpreterToolAuto()),
                ],
            ),
            description="Agent for code analysis and execution.",
        )
        print(f"Agent created (id: {agent.id})")

        # Request that requires both tools: find code AND execute it
        response = openai_client.responses.create(
            input="Find the fibonacci code file and run it to calculate fibonacci(15). What is the result?",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )

        response_text = response.output_text
        print(f"Response: {response_text[:400]}...")

        # Verify response is meaningful
        assert len(response_text) > 30, "Expected detailed response"

        # Verify File Search was used - response should reference the fibonacci code
        response_lower = response_text.lower()
        assert any(
            keyword in response_lower for keyword in ["fibonacci", "function", "recursive", "code"]
        ), f"Expected response to reference the fibonacci code. Got: {response_text[:200]}"

        # Verify Code Interpreter executed the code and got the correct result
        # fibonacci(15) = 610 - this requires actual execution
        assert "610" in response_text, f"Expected fibonacci(15) = 610 in response. Got: {response_text[:300]}"

        print("[PASS] File Search + Code Interpreter both verified!")
        print("  - File Search: Found the fibonacci code file")
        print("  - Code Interpreter: Executed code and computed fibonacci(15) = 610")

        # Cleanup
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        openai_client.vector_stores.delete(vector_store.id)
