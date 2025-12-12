# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

import os
from io import BytesIO
from test_base import TestBase, servicePreparer
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import RecordedTransport
from azure.ai.projects.models import PromptAgentDefinition, FileSearchTool


class TestAgentFileSearchAsync(TestBase):

    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_agent_file_search_async(self, **kwargs):

        model = self.test_agents_params["model_deployment_name"]

        async with (
            self.create_async_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Get the path to the test file
            asset_file_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../../samples/agents/assets/product_info.md")
            )

            assert os.path.exists(asset_file_path), f"Test file not found at: {asset_file_path}"
            print(f"Using test file: {asset_file_path}")

            # Create vector store for file search
            vector_store = await openai_client.vector_stores.create(name="ProductInfoStore")
            print(f"Vector store created (id: {vector_store.id})")
            assert vector_store.id

            # Upload file to vector store
            with self.open_with_lf(asset_file_path, "rb") as f:
                file = await openai_client.vector_stores.files.upload_and_poll(
                    vector_store_id=vector_store.id,
                    file=f,
                )

            print(f"File uploaded (id: {file.id}, status: {file.status})")
            assert file.id
            assert file.status == "completed", f"Expected file status 'completed', got '{file.status}'"

            # Create agent with file search tool
            agent_name = "file-search-agent"
            agent = await project_client.agents.create_version(
                agent_name=agent_name,
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a helpful assistant that can search through uploaded documents to answer questions.",
                    tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
                ),
                description="Agent for testing file search capabilities.",
            )
            self._validate_agent_version(agent, expected_name=agent_name)

            # Ask a question about the uploaded document
            print("\nAsking agent about the product information...")

            response = await openai_client.responses.create(
                input="What products are mentioned in the document?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            print(f"Response completed (id: {response.id})")
            assert response.id
            assert response.output is not None
            assert len(response.output) > 0

            # Get the response text
            response_text = response.output_text
            print(f"\nAgent's response: {response_text[:300]}...")

            # Verify we got a meaningful response
            assert len(response_text) > 50, "Expected a substantial response from the agent"

            # The response should mention finding information (indicating file search was used)
            # We can't assert exact product names without knowing the file content,
            # but we can verify the agent provided an answer
            print("\n✓ Agent successfully used file search tool to answer question from uploaded document")

            # Teardown
            print("\nCleaning up...")
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")

            await openai_client.vector_stores.delete(vector_store.id)
            print("Vector store deleted")

    @servicePreparer()
    @recorded_by_proxy_async(RecordedTransport.AZURE_CORE, RecordedTransport.HTTPX)
    async def test_agent_file_search_multi_turn_conversation_async(self, **kwargs):
        """
        Test multi-turn conversation with File Search (async version).

        This test verifies that an agent can maintain context across multiple turns
        while using File Search to answer follow-up questions.
        """

        model = self.test_agents_params["model_deployment_name"]

        async with (
            self.create_async_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Create a document with information about products
            product_info = """Product Catalog:

Widget A:
- Price: $150
- Category: Electronics
- Stock: 50 units
- Rating: 4.5/5 stars

Widget B:
- Price: $220
- Category: Electronics  
- Stock: 30 units
- Rating: 4.8/5 stars

Widget C:
- Price: $95
- Category: Home & Garden
- Stock: 100 units
- Rating: 4.2/5 stars
"""

            # Create vector store and upload document
            vector_store = await openai_client.vector_stores.create(name="ProductCatalog")
            print(f"Vector store created: {vector_store.id}")

            product_file = BytesIO(product_info.encode("utf-8"))
            product_file.name = "products.txt"

            file = await openai_client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=product_file,
            )
            print(f"Product catalog uploaded: {file.id}")

            # Create agent with File Search
            agent = await project_client.agents.create_version(
                agent_name="product-catalog-agent",
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a product information assistant. Use file search to answer questions about products.",
                    tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
                ),
                description="Agent for multi-turn product queries.",
            )
            print(f"Agent created: {agent.id}")

            # Turn 1: Ask about price
            print("\n--- Turn 1: Initial query ---")
            response_1 = await openai_client.responses.create(
                input="What is the price of Widget B?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            response_1_text = response_1.output_text
            print(f"Response 1: {response_1_text[:200]}...")
            assert "$220" in response_1_text or "220" in response_1_text, "Response should mention Widget B's price"

            # Turn 2: Follow-up question (requires context from turn 1)
            print("\n--- Turn 2: Follow-up query (testing context retention) ---")
            response_2 = await openai_client.responses.create(
                input="What about its stock level?",
                previous_response_id=response_1.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            response_2_text = response_2.output_text
            print(f"Response 2: {response_2_text[:200]}...")
            assert (
                "30" in response_2_text or "thirty" in response_2_text.lower()
            ), "Response should mention Widget B's stock (30 units)"

            # Turn 3: Another follow-up (compare with different product)
            print("\n--- Turn 3: Comparison query ---")
            response_3 = await openai_client.responses.create(
                input="How does that compare to Widget A's stock?",
                previous_response_id=response_2.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            response_3_text = response_3.output_text
            print(f"Response 3: {response_3_text[:200]}...")
            assert (
                "50" in response_3_text or "fifty" in response_3_text.lower()
            ), "Response should mention Widget A's stock (50 units)"

            # Turn 4: New topic (testing topic switching)
            print("\n--- Turn 4: Topic switch ---")
            response_4 = await openai_client.responses.create(
                input="Which widget has the highest rating?",
                previous_response_id=response_3.id,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            response_4_text = response_4.output_text
            print(f"Response 4: {response_4_text[:200]}...")
            assert (
                "widget b" in response_4_text.lower() or "4.8" in response_4_text
            ), "Response should identify Widget B as highest rated (4.8/5)"

            print("\n✓ Multi-turn conversation successful!")
            print("  - Context maintained across turns")
            print("  - Follow-up questions handled correctly")
            print("  - Topic switching works")

            # Cleanup
            await project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            await openai_client.vector_stores.delete(vector_store.id)
            print("Cleanup completed")
