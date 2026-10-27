# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Sync ``test_container_replace_item_throughput_bucket`` on the
``_backend="rust"`` path.

Copied from ``tests/test_headers.py``; the class and method names match
the source (apart from the method's ``_rust`` suffix) so the parity reporter can pair
the core-python and Rust
runs. Builds its own database + container and reads ``ACCOUNT_HOST`` /
``ACCOUNT_KEY`` from the environment.

Run: ``pytest --noconftest tests/replace_item/sync/legacy/test_headers.py -v``
"""
import importlib
import os
import unittest
from unittest.mock import patch
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, http_constants


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


# Same value as the source, so the wire bytes match the legacy path.
request_throughput_bucket_number = 3


@pytest.mark.cosmosEmulator
class TestHeaders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = CosmosClient(HOST, KEY, _backend="rust")
        cls._db_id = "legacy_ri_headers_" + uuid.uuid4().hex[:8]
        cls._container_id = "c_" + uuid.uuid4().hex[:8]
        cls.database = cls.client.create_database(cls._db_id)
        cls.container = cls.database.create_container(
            id=cls._container_id,
            partition_key=PartitionKey(path="/pk"),
        )

    @classmethod
    def tearDownClass(cls):
        try:
            cls.client.delete_database(cls._db_id)
        except Exception:  # pylint: disable=broad-except
            pass

    def test_container_replace_item_throughput_bucket_rust(self):
        """Verify the operation prepares the requested throughput bucket."""
        # Source: tests/test_headers.py::TestHeaders.test_container_replace_item_throughput_bucket
        created_document = self.container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        binding = importlib.import_module(type(self.client._adapter).__module__)._rust_module
        with patch.object(binding, "replace_item", wraps=binding.replace_item) as operation:
            self.container.replace_item(
                item=created_document['id'],
                body={'id': '2' + str(uuid.uuid4()), 'pk': 'mypk'},
                throughput_bucket=request_throughput_bucket_number)
        self.assertTrue(operation.called)
        for call in operation.call_args_list:
            self.assertEqual(
                call.args[1].headers[http_constants.HttpHeaders.ThroughputBucket],
                str(request_throughput_bucket_number),
            )
