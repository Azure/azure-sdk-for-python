# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Sync ``test_container_patch_item_throughput_bucket`` on the core-python path.

A deterministic copy of ``sync/legacy/test_headers.py`` (identical except
that it doesn't pass the ``_backend`` argument). The partition-key value
and id are fixed so the parity reporter can diff the patched document
field by field against the rust run; the original test uses a random pk
each run, which would show up as a spurious mismatch.

Run: ``pytest tests/patch_item/sync/test_headers.py -v -s``
"""
import os
import unittest
import uuid

from azure.cosmos import CosmosClient, PartitionKey, http_constants


HOST = os.environ["ACCOUNT_HOST"]
KEY = os.environ["ACCOUNT_KEY"]


# Same value as the rust copy, so the wire bytes match.
request_throughput_bucket_number = 3


def request_raw_response_hook(response):
    assert (response.http_request.headers[http_constants.HttpHeaders.ThroughputBucket]
            == str(request_throughput_bucket_number))


class TestHeaders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # No ``_backend`` -> the SDK default (core-python) path.
        cls.client = CosmosClient(HOST, KEY)
        cls._db_id = "corepy_pi_headers_" + uuid.uuid4().hex[:8]
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

    def test_container_patch_item_throughput_bucket(self):
        """patch_item forwards the ``throughput_bucket`` keyword as the
        ``x-ms-cosmos-throughput-bucket`` header, and all six patch
        operations apply to produce the expected document."""
        # Fixed (pk, id) so the parity reporter can diff the patched document
        # against the rust run field by field; each run has its own fresh
        # container, so there is no collision.
        pkValue = "patch_item_pk"
        item = {
            "id": "patch_item",
            "pk": pkValue,
            "prop": "prop1",
            "address": {
                "city": "Redmond"
            },
            "company": "Microsoft",
            "number": 3}
        self.container.create_item(item)
        operations = [
            {"op": "add", "path": "/color", "value": "yellow"},
            {"op": "remove", "path": "/prop"},
            {"op": "replace", "path": "/company", "value": "CosmosDB"},
            {"op": "set", "path": "/address/new_city", "value": "Atlanta"},
            {"op": "incr", "path": "/number", "value": 7},
            {"op": "move", "from": "/color", "path": "/favorite_color"}
        ]
        self.container.patch_item(
            item="patch_item",
            partition_key=pkValue,
            patch_operations=operations,
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)
