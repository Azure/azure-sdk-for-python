# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import asyncio
from typing import Final
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import RecordedTransport, is_live, is_live_and_not_recording
from azure.core.exceptions import ResourceNotFoundError
from azure.ai.projects.models import (
    MemoryStoreDefaultDefinition,
    MemorySearchTool,
    PromptAgentDefinition,
    MemoryStoreDefaultOptions,
)


class TestAgentMemorySearchAsync(TestBase):

    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_agent_memory_search_async(self, **kwargs):

        model = kwargs.get("azure_ai_projects_tests_model_deployment_name")
        chat_model = kwargs.get("azure_ai_projects_tests_memory_store_chat_model_deployment_name")
        embedding_model = kwargs.get("azure_ai_projects_tests_memory_store_embedding_model_deployment_name")

        assert isinstance(model, str)
        assert isinstance(chat_model, str)
        assert isinstance(embedding_model, str)

        print(f"Using model: {model}")
        print(f"Using chat model: {chat_model}")
        print(f"Using embedding model: {embedding_model}")

        async with (
            self.create_async_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):

            # Initialize resource references for cleanup
            memory_store = None
            agent = None
            conversation = None
            new_conversation = None

            memory_store_name: Final[str] = "test_memory_store"
            agent_name: Final[str] = "memory-search-agent-async"
            scope: Final[str]  = "test_user_123"

            # Delete memory store, if it already exists. Do this cleaup only
            # in live mode so we don't get logs of this call in test recordings.
            if is_live_and_not_recording():
                try:
                    await project_client.memory_stores.delete(memory_store_name)
                    print(f"Memory store `{memory_store_name}` deleted")
                except ResourceNotFoundError:
                    pass

            try:
                # Create memory store with chat and embedding models
                definition = MemoryStoreDefaultDefinition(
                    chat_model=chat_model,
                    embedding_model=embedding_model,
                    options=MemoryStoreDefaultOptions(user_profile_enabled=True, chat_summary_enabled=True),
                )
                memory_store = await project_client.memory_stores.create(
                    name=memory_store_name,
                    description="Test memory store for agent conversations",
                    definition=definition,
                )
                print(f"\nMemory store created: {memory_store.name} (id: {memory_store.id})")
                assert memory_store.name == memory_store_name
                assert memory_store.id
                assert memory_store.description == "Test memory store for agent conversations"


                # Create memory search tool
                tool = MemorySearchTool(
                    memory_store_name=memory_store.name,
                    scope=scope,
                    update_delay=1,  # Wait 1 second for testing; use higher value (300) in production
                )

                # Create agent with memory search tool
                agent = await project_client.agents.create_version(
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
                conversation = await openai_client.conversations.create()
                print(f"First conversation created (id: {conversation.id})")
                assert conversation.id

                # Store user preference in memory
                print("\nStoring user preference in memory...")
                response = await openai_client.responses.create(
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
                    await asyncio.sleep(60)

                # Create a new conversation to test memory retrieval
                new_conversation = await openai_client.conversations.create()
                print(f"Second conversation created (id: {new_conversation.id})")
                assert new_conversation.id
                assert new_conversation.id != conversation.id, "New conversation should have different ID"

                # Query agent with information that should be retrieved from memory
                print("\nQuerying agent with stored memory context...")
                new_response = await openai_client.responses.create(
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

            finally:
                # Teardown - clean up resources even if test fails
                print("\nCleaning up...")
                cleanup_exception = None

                if conversation:
                    try:
                        await openai_client.conversations.delete(conversation.id)
                        print(f"First conversation deleted (id: {conversation.id})")
                    except Exception as e:
                        print(f"Failed to delete first conversation: {e}")
                        if cleanup_exception is None:
                            cleanup_exception = e

                if new_conversation:
                    try:
                        await openai_client.conversations.delete(new_conversation.id)
                        print(f"Second conversation deleted (id: {new_conversation.id})")
                    except Exception as e:
                        print(f"Failed to delete second conversation: {e}")
                        if cleanup_exception is None:
                            cleanup_exception = e

                if agent:
                    try:
                        await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
                        print("Agent deleted")
                    except Exception as e:
                        print(f"Failed to delete agent: {e}")
                        if cleanup_exception is None:
                            cleanup_exception = e

                if memory_store:
                    try:
                        await project_client.memory_stores.delete(memory_store.name)
                        print("Memory store deleted")
                    except Exception as e:
                        print(f"Failed to delete memory store: {e}")
                        if cleanup_exception is None:
                            cleanup_exception = e

                # Re-raise the first cleanup exception if any occurred
                if cleanup_exception:
                    raise cleanup_exception
