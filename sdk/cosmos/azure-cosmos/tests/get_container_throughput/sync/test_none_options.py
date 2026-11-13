# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Keep the original explicit-None throughput contract on a Rust-owned fixture."""

from contextlib import ExitStack
import os
import unittest
import uuid

import pytest

from common.throughput_fixtures import owned_database

from azure.cosmos import CosmosClient, PartitionKey


@pytest.mark.cosmosEmulator
class TestNoneOptions(unittest.TestCase):
    def setUp(self):
        self.key_client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.addCleanup(self.key_client.close)
        cleanup = ExitStack()
        self.addCleanup(cleanup.close)
        database = cleanup.enter_context(owned_database(
            self.key_client, "throughput_none_" + uuid.uuid4().hex,
        ))
        self.key_container = database.create_container(
            id="orders", partition_key=PartitionKey(path="/pk"), offer_throughput=400,
        )

    def test_get_throughput_none_options_rust(self):
        # Source: tests/test_none_options.py::TestNoneOptions.test_get_throughput_none_options
        tp = self.key_container.get_throughput(response_hook=None)
        assert tp.offer_throughput > 0
