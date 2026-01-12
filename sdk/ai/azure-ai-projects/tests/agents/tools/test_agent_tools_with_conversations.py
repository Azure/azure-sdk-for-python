# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Test agents using tools within conversations.

This test file demonstrates how to use various agent tools (both server-side and client-side)
within the context of conversations, testing conversation state management with tool interactions.
"""

import json
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, RecordedTransport
from azure.ai.projects.models import (
    FunctionTool,
    FileSearchTool,
    CodeInterpreterTool,
    CodeInterpreterToolAuto,
    PromptAgentDefinition,
)
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam


class TestAgentToolsWithConversations(TestBase):

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_function_tool_with_conversation(self, **kwargs):
        """
        Test using FunctionTool within a conversation.

        This tests:
        - Creating a conversation
        - Multiple turns with function calls
        - Conversation state preservation across function calls
        - Using conversation_id parameter
        """

        model = kwargs.get("azure_ai_model_deployment_name")

        with (
            self.create_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Define a calculator function
            calculator = FunctionTool(
                name="calculator",
                description="Perform basic arithmetic operations",
                parameters={
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["add", "subtract", "multiply", "divide"],
                            "description": "The operation to perform",
                        },
                        "a": {"type": "number", "description": "First number"},
                        "b": {"type": "number", "description": "Second number"},
                    },
                    "required": ["operation", "a", "b"],
                    "additionalProperties": False,
                },
                strict=True,
            )

            # Create agent
            agent = project_client.agents.create_version(
                agent_name="calculator-agent-conversation",
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a calculator assistant. Use the calculator function to perform operations.",
                    tools=[calculator],
                ),
                description="Calculator agent for conversation testing.",
            )
            print(f"Agent created: {agent.id}")

            # Create conversation
            conversation = openai_client.conversations.create()
            print(f"Conversation created: {conversation.id}")

            # Turn 1: Add two numbers
            print("\n--- Turn 1: Addition ---")
            response_1 = openai_client.responses.create(
                input="What is 15 plus 27?",
                conversation=conversation.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            # Handle function call
            input_list: ResponseInputParam = []
            for item in response_1.output:
                if item.type == "function_call":
                    print(f"Function called: {item.name} with {item.arguments}")
                    args = json.loads(item.arguments)

                    # Execute calculator
                    result = {
                        "add": args["a"] + args["b"],
                        "subtract": args["a"] - args["b"],
                        "multiply": args["a"] * args["b"],
                        "divide": args["a"] / args["b"] if args["b"] != 0 else "Error: Division by zero",
                    }[args["operation"]]

                    input_list.append(
                        FunctionCallOutput(
                            type="function_call_output",
                            call_id=item.call_id,
                            output=json.dumps({"result": result}),
                        )
                    )

            response_1 = openai_client.responses.create(
                input=input_list,
                conversation=conversation.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )
            print(f"Response 1: {response_1.output_text[:100]}...")
            assert "42" in response_1.output_text

            # Turn 2: Follow-up using previous result (tests conversation memory)
            print("\n--- Turn 2: Follow-up using conversation context ---")
            response_2 = openai_client.responses.create(
                input="Now multiply that result by 2",
                conversation=conversation.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            # Handle function call
            input_list = []
            for item in response_2.output:
                if item.type == "function_call":
                    print(f"Function called: {item.name} with {item.arguments}")
                    args = json.loads(item.arguments)

                    # Should be multiplying 42 by 2
                    assert args["operation"] == "multiply"
                    assert args["a"] == 42 or args["b"] == 42

                    result = args["a"] * args["b"]
                    input_list.append(
                        FunctionCallOutput(
                            type="function_call_output",
                            call_id=item.call_id,
                            output=json.dumps({"result": result}),
                        )
                    )

            response_2 = openai_client.responses.create(
                input=input_list,
                conversation=conversation.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )
            print(f"Response 2: {response_2.output_text[:100]}...")
            assert "84" in response_2.output_text

            print("\n✓ Function tool with conversation successful!")
            print("  - Conversation preserved state across function calls")
            print("  - Agent remembered previous result (42)")

            # Verify conversation state by reading items
            print("\n--- Verifying conversation state ---")
            all_items = list(openai_client.conversations.items.list(conversation.id))
            print(f"Total conversation items: {len(all_items)}")

            # Count different item types
            user_messages = sum(1 for item in all_items if item.type == "message" and item.role == "user")
            assistant_messages = sum(1 for item in all_items if item.type == "message" and item.role == "assistant")
            function_calls = sum(1 for item in all_items if item.type == "function_call")
            function_outputs = sum(1 for item in all_items if item.type == "function_call_output")

            print(f"  User messages: {user_messages}")
            print(f"  Assistant messages: {assistant_messages}")
            print(f"  Function calls: {function_calls}")
            print(f"  Function outputs: {function_outputs}")

            # Verify we have expected items
            assert user_messages >= 2, "Expected at least 2 user messages (two turns)"
            assert function_calls >= 2, "Expected at least 2 function calls (one per turn)"
            assert function_outputs >= 2, "Expected at least 2 function outputs"
            print("✓ Conversation state verified - all items preserved")

            # Cleanup
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            openai_client.conversations.delete(conversation_id=conversation.id)
            print("Cleanup completed")

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_file_search_with_conversation(self, **kwargs):
        """
        Test using FileSearchTool within a conversation.

        This tests:
        - Server-side tool execution within conversation
        - Multiple search queries in same conversation
        - Conversation context retention
        """

        model = kwargs.get("azure_ai_model_deployment_name")

        with (
            self.create_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Create documents with related information
            doc_content = """Product Catalog

