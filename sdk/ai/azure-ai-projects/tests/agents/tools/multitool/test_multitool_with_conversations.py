# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Test agents using multiple tools within conversations.

This test file demonstrates how to use multiple agent tools (both server-side and client-side)
within the context of conversations, testing conversation state management with multi-tool interactions.
"""

import json
import pytest
from test_base import TestBase, servicePreparer
from devtools_testutils import is_live_and_not_recording
from azure.ai.projects.models import (
    FunctionTool,
    FileSearchTool,
    PromptAgentDefinition,
)
from openai.types.responses.response_input_param import FunctionCallOutput, ResponseInputParam


class TestMultiToolWithConversations(TestBase):

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_file_search_and_function_with_conversation(self, **kwargs):
        """
        Test using multiple tools (FileSearch + Function) within one conversation.

        This tests:
        - Mixing FileSearch (server-side) and Function (client-side) tools in same conversation
        - Complex multi-turn workflow with different tool types
        - Conversation managing state across different tool executions
        - Verifying conversation state preserves all tool interactions
        """

        model = self.test_agents_params["model_deployment_name"]

        # Setup
        project_client = self.create_client(operation_group="agents", **kwargs)
        openai_client = project_client.get_openai_client()

        # Create document
        doc_content = """Sales Data Q1 2024

Product A: $45,000
Product B: $67,000
Product C: $32,000

Total Revenue: $144,000
"""

        vector_store = openai_client.vector_stores.create(name="SalesDataStore")
        from io import BytesIO

        file = BytesIO(doc_content.encode("utf-8"))
        file.name = "sales.txt"
        openai_client.vector_stores.files.upload_and_poll(vector_store_id=vector_store.id, file=file)
        print(f"Vector store created: {vector_store.id}")

        # Define save function
        save_report = FunctionTool(
            name="save_report",
            description="Save a report summary. Use this when explicitly asked to perform a save operation.",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                },
                "required": ["title", "summary"],
                "additionalProperties": False,
            },
            strict=True,
        )

        # Create agent with both tools
        agent = project_client.agents.create_version(
            agent_name="mixed-tools-conversation",
            definition=PromptAgentDefinition(
                model=model,
                instructions="You are an analyst. Search data to answer questions and save reports when instructed",
                tools=[
                    FileSearchTool(vector_store_ids=[vector_store.id]),
                    save_report,
                ],
            ),
            description="Mixed tools agent for conversation testing.",
        )
        print(f"Agent created: {agent.id}")

        # Create conversation
        conversation = openai_client.conversations.create()
        print(f"Conversation created: {conversation.id}")

        # Turn 1: Search (server-side tool)
        print("\n--- Turn 1: File Search ---")
        response_1 = openai_client.responses.create(
            input="What was the total revenue in Q1 2024?",
            conversation=conversation.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )

        print(f"Response 1: {response_1.output_text[:150]}...")
        assert "144,000" in response_1.output_text or "144000" in response_1.output_text

        # Turn 2: Follow-up search
        print("\n--- Turn 2: Follow-up search ---")
        response_2 = openai_client.responses.create(
            input="Which product had the highest sales?",
            conversation=conversation.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )

        print(f"Response 2: {response_2.output_text[:150]}...")
        assert "Product B" in response_2.output_text or "67,000" in response_2.output_text

        # Turn 3: Save report (client-side tool)
        print("\n--- Turn 3: Save report using function ---")
        response_3 = openai_client.responses.create(
            input="Save a summary report of these Q1 results",
            conversation=conversation.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )

        # Handle function call
        input_list: ResponseInputParam = []
        for item in response_3.output:
            if item.type == "function_call":
                print(f"Function called: {item.name}")
                args = json.loads(item.arguments)
                print(f"  Title: {args['title']}")
                print(f"  Summary: {args['summary'][:100]}...")

                input_list.append(
                    FunctionCallOutput(
                        type="function_call_output",
                        call_id=item.call_id,
                        output=json.dumps({"status": "saved", "report_id": "Q1_2024"}),
                    )
                )

        response_3 = openai_client.responses.create(
            input=input_list,
            conversation=conversation.id,
            extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
        )
        print(f"Response 3: {response_3.output_text[:150]}...")

        print("\n✓ Mixed tools with conversation successful!")
        print("  - File search (server-side) worked")
        print("  - Function call (client-side) worked")
        print("  - Both tools used in same conversation")

        # Verify conversation state with multiple tool types
        print("\n--- Verifying multi-tool conversation state ---")
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

        # Print item sequence to show tool interleaving
        print("\n  Conversation item sequence:")
        for i, item in enumerate(all_items, 1):
            if item.type == "message":
                content_preview = str(item.content[0] if item.content else "")[:50]
                print(f"    {i}. {item.type} ({item.role}): {content_preview}...")
            else:
                print(f"    {i}. {item.type}")

        # Verify we have items from all three turns
        assert user_messages >= 3, "Expected at least 3 user messages (three turns)"
        assert assistant_messages >= 3, "Expected assistant responses for each turn"
        assert function_calls >= 1, "Expected at least 1 function call (save_report)"
        assert function_outputs >= 1, "Expected at least 1 function output"

        print("\n✓ Multi-tool conversation state verified")
        print("  - Both server-side (FileSearch) and client-side (Function) tools tracked")
        print("  - All 3 turns preserved in conversation")

        # Cleanup
        project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        openai_client.conversations.delete(conversation_id=conversation.id)
        openai_client.vector_stores.delete(vector_store.id)
        print("Cleanup completed")
