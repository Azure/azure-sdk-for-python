# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Sync ``test_container_create_item_throughput_bucket`` test against
the ``_backend="rust"`` path.

The other methods in the source ``TestHeaders`` class cover correlated
activity ids, dedicated-gateway max-age, query headers, etc.; they
belong to their own operations' ``legacy/`` folders.

Self-contained: key-owned setup registers cleanup in ``setUpClass``;
data operations follow the configured key/AAD lane. The class name matches
``tests/test_headers.py``; copied method names add ``_rust``.

Run with::

    pytest --noconftest tests/create_item/sync/test_headers.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
import importlib
from unittest.mock import patch
from config import clients


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


# Preserve the original value at the typed native boundary.
# Wire-header conversion is checked by the binding settings tests.
request_throughput_bucket_number = 3


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestHeaders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.key_client = CosmosClient(HOST, KEY, _backend="rust")
        cls.addClassCleanup(cls.key_client.close)
        cls._db_id = "legacy_headers_" + uuid.uuid4().hex[:8]
        cls._container_id = "c_" + uuid.uuid4().hex[:8]
        key_database = cls.key_client.create_database(cls._db_id)
        cls.addClassCleanup(cls.key_client.delete_database, cls._db_id)
        key_database.create_container(
            id=cls._container_id, partition_key=PartitionKey(path="/pk"),
        )
        cls.client = clients.create_data_client(_backend="rust")
        cls.addClassCleanup(cls.client.close)
        cls.database = cls.client.get_database_client(cls._db_id)
        cls.container = cls.database.get_container_client(cls._container_id)

    def test_container_create_item_throughput_bucket_rust(self):
        # Source: tests/test_headers.py::TestHeaders.test_container_create_item_throughput_bucket
        binding = importlib.import_module(type(self.client._adapter).__module__)._rust_module
        with patch.object(binding, "create_item", wraps=binding.create_item) as operation:
            created = self.container.create_item(
                body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
                throughput_bucket=request_throughput_bucket_number)
        operation.assert_called_once()
        prepared = operation.call_args.args[1]
        self.assertEqual(prepared.settings.throughput_bucket, request_throughput_bucket_number)
        self.assertEqual(prepared.op, "create_item")
        self.assertEqual(created["id"], prepared.item_id)
