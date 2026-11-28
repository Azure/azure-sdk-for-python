# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
# cspell:ignore rerank reranker reranking
"""Original async semantic reranker tests, re-run with the new test configuration.

Source: ``tests/test_semantic_reranker_async.py::TestSemanticRerankerAsync``.
Each method keeps the original steps and assertions; only setup changed.
``semantic_rerank`` itself is a Python wrapper around the external inference
service and has no Rust implementation. The ``_backend="rust"`` pin only
selects the client used to own the test database and container.
"""
import json
import unittest

import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import pytest

from config import clients
from config.settings import TestSettings, unique_database_id


@pytest.mark.semanticReranker
class TestSemanticRerankerAsync(unittest.IsolatedAsyncioTestCase):
    """Test to check async semantic reranker behavior."""
    TEST_CONTAINER_ID = TestSettings.TEST_SINGLE_PARTITION_CONTAINER_ID
    TEST_CONTAINER_PARTITION_KEY = TestSettings.TEST_CONTAINER_PARTITION_KEY

    async def asyncSetUp(self):
        """Async setup for each test."""
        self.TEST_DATABASE_ID = unique_database_id("semantic_rerank_async")
        self.key_client = clients.create_data_client_async(settings=_KeySettings, _backend="rust")
        self.client = clients.create_data_client_async(_backend="rust")
        await self.key_client.__aenter__()
        await self.client.__aenter__()
        self.key_db = await self.key_client.create_database_if_not_exists(id=self.TEST_DATABASE_ID)
        await self.key_db.create_container_if_not_exists(
            id=self.TEST_CONTAINER_ID,
            partition_key=PartitionKey(path='/' + self.TEST_CONTAINER_PARTITION_KEY, kind='Hash')
        )
        self.created_db = self.client.get_database_client(self.TEST_DATABASE_ID)
        self.test_container = self.created_db.get_container_client(self.TEST_CONTAINER_ID)

    async def asyncTearDown(self):
        """Async teardown for each test."""
        try:
            await self.key_client.delete_database(self.TEST_DATABASE_ID)
        except exceptions.CosmosHttpResponseError:
            pass
        finally:
            await self.key_client.close()
            await self.client.close()

    async def test_semantic_reranker_async_rust(self):
        """Test async semantic reranking functionality."""
        # Source: tests/test_semantic_reranker_async.py::TestSemanticRerankerAsync.test_semantic_reranker_async
        documents = self._get_documents(document_type="string")
        results = await self.test_container.semantic_rerank(
            context="What is the capital of France?",
            documents=documents,
            options={
                "return_documents": True,
                "top_k": 10,
                "batch_size": 32,
                "sort": True
            }
        )
        assert len(results["Scores"]) == len(documents)
        assert results["Scores"][0]["document"] == "Paris is the capital of France."

    async def test_semantic_reranker_async_json_documents_rust(self):
        # Source: tests/test_semantic_reranker_async.py::TestSemanticRerankerAsync.test_semantic_reranker_async_json_documents
        documents = self._get_documents(document_type="json")
        results = await self.test_container.semantic_rerank(
            context="What is the capital of France?",
            documents=[json.dumps(item) for item in documents],
            options={
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

    async def test_semantic_reranker_async_nested_json_documents_rust(self):
        # Source: tests/test_semantic_reranker_async.py::TestSemanticRerankerAsync.test_semantic_reranker_async_nested_json_documents
        documents = self._get_documents(document_type="nested_json")
        results = await self.test_container.semantic_rerank(
            context="What is the capital of France?",
            documents=[json.dumps(item) for item in documents],
            options={
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


class _KeySettings(TestSettings):
    """Key-authenticated settings for the control-plane client."""
    data_auth_mode = "key"
