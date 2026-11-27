# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Main's explicit-None container read."""

import pytest
from azure.cosmos import PartitionKey
from read_container._container_setup import SyncContainerReadCase


@pytest.mark.cosmosEmulator
class TestNoneOptions(SyncContainerReadCase):
    def setUp(self):
        super().setUp()
        self.key_db.create_container("orders", PartitionKey(path="/pk"))
        self.container = self.data_db.get_container_client("orders")

    def test_container_read_none_options_rust(self):
        # Source: tests/test_none_options.py::TestNoneOptions.test_container_read_none_options
        result = self.container.read(populate_partition_key_range_statistics=None, populate_quota_info=None,
                                     priority=None, initial_headers=None)
        assert result
