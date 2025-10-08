# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
# cspell:ignore rerank reranker reranking
import json
import unittest

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import pytest
from azure.identity import DefaultAzureCredential

import test_config


@pytest.mark.semanticReranker
class TestSemanticReranker(unittest.TestCase):
    """Test to check semantic reranker behavior."""
    client: cosmos_client.CosmosClient = None
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

        credential = DefaultAzureCredential()
        cls.client = cosmos_client.CosmosClient(cls.host, credential=credential)
        cls.test_db = cls.client.create_database_if_not_exists(cls.TEST_DATABASE_ID)
        cls.test_container = cls.test_db.create_container_if_not_exists(cls.TEST_CONTAINER_ID,
                                                                        cls.TEST_CONTAINER_PARTITION_KEY)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.test_db.delete_container(cls.TEST_CONTAINER_ID)
            cls.client.delete_database(cls.TEST_DATABASE_ID)
        except exceptions.CosmosHttpResponseError:
            pass

    def test_semantic_reranker(self):
        documents = self._get_documents(document_type="string")
        results = self.test_container.semantic_rerank(
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

    def test_semantic_reranker_json_documents(self):
        documents = self._get_documents(document_type="json")
        results = self.test_container.semantic_rerank(
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

    def test_semantic_reranker_nested_json_documents(self):
        documents = self._get_documents(document_type="nested_json")
        results = self.test_container.semantic_rerank(
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
