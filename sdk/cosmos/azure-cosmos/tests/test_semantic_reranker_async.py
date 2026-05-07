# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
# cspell:ignore rerank reranker reranking
import json
import unittest

import azure.cosmos.exceptions as exceptions
import pytest

import test_config


@pytest.mark.semanticReranker
@pytest.mark.cosmosAAD
class TestSemanticRerankerAsync(unittest.IsolatedAsyncioTestCase):
    """Test to check async semantic reranker behavior."""
    client = None
    key_client = None
    config = test_config.TestConfig
    host = config.host
    TEST_DATABASE_ID = config.TEST_DATABASE_ID
    TEST_CONTAINER_ID = config.TEST_SINGLE_PARTITION_CONTAINER_ID
    TEST_CONTAINER_PARTITION_KEY = config.TEST_CONTAINER_PARTITION_KEY


    @classmethod
    def setUpClass(cls):
        if cls.host == '[YOUR_ENDPOINT_HERE]':
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'host' at the top of this class to run the "
                "tests.")

    async def asyncSetUp(self):
        """Async setup for each test."""
        self.key_client, self.key_db, self.client, self.created_db = test_config.TestConfig.create_test_clients_async(
            self.TEST_DATABASE_ID,
            connection_verify=False,
        )
        await self.key_client.__aenter__()
        await self.client.__aenter__()
        await self.key_db.create_container_if_not_exists(self.TEST_CONTAINER_ID, self.TEST_CONTAINER_PARTITION_KEY)
        self.test_container = self.created_db.get_container_client(self.TEST_CONTAINER_ID)

    async def asyncTearDown(self):
        """Async teardown for each test."""
        try:
            await self.key_db.delete_container(self.TEST_CONTAINER_ID)
            await self.key_client.delete_database(self.TEST_DATABASE_ID)
        except exceptions.CosmosHttpResponseError:
            pass
        finally:
            await self.key_client.close()
            await self.client.close()

    async def test_semantic_reranker_async(self):
        """Test async semantic reranking functionality."""
        documents = self._get_documents(document_type="string")
        results = await self.test_container.semantic_rerank(
            reranking_context="What is the capital of France?",
            documents=documents,
            semantic_reranking_options={
                "return_documents": True,
                "top_k": 10,
                "batch_size": 32,
                "sort": True
            }
        )
        assert len(results["Scores"]) == len(documents)
        assert results["Scores"][0]["document"] == "Paris is the capital of France."

    async def test_semantic_reranker_async_json_documents(self):
        documents = self._get_documents(document_type="json")
        results = await self.test_container.semantic_rerank(
            reranking_context="What is the capital of France?",
            documents=[json.dumps(item) for item in documents],
            semantic_reranking_options={
                "return_documents": True,
                "top_k": 10,
                "batch_size": 32,
                "sort": True,
                "document_type": "json",
                "target_paths": "text",
            }
        )

        assert len(results["Scores"]) == len(documents)
        returned_document = json.loads(results["Scores"][0]["document"])
        assert returned_document["text"] == "Paris is the capital of France."

    async def test_semantic_reranker_async_nested_json_documents(self):
        documents = self._get_documents(document_type="nested_json")
        results = await self.test_container.semantic_rerank(
            reranking_context="What is the capital of France?",
            documents=[json.dumps(item) for item in documents],
            semantic_reranking_options={
                "return_documents": True,
                "top_k": 10,
                "batch_size": 32,
                "sort": True,
                "document_type": "json",
                "target_paths": "info.text",
            }
        )

        assert len(results["Scores"]) == len(documents)
        returned_document = json.loads(results["Scores"][0]["document"])
        assert returned_document["info"]["text"] == "Paris is the capital of France."

    def _get_documents(self, document_type: str):
        if document_type == "string":
            return [
                "Berlin is the capital of Germany.",
                "Paris is the capital of France.",
                "Madrid is the capital of Spain."
            ]
        elif document_type == "json":
            return [
                {"id": "1", "text": "Berlin is the capital of Germany."},
                {"id": "2", "text": "Paris is the capital of France."},
                {"id": "3", "text": "Madrid is the capital of Spain."}
            ]
        elif document_type == "nested_json":
            return [
                {"id": "1", "info": {"text": "Berlin is the capital of Germany."}},
                {"id": "2", "info": {"text": "Paris is the capital of France."}},
                {"id": "3", "info": {"text": "Madrid is the capital of Spain."}}
            ]
        else:
            raise ValueError("Unsupported document type")
