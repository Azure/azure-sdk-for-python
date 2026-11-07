# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
# cspell:ignore rerank reranker reranking
"""Original sync semantic reranker tests, re-run with the new test configuration.

Source: ``tests/test_semantic_reranker.py::TestSemanticReranker``. Each method
keeps the original steps and assertions; only setup changed.
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
class TestSemanticReranker(unittest.TestCase):
    """Test to check semantic reranker behavior."""
    TEST_CONTAINER_ID = TestSettings.TEST_SINGLE_PARTITION_CONTAINER_ID
    TEST_CONTAINER_PARTITION_KEY = TestSettings.TEST_CONTAINER_PARTITION_KEY

    @classmethod
    def setUpClass(cls):
        cls.TEST_DATABASE_ID = unique_database_id("semantic_rerank")
        cls.key_client = clients.create_setup_client(_backend="rust")
        cls.key_db = cls.key_client.create_database_if_not_exists(id=cls.TEST_DATABASE_ID)
        cls.key_db.create_container_if_not_exists(
            id=cls.TEST_CONTAINER_ID,
            partition_key=PartitionKey(path='/' + cls.TEST_CONTAINER_PARTITION_KEY, kind='Hash')
        )
        cls.client = clients.create_data_client(_backend="rust")
        cls.created_db = cls.client.get_database_client(cls.TEST_DATABASE_ID)
        cls.test_container = cls.created_db.get_container_client(cls.TEST_CONTAINER_ID)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.key_client.delete_database(cls.TEST_DATABASE_ID)
        except exceptions.CosmosHttpResponseError:
            pass
        finally:
            cls.client.close()
            cls.key_client.close()

    def test_semantic_reranker_rust(self):
        # Source: tests/test_semantic_reranker.py::TestSemanticReranker.test_semantic_reranker
        documents = self._get_documents(document_type="string")
        results = self.test_container.semantic_rerank(
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

    def test_semantic_reranker_json_documents_rust(self):
        # Source: tests/test_semantic_reranker.py::TestSemanticReranker.test_semantic_reranker_json_documents
        documents = self._get_documents(document_type="json")
        results = self.test_container.semantic_rerank(
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

    def test_semantic_reranker_nested_json_documents_rust(self):
        # Source: tests/test_semantic_reranker.py::TestSemanticReranker.test_semantic_reranker_nested_json_documents
        documents = self._get_documents(document_type="nested_json")
        results = self.test_container.semantic_rerank(
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
