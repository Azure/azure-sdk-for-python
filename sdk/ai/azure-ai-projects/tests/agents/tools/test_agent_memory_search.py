# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import time
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, RecordedTransport, is_live
from azure.ai.projects.models import (
    MemoryStoreDefaultDefinition,
    MemorySearchTool,
    PromptAgentDefinition,
    MemoryStoreDefaultOptions,
)


class TestAgentMemorySearch(TestBase):

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agent_memory_search(self, **kwargs):
        """
        Test agent with Memory Search tool for contextual memory retrieval.

        This test verifies that an agent can:
        1. Create a memory store with chat and embedding models
        2. Use MemorySearchTool to store user preferences/information
        3. Retrieve stored memories across different conversations
        4. Answer questions based on previously stored context

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------
        # Setup:
        POST   /memory_stores                                project_client.memory_stores.create()
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()
        POST   /conversations                                openai_client.conversations.create()

        # Test focus:
        POST   /openai/responses                             openai_client.responses.create() (with MemorySearchTool)

        # Teardown:
        DELETE /conversations/{conversation_id}              openai_client.conversations.delete()
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        DELETE /memory_stores/{memory_store_name}            project_client.memory_stores.delete()
        """

        memory_store_name = "test_memory_store"

        model = kwargs.get("azure_ai_projects_tests_model_deployment_name")
        chat_model = kwargs.get("azure_ai_projects_tests_memory_store_chat_model_deployment_name")
        embedding_model = kwargs.get("azure_ai_projects_tests_memory_store_embedding_model_deployment_name")

        assert isinstance(model, str)
        assert isinstance(chat_model, str)
        assert isinstance(embedding_model, str)

        with (
            self.create_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):

            # Create memory store with chat and embedding models
            definition = MemoryStoreDefaultDefinition(
                chat_model=chat_model,
                embedding_model=embedding_model,
                options=MemoryStoreDefaultOptions(user_profile_enabled=True, chat_summary_enabled=True),
            )
            memory_store = project_client.memory_stores.create(
                name=memory_store_name,
                description="Test memory store for agent conversations",
                definition=definition,
            )
            print(f"Memory store created: {memory_store.name} (id: {memory_store.id})")
            assert memory_store.name == memory_store_name
            assert memory_store.id
            assert memory_store.description == "Test memory store for agent conversations"

            # Define scope for memory association
            scope = "test_user_123"

            # Create memory search tool
            tool = MemorySearchTool(
                memory_store_name=memory_store.name,
                scope=scope,
                update_delay=1,  # Wait 1 second for testing; use higher value (300) in production
            )

            # Create agent with memory search tool
            agent_name = "memory-search-agent"
            agent = project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a helpful assistant that remembers user preferences and answers questions based on past conversations.",
                    tools=[tool],
                ),
                description="Agent for testing memory search capabilities.",
            )
            self._validate_agent_version(agent, expected_name=agent_name)

            # Create first conversation to store user preferences
            conversation = openai_client.conversations.create()
            print(f"First conversation created (id: {conversation.id})")
            assert conversation.id

            # Store user preference in memory
            print("\nStoring user preference in memory...")
            response = openai_client.responses.create(
                input="I prefer dark roast coffee",
                conversation=conversation.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )
            self.validate_response(response)

            response_text = response.output_text
            print(f"Agent's response: {response_text[:200]}...")
            assert len(response_text) > 10, "Expected a meaningful response from the agent"

            # Wait for memories to be extracted and stored
            # In a real scenario, this happens after inactivity period (update_delay)
            print("\nWaiting for memories to be stored (this may take up to 60 seconds)...")
            if is_live():
                time.sleep(60)

            # Create a new conversation to test memory retrieval
            new_conversation = openai_client.conversations.create()
            print(f"Second conversation created (id: {new_conversation.id})")
            assert new_conversation.id
            assert new_conversation.id != conversation.id, "New conversation should have different ID"

            # Query agent with information that should be retrieved from memory
            print("\nQuerying agent with stored memory context...")
            new_response = openai_client.responses.create(
                input="Please order my usual coffee",
                conversation=new_conversation.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )
            self.validate_response(new_response)

            new_response_text = new_response.output_text
            print(f"Agent's response: {new_response_text[:300]}...")
            assert len(new_response_text) > 10, "Expected a meaningful response from the agent"

            # Verify that the response references the stored preference
            # The agent should mention "dark roast" or similar based on memory
            response_lower = new_response_text.lower()
            assert "dark roast" in response_lower, "Agent should recall the user's coffee preference from memory"

            print("\n✓ Agent successfully stored and retrieved memory across conversations")

            # Teardown
            print("\nCleaning up...")
            openai_client.conversations.delete(conversation.id)
            print(f"First conversation deleted (id: {conversation.id})")

            openai_client.conversations.delete(new_conversation.id)
            print(f"Second conversation deleted (id: {new_conversation.id})")

            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")

            project_client.memory_stores.delete(memory_store.name)
            print("Memory store deleted")
