# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Sync ``test_container_delete_item_throughput_bucket`` against the Rust path.

The original captured outgoing Python HTTP requests and checked their
throughput-bucket header. Rust requests bypass that transport, so this copy
checks the value the Python wrapper hands to the Rust delete binding.

Self-contained: builds its own database + container in ``setUpClass`` and
deletes them in ``tearDownClass``.
"""
import importlib
import os
import unittest
import uuid
from unittest.mock import patch

import pytest

from azure.cosmos import CosmosClient, PartitionKey

HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)

request_throughput_bucket_number = 3


def assert_request_throughput_bucket(prepared):
    assert prepared.settings.throughput_bucket == request_throughput_bucket_number


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestHeaders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = CosmosClient(HOST, KEY, _backend="rust")
        cls._db_id = "delete_headers_" + uuid.uuid4().hex[:8]
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

    def test_container_delete_item_throughput_bucket_rust(self):
        # Source: tests/test_headers.py::TestHeaders.test_container_delete_item_throughput_bucket
        created_item = self.data_container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})

        binding = importlib.import_module(type(self.client._adapter).__module__)._rust_module
        with patch.object(binding, "delete_item", wraps=binding.delete_item) as operation:
            self.data_container.delete_item(
                created_item['id'],
                partition_key='mypk',
                throughput_bucket=request_throughput_bucket_number)
        operation.assert_called_once()
        requests = [operation.call_args.args[1]]
        self.assertEqual(requests[0].op, "delete_item")
        self.assertEqual(requests[0].item_id, created_item['id'])
        # Known gap 33: `CosmosClient(...)`: settings from first principles, bites 1-15 (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-33). The binding receives the bucket, but the pinned driver omits it on Gateway V2, so this checks the native boundary, not the wire header.
        for request in requests:
            assert_request_throughput_bucket(request)
