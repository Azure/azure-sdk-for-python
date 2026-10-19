# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Sync ``test_container_read_item_throughput_bucket`` and
``test_negative_max_integrated_cache_staleness`` tests against the
``_backend="rust"`` path.

Source: ``tests/test_headers.py``. The other methods in the source
``TestHeaders`` class cover create-item throughput-bucket, query-item
throughput-bucket, correlated activity ids, etc.; they belong to their
own operations' ``legacy/`` folders. ``test_max_integrated_cache_staleness``
and ``test_client_id`` are deliberately not copied here because they
patch ``CosmosClientConnection._CosmosClientConnection__Get`` directly
-- internals-only, not a customer contract.

Self-contained: builds its own database + container in ``setUpClass``
and registers resource deletion and client closure as each is acquired. Reads ``ACCOUNT_HOST`` and
``ACCOUNT_KEY`` from the environment, defaulting to the local emulator when unset.

Run with::

    pytest --noconftest tests/read_item/sync/legacy/test_headers.py -v
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


# Constants kept identical to the source so the wire value is the same
# as what the legacy path sent.
request_throughput_bucket_number = 3


@pytest.mark.cosmosEmulator
class TestHeaders(unittest.TestCase):

    dedicated_gateway_max_age_negative = -1

    @classmethod
    def setUpClass(cls):
        cls.client = CosmosClient(HOST, KEY, _backend="rust")
        cls.addClassCleanup(cls.client.close)
        cls._db_id = "legacy_ri_headers_" + uuid.uuid4().hex[:8]
        cls._container_id = "c_" + uuid.uuid4().hex[:8]
        cls.database = cls.client.create_database(cls._db_id)
        cls.addClassCleanup(cls.client.delete_database, cls._db_id)
        print(f"\nOwned read-test database: {cls._db_id}")
        cls.container = cls.database.create_container(
            id=cls._container_id,
            partition_key=PartitionKey(path="/pk"),
        )

    def test_container_read_item_throughput_bucket_rust(self):
        """Verify the operation prepares the requested throughput bucket."""
        # Source: tests/test_headers.py::TestHeaders.test_container_read_item_throughput_bucket
        created_document = self.container.create_item(
            body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'}
        )
        binding = importlib.import_module(type(self.client._adapter).__module__)._rust_module
        with patch.object(binding, "read_item", wraps=binding.read_item) as operation:
            self.container.read_item(
                item=created_document['id'],
                partition_key="mypk",
                throughput_bucket=request_throughput_bucket_number,
            )
        self.assertTrue(operation.called)
        for call in operation.call_args_list:
            self.assertEqual(
                call.args[1].headers[http_constants.HttpHeaders.ThroughputBucket],
                str(request_throughput_bucket_number),
            )

    def test_negative_max_integrated_cache_staleness_rust(self):
        """If the negative-staleness call raises, require a ValueError.

        The copied try/except has no assertion when the call returns normally.
        It therefore does not establish that rejection occurs or precedes I/O.
        """
        # Source: tests/test_headers.py::TestHeaders.test_negative_max_integrated_cache_staleness
        try:
            self.container.read_item(
                item="id-1", partition_key="pk-1",
                max_integrated_cache_staleness_in_ms=self.dedicated_gateway_max_age_negative,
            )
        except Exception as exception:
            assert isinstance(exception, ValueError)
