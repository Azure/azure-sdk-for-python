# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Sync ``test_container_delete_item_throughput_bucket`` against the Rust path.

The original captured outgoing Python HTTP requests and checked their
throughput-bucket header. Rust requests bypass that transport, so this copy
checks the value the Python wrapper hands to the Rust delete binding.

Self-contained: builds its own database + container through a key client in
``setUpClass`` and deletes them in ``tearDownClass``; the tested operations
run on the data client (AAD in the cosmosAAD* lanes).
"""
import importlib
import unittest
import uuid
from unittest.mock import patch

import pytest

from config.clients import create_data_client, create_setup_client

from azure.cosmos import PartitionKey

request_throughput_bucket_number = 3


def assert_request_throughput_bucket(prepared):
    assert prepared.settings.throughput_bucket == request_throughput_bucket_number


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestHeaders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Same split as the original: the key client provisions, the data
        # client (AAD in the cosmosAAD* lanes) runs the tested operations.
        cls.key_client = create_setup_client()
        cls.client = create_data_client(_backend="rust")
        cls._db_id = "delete_headers_" + uuid.uuid4().hex[:8]
        cls._container_id = "c_" + uuid.uuid4().hex[:8]
        cls.database = cls.key_client.create_database(cls._db_id)
        cls.container = cls.database.create_container(
            id=cls._container_id,
            partition_key=PartitionKey(path="/pk"),
        )
        cls.data_database = cls.client.get_database_client(cls._db_id)
        cls.data_container = cls.data_database.get_container_client(cls._container_id)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.key_client.delete_database(cls._db_id)
        except Exception:  # pylint: disable=broad-except
            pass
        cls.client.close()
        cls.key_client.close()

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
        # Known gap 36: Request options are not sent over Gateway V2. The binding receives the bucket, but the pinned driver omits it on Gateway V2, so this checks the native boundary, not the wire header.
        for request in requests:
            assert_request_throughput_bucket(request)
