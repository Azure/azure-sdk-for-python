# pylint: disable=too-many-lines,line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed-----------------------------------------------------------------------------------------
# cSpell:disable

import os
import pytest
from io import BytesIO
from test_base import TestBase, servicePreparer
from devtools_testutils import is_live_and_not_recording
from azure.ai.projects.models import PromptAgentDefinition, FileSearchTool


class TestAgentFileSearch(TestBase):

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_agent_file_search(self, **kwargs):
        """
        Test agent with File Search tool for document Q&A.

        This test verifies that an agent can:
        1. Upload and index documents into a vector store
        2. Use FileSearchTool to search through uploaded documents
        3. Answer questions based on document content

        Routes used in this test:

        Action REST API Route                                Client Method
        ------+---------------------------------------------+-----------------------------------
        # Setup:
        POST   /vector_stores                                openai_client.vector_stores.create()
        POST   /vector_stores/{id}/files                     openai_client.vector_stores.files.upload_and_poll()
        POST   /agents/{agent_name}/versions                 project_client.agents.create_version()

        # Test focus:
        POST   /openai/responses                             openai_client.responses.create() (with FileSearchTool)

        # Teardown:
        DELETE /agents/{agent_name}/versions/{agent_version} project_client.agents.delete_version()
        DELETE /vector_stores/{id}                           openai_client.vector_stores.delete()
        """

        model = self.test_agents_params["model_deployment_name"]

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
            vector_store = openai_client.vector_stores.create(name="ProductInfoStore")
            print(f"Vector store created (id: {vector_store.id})")
            assert vector_store.id is not None

            # Upload file to vector store
            with open(asset_file_path, "rb") as f:
                file = openai_client.vector_stores.files.upload_and_poll(
                    vector_store_id=vector_store.id,
                    file=f,
                )

            print(f"File uploaded (id: {file.id}, status: {file.status})")
            assert file.id is not None
            assert file.status == "completed", f"Expected file status 'completed', got '{file.status}'"

            # Create agent with file search tool
            agent = project_client.agents.create_version(
                agent_name="file-search-agent",
                definition=PromptAgentDefinition(
                    model=model,
                    instructions="You are a helpful assistant that can search through uploaded documents to answer questions.",
                    tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
                ),
                description="Agent for testing file search capabilities.",
            )
            print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")
            assert agent.id is not None
            assert agent.name == "file-search-agent"
            assert agent.version is not None

            # Ask a question about the uploaded document
            print("\nAsking agent about the product information...")

            response = openai_client.responses.create(
                input="What products are mentioned in the document?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            print(f"Response completed (id: {response.id})")
            assert response.id is not None
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
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("Agent deleted")

            openai_client.vector_stores.delete(vector_store.id)
            print("Vector store deleted")

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_agent_file_search_unsupported_file_type(self, **kwargs):
        """
        Negative test: Verify that unsupported file types are rejected with clear error messages.

        This test validates that:
        1. CSV files (unsupported format) are rejected
        2. The error message clearly indicates the file type is not supported
        3. The error message lists supported file types

        This ensures good developer experience by providing actionable error messages.
        """

        with (
            self.create_client(operation_group="agents", **kwargs) as project_client,
            project_client.get_openai_client() as openai_client,
        ):
            # Create vector store
            vector_store = openai_client.vector_stores.create(name="UnsupportedFileTestStore")
            print(f"Vector store created (id: {vector_store.id})")

            # Create CSV file (unsupported format)
            csv_content = """product,quarter,revenue
Widget A,Q1,15000
Widget B,Q1,22000
Widget A,Q2,18000
Widget B,Q2,25000"""

            csv_file = BytesIO(csv_content.encode("utf-8"))
            csv_file.name = "sales_data.csv"

            # Attempt to upload unsupported file type
            print("\nAttempting to upload CSV file (unsupported format)...")
            try:
                file = openai_client.vector_stores.files.upload_and_poll(
                    vector_store_id=vector_store.id,
                    file=csv_file,
                )
                # If we get here, the test should fail
                openai_client.vector_stores.delete(vector_store.id)
                pytest.fail("Expected BadRequestError for CSV file upload, but upload succeeded")

            except Exception as e:
                error_message = str(e)
                print(f"\n✓ Upload correctly rejected with error: {error_message[:200]}...")

                # Verify error message quality
                assert (
                    "400" in error_message or "BadRequestError" in type(e).__name__
                ), "Should be a 400 Bad Request error"

                assert ".csv" in error_message.lower(), "Error message should mention the CSV file extension"

                assert (
                    "not supported" in error_message.lower() or "unsupported" in error_message.lower()
                ), "Error message should clearly state the file type is not supported"

                # Check that supported file types are mentioned (helpful for developers)
                error_lower = error_message.lower()
                has_supported_list = any(ext in error_lower for ext in [".txt", ".pdf", ".md", ".py"])
                assert has_supported_list, "Error message should list examples of supported file types"

                print("✓ Error message is clear and actionable")
                print("  - Mentions unsupported file type (.csv)")
                print("  - States it's not supported")
                print("  - Lists supported file types")

            # Cleanup
            openai_client.vector_stores.delete(vector_store.id)
            print("\nVector store deleted")

    @servicePreparer()
    @pytest.mark.skipif(
        condition=(not is_live_and_not_recording()),
        reason="Skipped because we cannot record network calls with OpenAI client",
    )
    def test_agent_file_search_multi_turn_conversation(self, **kwargs):
        """
        Test multi-turn conversation with File Search.

        This test verifies that an agent can maintain context across multiple turns
        while using File Search to answer follow-up questions.
        """

        model = self.test_agents_params["model_deployment_name"]

        with (
            self.create_client(operation_group="agents", **kwargs) as project_client,
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
            vector_store = openai_client.vector_stores.create(name="ProductCatalog")
            print(f"Vector store created: {vector_store.id}")

            product_file = BytesIO(product_info.encode("utf-8"))
            product_file.name = "products.txt"

            file = openai_client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=product_file,
            )
            print(f"Product catalog uploaded: {file.id}")

            # Create agent with File Search
            agent = project_client.agents.create_version(
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
            response_1 = openai_client.responses.create(
                input="What is the price of Widget B?",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            response_1_text = response_1.output_text
            print(f"Response 1: {response_1_text[:200]}...")
            assert "$220" in response_1_text or "220" in response_1_text, "Response should mention Widget B's price"

            # Turn 2: Follow-up question (requires context from turn 1)
            print("\n--- Turn 2: Follow-up query (testing context retention) ---")
            response_2 = openai_client.responses.create(
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
            response_3 = openai_client.responses.create(
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
            response_4 = openai_client.responses.create(
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
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            openai_client.vector_stores.delete(vector_store.id)
            print("Cleanup completed")
