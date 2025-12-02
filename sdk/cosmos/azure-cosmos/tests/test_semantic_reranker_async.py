# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
# cspell:ignore rerank reranker reranking
import json
import unittest
import asyncio

from azure.cosmos.aio import CosmosClient
import azure.cosmos.exceptions as exceptions
import pytest
from azure.identity.aio import DefaultAzureCredential

import test_config


@pytest.mark.semanticReranker
class TestSemanticRerankerAsync(unittest.TestCase):
    """Test to check async semantic reranker behavior."""
    client: CosmosClient = None
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
        credential = DefaultAzureCredential()
        self.client = CosmosClient(self.host, credential, connection_verify=False)
        self.test_db = await self.client.create_database_if_not_exists(self.TEST_DATABASE_ID)
        self.test_container = await self.test_db.create_container_if_not_exists(
            self.TEST_CONTAINER_ID,
            self.TEST_CONTAINER_PARTITION_KEY
        )

    async def asyncTearDown(self):
        """Async teardown for each test."""
        try:
            await self.test_db.delete_container(self.TEST_CONTAINER_ID)
            await self.client.delete_database(self.TEST_DATABASE_ID)
        except exceptions.CosmosHttpResponseError:
            pass
        finally:
            await self.client.close()

    def test_semantic_reranker_async(self):
        """Test async semantic reranking functionality."""
        async def run_test():
            await self.asyncSetUp()
            try:
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

            finally:
                await self.asyncTearDown()
        asyncio.run(run_test())

    def test_semantic_reranker_async_json_documents(self):
        async def run_test():
            await self.asyncSetUp()
            try:
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
            finally:
                await self.asyncTearDown()
        asyncio.run(run_test())

    def test_semantic_reranker_async_nested_json_documents(self):
        async def run_test():
            await self.asyncSetUp()
            try:
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
            finally:
                await self.asyncTearDown()
        asyncio.run(run_test())

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
