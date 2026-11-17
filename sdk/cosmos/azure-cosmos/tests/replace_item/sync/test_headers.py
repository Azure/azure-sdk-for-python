# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Sync ``test_container_replace_item_throughput_bucket`` on the
``_backend="rust"`` path.

Copied from ``tests/test_headers.py``; the class and method names match
the source (apart from the method's ``_rust`` suffix) so the parity reporter can pair
the core-python and Rust
runs. Builds its own database + container through a key client; the tested
operations run on the data client (AAD in the cosmosAAD* lanes).

Run: ``pytest --noconftest tests/replace_item/sync/test_headers.py -v``
"""
import importlib
import unittest
from unittest.mock import patch
import uuid

import pytest

from config.clients import create_data_client, create_setup_client

from azure.cosmos import PartitionKey


# Same value as the source, so the wire bytes match the legacy path.
request_throughput_bucket_number = 3


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestHeaders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Same split as the original: the key client provisions, the data
        # client (AAD in the cosmosAAD* lanes) runs the tested operations.
        cls.key_client = create_setup_client()
        cls.client = create_data_client(_backend="rust")
        cls._db_id = "legacy_ri_headers_" + uuid.uuid4().hex[:8]
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

    def test_container_replace_item_throughput_bucket_rust(self):
        """Verify the operation prepares the requested throughput bucket."""
        # Source: tests/test_headers.py::TestHeaders.test_container_replace_item_throughput_bucket
        created_document = self.data_container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        binding = importlib.import_module(type(self.client._adapter).__module__)._rust_module
        with patch.object(binding, "replace_item", wraps=binding.replace_item) as operation:
            self.data_container.replace_item(
                item=created_document['id'],
                body={'id': '2' + str(uuid.uuid4()), 'pk': 'mypk'},
                throughput_bucket=request_throughput_bucket_number)
        self.assertTrue(operation.called)
        for call in operation.call_args_list:
            self.assertEqual(call.args[1].settings.throughput_bucket, request_throughput_bucket_number)
