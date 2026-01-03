# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import os
from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, RecordedTransport
from azure.ai.projects.models import PromptAgentDefinition, FileSearchTool


class TestAgentFileSearchStream(TestBase):

    @servicePreparer()
    @recorded_by_proxy(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    def test_agent_file_search_stream(self, **kwargs):
        """
        Test agent with File Search tool using streaming responses.

        This test verifies that an agent can:
        1. Upload and index documents into a vector store
        2. Use FileSearchTool with streaming enabled
        3. Stream back responses based on document content

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------
        # Setup:
        POST   /vector_stores                                openai_client.vector_stores.create()
        POST   /vector_stores/{id}/files                     openai_client.vector_stores.files.upload_and_poll()
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()

        # Test focus:
        POST   /openai/responses                             openai_client.responses.create() (stream=True, with FileSearchTool)

        # Teardown:
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        DELETE /vector_stores/{id}                           openai_client.vector_stores.delete()
        """

        model = kwargs.get("AZURE_AI_MODEL_DEPLOYMENT_NAME")

        with (
            self.create_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Get the path to the test file
            asset_file_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../../samples/agents/assets/product_info.md")
            )

            assert os.path.exists(asset_file_path), f"Test file not found at: {asset_file_path}"
            print(f"Using test file: {asset_file_path}")

            # Create vector store for file search
            vector_store = openai_client.vector_stores.create(name="ProductInfoStoreStream")
            print(f"Vector store created (id: {vector_store.id})")
            assert vector_store.id

            # Upload file to vector store
            with self.open_with_lf(asset_file_path, "rb") as f:
                file = openai_client.vector_stores.files.upload_and_poll(
                    vector_store_id=vector_store.id,
                    file=f,
                )

            print(f"File uploaded (id: {file.id}, status: {file.status})")
            assert file.id
            assert file.status == "completed", f"Expected file status 'completed', got '{file.status}'"

            # Create agent with file search tool
            agent_name = "file-search-stream-agent"
            agent = project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a helpful assistant that can search through uploaded documents to answer questions.",
                    tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
                ),
                description="Agent for testing file search with streaming.",
            )
            self._validate_agent_version(agent, expected_name=agent_name)

            # Ask a question with streaming enabled
            print("\nAsking agent about the product information (streaming)...")

            stream_response = openai_client.responses.create(
                stream=True,
                input="What products are mentioned in the document? Please provide a brief summary.",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            # Collect streamed response
            response_text = ""
            response_id = None
            events_received = 0

            for event in stream_response:
                events_received += 1

                if event.type == "response.output_item.done":
                    if event.item.type == "message":
                        for content_item in event.item.content:
                            if content_item.type == "output_text":
                                response_text += content_item.text

                elif event.type == "response.completed":
                    response_id = event.response.id
                    # Could also use event.response.output_text

            print(f"\nStreaming completed (id: {response_id}, events: {events_received})")
            assert response_id is not None, "Expected response ID from stream"
            assert events_received > 0, "Expected to receive stream events"

            print(f"Agent's streamed response: {response_text[:300]}...")

            # Verify we got a meaningful response
            assert len(response_text) > 50, "Expected a substantial response from the agent"

            print("\n✓ Agent successfully streamed responses using file search tool")

            # Teardown
            print("\nCleaning up...")
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")

            openai_client.vector_stores.delete(vector_store.id)
            print("Vector store deleted")
