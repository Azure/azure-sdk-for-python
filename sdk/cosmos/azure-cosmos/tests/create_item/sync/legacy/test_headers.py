# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Sync ``test_container_create_item_throughput_bucket`` test against
the ``_backend="rust"`` path.

The other methods in the source ``TestHeaders`` class cover correlated
activity ids, dedicated-gateway max-age, query headers, etc.; they
belong to their own operations' ``legacy/`` folders.

Self-contained: builds its own database + container in ``setUpClass``
and deletes them in ``tearDownClass``. The class name and method name
match the source at ``tests/test_headers.py`` so test IDs differ only
by path.

Run with::

    pytest --noconftest tests/create_item/sync/legacy/test_headers.py -v
"""
import os
import unittest
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, http_constants
import importlib
from unittest.mock import patch


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


# The throughput-bucket number the test asserts is set on the
# outgoing request. Kept identical to the source constant so the wire
# value is the same as what the legacy path sent.
request_throughput_bucket_number = 3


@pytest.mark.cosmosEmulator
class TestHeaders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = CosmosClient(HOST, KEY, _backend="rust")
        cls._db_id = "legacy_headers_" + uuid.uuid4().hex[:8]
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

    def test_container_create_item_throughput_bucket(self):
        # Source: tests/test_headers.py::TestHeaders.test_container_create_item_throughput_bucket
        binding = importlib.import_module(type(self.client._adapter).__module__)._rust_module
        with patch.object(binding, "create_item", wraps=binding.create_item) as operation:
            self.container.create_item(
                body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
                throughput_bucket=request_throughput_bucket_number)
        self.assertTrue(operation.called)
        for call in operation.call_args_list:
            self.assertEqual(
                call.args[1].headers[http_constants.HttpHeaders.ThroughputBucket],
                str(request_throughput_bucket_number),
            )
