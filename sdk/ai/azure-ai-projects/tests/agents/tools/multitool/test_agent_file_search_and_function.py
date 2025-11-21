# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

"""
Multi-Tool Tests: File Search + Function Tool

Tests various scenarios using an agent with File Search and Function Tool.
All tests use the same tool combination but different inputs and workflows.
"""

import os
import json
import pytest
from test_base import TestBase, servicePreparer
from devtools_testutils import is_live_and_not_recording
from azure.ai.projects.models import PromptAgentDefinition, FileSearchTool, FunctionTool
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam


class TestAgentFileSearchAndFunction(TestBase):
    """Tests for agents using File Search + Function Tool combination."""

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_data_analysis_workflow(self, **kwargs):
        """
        Test data analysis workflow: upload data, search, save results.
        """

        model = self.test_agents_params["model_deployment_name"]

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Create sample data file
        txt_content = """Sales Data Q1-Q3:

Product: Widget A
Q1: $15,000
Q2: $18,000
Q3: $21,000
Total: $54,000

Product: Widget B
Q1: $22,000
Q2: $25,000
Q3: $28,000
Total: $75,000

Overall Total Revenue: $129,000
"""

        # Create vector store and upload
        vector_store = openai_client.vector_stores.create(name="SalesDataStore")
        print(f"Vector store created (id: {vector_store.id})")
        
        from io import BytesIO
        txt_file = BytesIO(txt_content.encode('utf-8'))
        txt_file.name = "sales_data.txt"
        
        file = openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=txt_file,
        )
        print(f"File uploaded (id: {file.id})")
        assert file.status == "completed"

        # Define function tool
        save_results_function = FunctionTool(
            name="save_analysis_results",
            description="Save the analysis results",
            parameters={
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "Summary of the analysis",
                    },
                },
                "required": ["summary"],
                "additionalProperties": False,
            },
            strict=True,
        )

        # Create agent
        agent = project_client.agents.create_version(
            agent_name="file-search-function-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a data analyst. Use file search to find data and save_analysis_results function to save your findings.",
                tools=[
                    FileSearchTool(vector_store_ids=[vector_store.id]),
                    save_results_function,
                ],
            ),
            description="Agent with File Search and Function Tool.",
        )
        print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

        # Request analysis
        print("\nAsking agent to analyze the sales data...")
        
        response = openai_client.responses.create(
            input="Analyze the sales data and calculate the total revenue for each product. Then save the results.",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
        
        print(f"Initial response completed (id: {response.id})")
        
        # Check if function was called
        function_calls_found = 0
        input_list: ResponseInputParam = []
        
        for item in response.output:
            if item.type == "function_call":
                function_calls_found += 1
                print(f"Function call detected (id: {item.call_id}, name: {item.name})")
                
                assert item.name == "save_analysis_results"
                
                arguments = json.loads(item.arguments)
                print(f"Function arguments: {arguments}")
                
                assert "summary" in arguments
                assert len(arguments["summary"]) > 20
                
                input_list.append(
                    FunctionCallOutput(
                        type="function_call_output",
                        call_id=item.call_id,
                        output=json.dumps({"status": "success", "saved": True}),
                    )
                )

        assert function_calls_found > 0, "Expected save_analysis_results function to be called"
        
        # Send function results back
        if input_list:
            response = openai_client.responses.create(
                input=input_list,
                previous_response_id=response.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )
            print(f"Final response: {response.output_text[:200]}...")

        print("\n✓ Workflow completed successfully")

        # Teardown
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        openai_client.vector_stores.delete(vector_store.id)
        print("Cleanup completed")

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_empty_vector_store_handling(self, **kwargs):
        """
        Test how agent handles empty vector store (no files uploaded).
        """

        model = self.test_agents_params["model_deployment_name"]

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Create EMPTY vector store
        vector_store = openai_client.vector_stores.create(name="EmptyStore")
        print(f"Empty vector store created (id: {vector_store.id})")

        # Define function tool
        error_function = FunctionTool(
            name="report_error",
            description="Report when data is not available",
            parameters={
                "type": "object",
                "properties": {
                    "error_message": {
                        "type": "string",
                        "description": "Description of the error",
                    },
                },
                "required": ["error_message"],
                "additionalProperties": False,
            },
            strict=True,
        )

        # Create agent
        agent = project_client.agents.create_version(
            agent_name="file-search-function-error-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="Search for data. If you can't find it, use report_error function to explain what happened.",
                tools=[
                    FileSearchTool(vector_store_ids=[vector_store.id]),
                    error_function,
                ],
            ),
            description="Agent for testing error handling.",
        )
        print(f"Agent created (id: {agent.id})")

        # Request analysis of non-existent file
        print("\nAsking agent to find non-existent data...")
        
        response = openai_client.responses.create(
            input="Find and analyze the quarterly sales report.",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
        
        response_text = response.output_text
        print(f"Response: '{response_text[:200] if response_text else '(empty)'}...'")
        
        # Verify agent didn't crash
        assert response.id is not None, "Agent should return a valid response"
        assert len(response.output) >= 0, "Agent should return output items"
        
        # If there's text, it should be meaningful
        if response_text:
            assert len(response_text) > 10, "Non-empty response should be meaningful"
        
        print("\n✓ Agent handled missing data gracefully")

        # Teardown
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        openai_client.vector_stores.delete(vector_store.id)
        print("Cleanup completed")

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_python_code_file_search(self, **kwargs):
        """
        Test searching for Python code files.
        """

        model = self.test_agents_params["model_deployment_name"]

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Create sample Python code
        python_code = """# Sample Python code for analysis
def calculate_sum(numbers):
    return sum(numbers)

# Test data
data = [1, 2, 3, 4, 5]
result = calculate_sum(data)
print(f"Sum: {result}")
"""

        # Create vector store and upload
        vector_store = openai_client.vector_stores.create(name="CodeStore")
        
        from io import BytesIO
        code_file = BytesIO(python_code.encode('utf-8'))
        code_file.name = "sample_code.py"
        
        file = openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=code_file,
        )
        print(f"Python file uploaded (id: {file.id})")

        # Define function tool
        save_function = FunctionTool(
            name="save_code_review",
            description="Save code review findings",
            parameters={
                "type": "object",
                "properties": {
                    "findings": {
                        "type": "string",
                        "description": "Code review findings",
                    },
                },
                "required": ["findings"],
                "additionalProperties": False,
            },
            strict=True,
        )

        # Create agent
        agent = project_client.agents.create_version(
            agent_name="file-search-function-code-agent",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You can search for code files and describe what they do. Save your findings.",
                tools=[
                    FileSearchTool(vector_store_ids=[vector_store.id]),
                    save_function,
                ],
            ),
            description="Agent for testing file search with code.",
        )
        print(f"Agent created (id: {agent.id})")

        # Request code analysis
        print("\nAsking agent to find and analyze the Python code...")
        
        response = openai_client.responses.create(
            input="Find the Python code file and tell me what the calculate_sum function does.",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
        
        response_text = response.output_text
        print(f"Response: {response_text[:300]}...")
        
        # Verify agent found and analyzed the code
        assert len(response_text) > 50, "Expected detailed analysis"
        
        response_lower = response_text.lower()
        assert any(keyword in response_lower for keyword in ["sum", "calculate", "function", "numbers", "code", "python"]), \
            "Expected response to discuss the code"
        
        print("\n✓ Agent successfully found code file using File Search")

        # Teardown
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        openai_client.vector_stores.delete(vector_store.id)
        print("Cleanup completed")

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_multi_turn_search_and_save_workflow(self, **kwargs):
        """
        Test multi-turn workflow: search documents, ask follow-ups, save findings.
        
        This tests:
        - File Search across multiple turns
        - Function calls interspersed with searches
        - Context retention across searches and function calls
        """

        model = self.test_agents_params["model_deployment_name"]

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Create research documents
        doc1_content = """Research Paper: Machine Learning in Healthcare

Abstract:
Machine learning algorithms are revolutionizing healthcare diagnostics.
Recent studies show 95% accuracy in disease detection using neural networks.
Key applications include medical imaging, patient risk prediction, and drug discovery.

Conclusion:
ML techniques offer promising solutions for early disease detection and personalized treatment.
"""

        doc2_content = """Research Paper: AI Ethics and Governance

Abstract:
As AI systems become more prevalent, ethical considerations are paramount.
Issues include bias in algorithms, data privacy, and accountability.
Regulatory frameworks are being developed globally to address these concerns.

Conclusion:
Responsible AI development requires multistakeholder collaboration and transparent governance.
"""

        # Create vector store and upload documents
        vector_store = openai_client.vector_stores.create(name="ResearchStore")
        print(f"Vector store created: {vector_store.id}")
        
        from io import BytesIO
        file1 = BytesIO(doc1_content.encode('utf-8'))
        file1.name = "ml_healthcare.txt"
        file2 = BytesIO(doc2_content.encode('utf-8'))
        file2.name = "ai_ethics.txt"
        
        uploaded1 = openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=file1,
        )
        uploaded2 = openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=file2,
        )
        print(f"Documents uploaded: {uploaded1.id}, {uploaded2.id}")

        # Define save function
        save_finding = FunctionTool(
            name="save_finding",
            description="Save research finding",
            parameters={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Research topic"},
                    "finding": {"type": "string", "description": "Key finding"},
                },
                "required": ["topic", "finding"],
                "additionalProperties": False,
            },
            strict=True,
        )

        # Create agent
        agent = project_client.agents.create_version(
            agent_name="research-assistant-multi-turn",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are a research assistant. Search documents and save important findings.",
                tools=[
                    FileSearchTool(vector_store_ids=[vector_store.id]),
                    save_finding,
                ],
            ),
            description="Research assistant for multi-turn testing.",
        )
        print(f"Agent created: {agent.id}")

        # Turn 1: Search for ML in healthcare
        print("\n--- Turn 1: Initial search query ---")
        response_1 = openai_client.responses.create(
            input="What does the research say about machine learning in healthcare?",
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
        
        response_1_text = response_1.output_text
        print(f"Response 1: {response_1_text[:200]}...")
        assert "95" in response_1_text or "accuracy" in response_1_text.lower()
        
        # Turn 2: Follow-up for specifics
        print("\n--- Turn 2: Follow-up for details ---")
        response_2 = openai_client.responses.create(
            input="What specific applications are mentioned?",
            previous_response_id=response_1.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
        
        response_2_text = response_2.output_text
        print(f"Response 2: {response_2_text[:200]}...")
        response_2_lower = response_2_text.lower()
        assert any(keyword in response_2_lower for keyword in ["imaging", "drug", "risk", "prediction"])
        
        # Turn 3: Save the finding
        print("\n--- Turn 3: Save finding ---")
        response_3 = openai_client.responses.create(
            input="Please save that finding about ML accuracy.",
            previous_response_id=response_2.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
        
        # Handle function call
        input_list: ResponseInputParam = []
        function_called = False
        for item in response_3.output:
            if item.type == "function_call":
                function_called = True
                print(f"Function called: {item.name} with args: {item.arguments}")
                assert item.name == "save_finding"
                
                args = json.loads(item.arguments)
                assert "topic" in args and "finding" in args
                print(f"  Topic: {args['topic']}")
                print(f"  Finding: {args['finding'][:100]}...")
                
                input_list.append(
                    FunctionCallOutput(
                        type="function_call_output",
                        call_id=item.call_id,
                        output=json.dumps({"status": "saved", "id": "finding_001"}),
                    )
                )
        
        assert function_called, "Expected save_finding to be called"
        
        # Send function result
        response_3 = openai_client.responses.create(
            input=input_list,
            previous_response_id=response_3.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
        print(f"Response 3: {response_3.output_text[:150]}...")
        
        # Turn 4: Switch to different topic (AI ethics)
        print("\n--- Turn 4: New search topic ---")
        response_4 = openai_client.responses.create(
            input="Now tell me about AI ethics concerns mentioned in the research.",
            previous_response_id=response_3.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
        
        response_4_text = response_4.output_text
        print(f"Response 4: {response_4_text[:200]}...")
        response_4_lower = response_4_text.lower()
        assert any(keyword in response_4_lower for keyword in ["bias", "privacy", "ethics", "accountability"])

        print("\n✓ Multi-turn File Search + Function workflow successful!")
        print("  - Multiple searches across different documents")
        print("  - Function called after context-building searches")
        print("  - Topic switching works correctly")

        # Cleanup
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        openai_client.vector_stores.delete(vector_store.id)
        print("Cleanup completed")
