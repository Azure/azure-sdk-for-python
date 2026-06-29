# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Sync ``test_container_upsert_item_throughput_bucket`` on the
``_backend="rust"`` path.

Copied from ``tests/test_headers.py``; the class and method names match
the source so the parity reporter can pair the core-python and rust
runs. Builds its own database + container and reads ``ACCOUNT_HOST`` /
``ACCOUNT_KEY`` from the environment.

Run: ``pytest --noconftest tests/upsert_item/sync/legacy/test_headers.py -v``
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


# Same value as the source, so the wire bytes match core-python.
request_throughput_bucket_number = 3


def request_raw_response_hook(response):
    assert (response.http_request.headers[http_constants.HttpHeaders.ThroughputBucket]
            == str(request_throughput_bucket_number))


class TestHeaders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = CosmosClient(HOST, KEY, _backend="rust")
        cls._db_id = "legacy_ui_headers_" + uuid.uuid4().hex[:8]
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

    def test_container_upsert_item_throughput_bucket(self):
        """Verify upsert_item forwards the per-request throughput_bucket kwarg as the x-ms-cosmos-throughput-bucket header."""
        # Source: tests/test_headers.py::TestHeaders.test_container_upsert_item_throughput_bucket
        self.container.upsert_item(
            body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook,
        )

