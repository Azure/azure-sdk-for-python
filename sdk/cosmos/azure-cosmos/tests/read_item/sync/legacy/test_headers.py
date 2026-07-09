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
and deletes them in ``tearDownClass``. Reads ``ACCOUNT_HOST`` and
``ACCOUNT_KEY`` from the environment, defaulting to the local emulator when unset.

Run with::

    pytest --noconftest tests/read_item/sync/legacy/test_headers.py -v
"""
import os
import unittest
import uuid

from azure.cosmos import CosmosClient, PartitionKey, http_constants


HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")
KEY = os.environ.get(
    "ACCOUNT_KEY",
    "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==",
)


# Constants kept identical to the source so the wire value is the same
# as what core-python sent.
request_throughput_bucket_number = 3


def request_raw_response_hook(response):
    assert (response.http_request.headers[http_constants.HttpHeaders.ThroughputBucket]
            == str(request_throughput_bucket_number))


class TestHeaders(unittest.TestCase):

    dedicated_gateway_max_age_negative = -1

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

    def test_container_read_item_throughput_bucket(self):
        """Verify read_item forwards the per-request throughput_bucket kwarg as the x-ms-cosmos-throughput-bucket header."""
        # Source: tests/test_headers.py::TestHeaders.test_container_read_item_throughput_bucket
        created_document = self.container.create_item(
            body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'}
        )
        self.container.read_item(
            item=created_document['id'],
            partition_key="mypk",
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook,
        )

    def test_negative_max_integrated_cache_staleness(self):
        """Verify read_item raises ValueError when max_integrated_cache_staleness_in_ms is negative."""
        # Source: tests/test_headers.py::TestHeaders.test_negative_max_integrated_cache_staleness
        try:
            self.container.read_item(
                item="id-1", partition_key="pk-1",
                max_integrated_cache_staleness_in_ms=self.dedicated_gateway_max_age_negative,
            )
        except Exception as exception:
            assert isinstance(exception, ValueError)

