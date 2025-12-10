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

from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, RecordedTransport
from azure.ai.projects.models import PromptAgentDefinition, CodeInterpreterTool, CodeInterpreterToolAuto, FunctionTool


class TestAgentCodeInterpreterAndFunction(TestBase):
    """Tests for agents using Code Interpreter + Function Tool combination."""

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_calculate_and_save(self, **kwargs):
        """
        Test calculation with Code Interpreter and saving with Function Tool.
        """

        model = self.test_agents_params["model_deployment_name"]

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Define function tool
        func_tool = FunctionTool(
            name="save_result",
            description="Save analysis result",
            parameters={
                "type": "object",
                "properties": {
                    "result": {"type": "string", "description": "The result"},
                },
                "required": ["result"],
                "additionalProperties": False,
            },
            strict=True,
        )

        # Create agent
        agent = project_client.agents.create_version(
            agent_name="code-func-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="Run calculations and save results.",
                tools=[
                    CodeInterpreterTool(container=CodeInterpreterToolAuto()),
                    func_tool,
                ],
            ),
            description="Agent with Code Interpreter and Function Tool.",
        )
        print(f"Agent created (id: {agent.id})")

        # Use the agent
        response = openai_client.responses.create(
            input="Calculate 5 + 3 and save the result.",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
        print(f"Response received (id: {response.id})")

        assert response.id is not None
        print("✓ Code Interpreter + Function Tool works!")

        # Cleanup
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_generate_data_and_report(self, **kwargs):
        """
        Test generating data with Code Interpreter and reporting with Function.
        """

        model = self.test_agents_params["model_deployment_name"]

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Define function tool
        report_function = FunctionTool(
            name="generate_report",
            description="Generate a report with the provided data",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Report title"},
                    "summary": {"type": "string", "description": "Report summary"},
                },
                "required": ["title", "summary"],
                "additionalProperties": False,
            },
            strict=True,
        )

        # Create agent
        agent = project_client.agents.create_version(
            agent_name="code-func-report-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="Generate data using code and create reports with the generate_report function.",
                tools=[
                    CodeInterpreterTool(container=CodeInterpreterToolAuto()),
                    report_function,
                ],
            ),
            description="Agent for data generation and reporting.",
        )
        print(f"Agent created (id: {agent.id})")

        # Request data generation and report
        response = openai_client.responses.create(
            input="Generate a list of 10 random numbers between 1 and 100, calculate their average, and create a report.",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )

        print(f"Response received (id: {response.id})")
        assert response.id is not None
        print("✓ Data generation and reporting works!")

        # Cleanup
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