Widget A:
- Price: $100
- Stock: 50 units
- Rating: 4.5/5
- Category: Electronics

Widget B:
- Price: $220
- Stock: 30 units
- Rating: 4.8/5
- Category: Electronics

Widget C:
- Price: $75
- Stock: 100 units
- Rating: 4.2/5
- Category: Home Goods
"""

            # Create vector store and upload document
            vector_store = openai_client.vector_stores.create(name="ConversationTestStore")
            print(f"Vector store created: {vector_store.id}")

            from io import BytesIO

            file = BytesIO(doc_content.encode("utf-8"))
            file.name = "products.txt"

            uploaded = openai_client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=file,
            )
            print(f"Document uploaded: {uploaded.id}")

            # Create agent with file search
            agent = project_client.agents.create_version(
                agent_name="search-agent-conversation",
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a product search assistant. Answer questions about products.",
                    tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
                ),
                description="Search agent for conversation testing.",
            )
            print(f"Agent created: {agent.id}")

            # Create conversation
            conversation = openai_client.conversations.create()
            print(f"Conversation created: {conversation.id}")

            # Turn 1: Search for highest rated
            print("\n--- Turn 1: Search query ---")
            response_1 = openai_client.responses.create(
                input="Which widget has the highest rating?",
                conversation=conversation.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            response_1_text = response_1.output_text
            print(f"Response 1: {response_1_text[:150]}...")
            assert "Widget B" in response_1_text or "4.8" in response_1_text

            # Turn 2: Follow-up about that specific product (tests context retention)
            print("\n--- Turn 2: Contextual follow-up ---")
            response_2 = openai_client.responses.create(
                input="What is its price?",  # "its" refers to Widget B from previous turn
                conversation=conversation.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            response_2_text = response_2.output_text
            print(f"Response 2: {response_2_text[:150]}...")
            assert "220" in response_2_text

            # Turn 3: New search in same conversation
            print("\n--- Turn 3: New search in same conversation ---")
            response_3 = openai_client.responses.create(
                input="Which widget is in the Home Goods category?",
                conversation=conversation.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            response_3_text = response_3.output_text
            print(f"Response 3: {response_3_text[:150]}...")
            assert "Widget C" in response_3_text

            print("\n✓ File search with conversation successful!")
            print("  - Multiple searches in same conversation")
            print("  - Context preserved (agent remembered Widget B)")

            # Cleanup
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            openai_client.conversations.delete(conversation_id=conversation.id)
            openai_client.vector_stores.delete(vector_store.id)
            print("Cleanup completed")

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_code_interpreter_with_conversation(self, **kwargs):
        """
        Test using CodeInterpreterTool within a conversation.

        This tests:
        - Server-side code execution within conversation
        - Multiple code executions in same conversation
        - Variables/state persistence across turns
        """

        model = kwargs.get("azure_ai_model_deployment_name")

        with (
            self.create_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Create agent with code interpreter
            agent = project_client.agents.create_version(
                agent_name="code-agent-conversation",
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a data analysis assistant. Use Python to perform calculations.",
                    tools=[CodeInterpreterTool(container=CodeInterpreterToolAuto(file_ids=[]))],
                ),
                description="Code interpreter agent for conversation testing.",
            )
            print(f"Agent created: {agent.id}")

            # Create conversation
            conversation = openai_client.conversations.create()
            print(f"Conversation created: {conversation.id}")

            # Turn 1: Calculate average
            print("\n--- Turn 1: Calculate average ---")
            response_1 = openai_client.responses.create(
                input="Calculate the average of these numbers: 10, 20, 30, 40, 50",
                conversation=conversation.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            response_1_text = response_1.output_text
            print(f"Response 1: {response_1_text[:200]}...")
            assert "30" in response_1_text

            # Turn 2: Follow-up calculation (tests conversation context)
            print("\n--- Turn 2: Follow-up calculation ---")
            response_2 = openai_client.responses.create(
                input="Now calculate the standard deviation of those same numbers",
                conversation=conversation.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            response_2_text = response_2.output_text
            print(f"Response 2: {response_2_text[:200]}...")
            # Standard deviation should be approximately 14.14 or similar
            assert any(num in response_2_text for num in ["14", "15", "standard"])

            # Turn 3: Another operation in same conversation
            print("\n--- Turn 3: New calculation ---")
            response_3 = openai_client.responses.create(
                input="Create a list of squares from 1 to 5",
                conversation=conversation.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            response_3_text = response_3.output_text
            print(f"Response 3: {response_3_text[:200]}...")
            assert "1" in response_3_text and "4" in response_3_text and "25" in response_3_text

            print("\n✓ Code interpreter with conversation successful!")
            print("  - Multiple code executions in conversation")
            print("  - Context preserved across calculations")

            # Cleanup
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            openai_client.conversations.delete(conversation_id=conversation.id)
            print("Cleanup completed")

    # To run this test only:
    # pytest tests/agents/tools/test_agent_tools_with_conversations.py::TestAgentToolsWithConversations::test_code_interpreter_with_file_in_conversation -s
    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_code_interpreter_with_file_in_conversation(self, **kwargs):
        """
        Test using CodeInterpreterTool with file upload within a conversation.

        This test reproduces the 500 error seen in the sample when using
        code interpreter with uploaded files in conversations.

        This tests:
        - Uploading a real file (not BytesIO) for code interpreter
        - Using code interpreter with files in conversation
        - Server-side code execution with file access and chart generation
        """

        model = kwargs.get("azure_ai_model_deployment_name")
        import os

        with (
            self.create_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Use the same CSV file as the sample
            asset_file_path = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "../../../samples/agents/assets/synthetic_500_quarterly_results.csv",
                )
            )

            # Upload file using open() with rb mode, just like the sample
            with self.open_with_lf(asset_file_path, "rb") as f:
                uploaded_file = openai_client.files.create(file=f, purpose="assistants")
            print(f"File uploaded: {uploaded_file.id}")

            # Create agent with code interpreter - matching sample exactly
            agent = project_client.agents.create_version(
                agent_name="agent-code-interpreter-with-file",
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a helpful assistant.",
                    tools=[CodeInterpreterTool(container=CodeInterpreterToolAuto(file_ids=[uploaded_file.id]))],
                ),
                description="Code interpreter agent for data analysis and visualization.",
            )
            print(f"Agent created: {agent.id}")

            # Create conversation
            conversation = openai_client.conversations.create()
            print(f"Conversation created: {conversation.id}")

            # Use the same prompt as the sample - requesting chart generation
            print("\n--- Turn 1: Create bar chart ---")
            response_1 = openai_client.responses.create(
                conversation=conversation.id,
                input="Could you please create bar chart in TRANSPORTATION sector for the operating profit from the uploaded csv file and provide file to me?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            response_1_text = response_1.output_text
            print(f"Response 1: {response_1_text[:200]}...")

            print("\n✓ Code interpreter with file in conversation successful!")

            # Cleanup
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            openai_client.conversations.delete(conversation_id=conversation.id)
            openai_client.files.delete(uploaded_file.id)
            print("Cleanup completed")
