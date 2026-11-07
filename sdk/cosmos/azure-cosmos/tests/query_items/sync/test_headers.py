# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Sync ``query_items`` header tests on the ``_backend="rust"`` path.

Copied from ``tests/test_headers.py``; the class and method names match the
source (apart from the method's ``_rust`` suffix). Builds its own database +
container and reads ``ACCOUNT_HOST`` / ``ACCOUNT_KEY`` from the environment.

The legacy test captured outgoing HTTP requests, which the Rust transport does
not expose (known gap 6). The throughput-bucket copy instead checks the
request the SDK hands to the Rust page binding, as the ``upsert_item`` copies do.
Gateway V2 may still drop the header on the wire (known gap 36).

Run: ``pytest --noconftest tests/query_items/sync/test_headers.py -v``
"""
import importlib
import os
import unittest
import uuid
from unittest.mock import MagicMock, patch

import pytest

from azure.cosmos import CosmosClient, PartitionKey


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


# Same value as the source, so the wire bytes match the legacy path.
request_throughput_bucket_number = 3


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestHeaders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = CosmosClient(HOST, KEY, _backend="rust")
        cls._db_id = "legacy_query_headers_" + uuid.uuid4().hex[:8]
        cls._container_id = "c_" + uuid.uuid4().hex[:8]
        cls.database = cls.client.create_database(cls._db_id)
        cls.data_container = cls.database.create_container(
            id=cls._container_id,
            partition_key=PartitionKey(path="/pk"),
        )

    @classmethod
    def tearDownClass(cls):
        try:
            cls.client.delete_database(cls._db_id)
        except Exception:  # pylint: disable=broad-except
            pass
        cls.client.close()

    def side_effect_correlated_activity_id(self, *args, **kwargs):
        # Source helper: tests/test_headers.py::TestHeaders.side_effect_correlated_activity_id
        # Extract request headers from args
        assert args[3]["x-ms-cosmos-correlated-activityid"]  # cspell:disable-line
        raise StopIteration

    def test_correlated_activity_id_rust(self):
        # Source: tests/test_headers.py::TestHeaders.test_correlated_activity_id
        query = 'SELECT * from c ORDER BY c._ts'

        pytest.skip("internals-only: the request headers are read by replacing legacy "
                    "client_connection._CosmosClientConnection__Post, which Rust-backed queries never call.")
        cosmos_client_connection = self.data_container.client_connection
        original_connection_post = cosmos_client_connection._CosmosClientConnection__Post
        cosmos_client_connection._CosmosClientConnection__Post = MagicMock(
            side_effect=self.side_effect_correlated_activity_id)
        try:
            list(self.data_container.query_items(query=query, partition_key="pk-1"))
        except StopIteration:
            pass
        finally:
            cosmos_client_connection._CosmosClientConnection__Post = original_connection_post

    def test_container_query_items_throughput_bucket_rust(self):
        """Verify the operation prepares the requested throughput bucket."""
        # Source: tests/test_headers.py::TestHeaders.test_container_query_items_throughput_bucket
        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        self.data_container.create_item(body=document_definition)

        query = 'SELECT * from c'
        binding = importlib.import_module(type(self.client._adapter).__module__)._rust_module
        with patch.object(binding, "fetch_page_with_cursor", wraps=binding.fetch_page_with_cursor) as operation:
            list(self.data_container.query_items(
                query=query,
                partition_key='pk',
                throughput_bucket=request_throughput_bucket_number))
        self.assertTrue(operation.called)
        for call in operation.call_args_list:
            self.assertEqual(call.args[1].settings.throughput_bucket, request_throughput_bucket_number)


if __name__ == "__main__":
    unittest.main()
