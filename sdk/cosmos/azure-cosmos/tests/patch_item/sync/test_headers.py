# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Sync ``test_container_patch_item_throughput_bucket`` on the ``_backend="rust"`` path.

Copied from ``tests/test_headers.py``; the class and method names match the
source (apart from the method's ``_rust`` suffix) so the parity reporter can pair the
core-python and Rust runs. A key client builds
its own database + container; the data client (AAD in AAD lanes) does the
item work, as in the source. The single patch call exercises all six operation kinds
(add / remove / replace / set / incr / move) in one request.

Run: ``pytest --noconftest tests/patch_item/sync/test_headers.py -v``
"""
import importlib
import unittest
from unittest.mock import patch
import uuid

import pytest

from azure.cosmos import PartitionKey
from config.clients import create_data_client, create_setup_client


# Same value as the source, so the wire bytes match core-python.
request_throughput_bucket_number = 3


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
class TestHeaders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Key client owns the database and container; the data client (AAD in
        # AAD lanes) does item work, as in the original. Class cleanups run in
        # reverse order and still run if setup fails partway.
        cls.key_client = create_setup_client(_backend="rust")
        cls.addClassCleanup(cls.key_client.close)
        cls.client = create_data_client(_backend="rust")
        cls.addClassCleanup(cls.client.close)
        cls._db_id = "legacy_pi_headers_" + uuid.uuid4().hex[:8]
        cls._container_id = "c_" + uuid.uuid4().hex[:8]
        key_database = cls.key_client.create_database(cls._db_id)
        cls.addClassCleanup(cls.key_client.delete_database, cls._db_id)
        key_database.create_container(
            id=cls._container_id,
            partition_key=PartitionKey(path="/pk"),
        )
        cls.container = cls.client.get_database_client(cls._db_id).get_container_client(cls._container_id)

    def test_container_patch_item_throughput_bucket_rust(self):
        """Verify the operation prepares the requested throughput bucket."""
        # Source: tests/test_headers.py::TestHeaders.test_container_patch_item_throughput_bucket
        # NOTE: the partition-key value and item id are FIXED (not a random
        # uuid like the source) so the parity reporter can diff the patched
        # item field-by-field against the core-python column -- a random
        # pk would show up as a spurious body divergence. Each column builds
        # its own fresh container, so the fixed (pk, id) never collides.
        pkValue = "patch_item_pk"
        # Create item to patch
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
        # Define and run patch operations
        operations = [
            {"op": "add", "path": "/color", "value": "yellow"},
            {"op": "remove", "path": "/prop"},
            {"op": "replace", "path": "/company", "value": "CosmosDB"},
            {"op": "set", "path": "/address/new_city", "value": "Atlanta"},
            {"op": "incr", "path": "/number", "value": 7},
            {"op": "move", "from": "/color", "path": "/favorite_color"}
        ]
        binding = importlib.import_module(type(self.client._adapter).__module__)._rust_module
        with patch.object(binding, "patch_item", wraps=binding.patch_item) as operation:
            self.container.patch_item(
                item="patch_item",
                partition_key=pkValue,
                patch_operations=operations,
                throughput_bucket=request_throughput_bucket_number)
        self.assertTrue(operation.called)
        for call in operation.call_args_list:
            self.assertEqual(call.args[1].settings.throughput_bucket, request_throughput_bucket_number)
