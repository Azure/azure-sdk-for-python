# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

"""
Multi-Tool Tests: Code Interpreter + Function Tool

Tests various scenarios using an agent with Code Interpreter and Function Tool.
All tests use the same tool combination but different inputs and workflows.
"""

import json
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, RecordedTransport
from azure.ai.projects.models import PromptAgentDefinition, CodeInterpreterTool, CodeInterpreterToolAuto, FunctionTool
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam

class TestAgentCodeInterpreterAndFunction(TestBase):
    """Tests for agents using Code Interpreter + Function Tool combination."""

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_calculate_and_save(self, **kwargs):
        """
        Test calculation with Code Interpreter and saving with Function Tool.

        This test verifies that both tools are used:
        1. Code Interpreter: Performs a calculation that requires actual computation
        2. Function Tool: Saves the computed result
        """

        model = self.test_agents_params["model_deployment_name"]

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Define function tool
        func_tool = FunctionTool(
            name="save_result",
            description="Save the calculation result. Must be called to persist the result.",
            parameters={
                "type": "object",
                "properties": {
                    "calculation": {"type": "string", "description": "Description of the calculation"},
                    "result": {"type": "string", "description": "The numerical result"},
                },
                "required": ["calculation", "result"],
                "additionalProperties": False,
            },
            strict=True,
        )

        # Create agent with explicit instructions to use both tools
        agent = project_client.agents.create_version(
            agent_name="code-func-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a calculator assistant. Use code interpreter to perform calculations, then ALWAYS save the result using the save_result function.",
                tools=[
                    CodeInterpreterTool(container=CodeInterpreterToolAuto()),
                    func_tool,
                ],
            ),
            description="Agent with Code Interpreter and Function Tool.",
        )
        print(f"Agent created (id: {agent.id})")

        # Request a calculation that requires Code Interpreter (not trivial math)
        # 17^4 = 83521 - not something easily computed mentally
        response = openai_client.responses.create(
            input="Calculate 17 to the power of 4 using code, then save the result.",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
        self.validate_response(response)
        print("✓ Code Interpreter + Function Tool works!")

        # Cleanup
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_generate_data_and_report(self, **kwargs):
        """
        Test generating data with Code Interpreter and reporting with Function.

        This test verifies that both tools are used:
        1. Code Interpreter: Generates random data and calculates statistics
        2. Function Tool: Creates a report with the computed statistics
        """

        model = self.test_agents_params["model_deployment_name"]

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Define function tool
        report_function = FunctionTool(
            name="generate_report",
            description="Generate and save a report with the analysis results. Must be called to create the report.",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Report title"},
                    "data_count": {"type": "integer", "description": "Number of data points analyzed"},
                    "average": {"type": "number", "description": "Calculated average value"},
                    "summary": {"type": "string", "description": "Summary of findings"},
                },
                "required": ["title", "data_count", "average", "summary"],
                "additionalProperties": False,
            },
            strict=True,
        )

        # Create agent with explicit instructions
        agent = project_client.agents.create_version(
            agent_name="code-func-report-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a data analyst. Use code interpreter to generate and analyze data, then ALWAYS create a report using the generate_report function with the exact statistics you computed.",
                tools=[
                    CodeInterpreterTool(container=CodeInterpreterToolAuto()),
                    report_function,
                ],
            ),
            description="Agent for data generation and reporting.",
        )
        print(f"Agent created (id: {agent.id})")

        # Request data generation and report - use a fixed seed for reproducibility in verification
        response = openai_client.responses.create(
            input="Using Python with random.seed(42), generate exactly 10 random integers between 1 and 100, calculate their average, and create a report with the results.",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )

        self.validate_response(response)
        print("✓ Data generation and reporting works!")

        # Cleanup
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
