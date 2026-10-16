# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Retain legacy autoscale-container assertions with owned fixtures and Rust selection."""

import os
import unittest
import uuid

from azure.cosmos import CosmosClient, PartitionKey, ThroughputProperties, exceptions


class TestAutoScale(unittest.TestCase):
    def setUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.database = self.client.create_database("container_autoscale_" + uuid.uuid4().hex)

    def tearDown(self):
        try:
            self.client.delete_database(self.database.id)
        finally:
            self.client.close()

    def test_autoscale_create_container(self):
        # Source: tests/test_auto_scale.py::TestAutoScale.test_autoscale_create_container
        container = self.database.create_container(
            id="auto_scale", partition_key=PartitionKey(path="/id"),
            offer_throughput=ThroughputProperties(auto_scale_max_throughput=7000, auto_scale_increment_percent=0),
        )
        result = container.get_throughput()
        assert result.auto_scale_max_throughput == 7000
        assert result.auto_scale_increment_percent == 0
        assert result.offer_throughput is None
        self.database.delete_container(container)
        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            self.database.create_container(
                id="container_with_wrong_auto_scale_settings", partition_key=PartitionKey(path="/id"),
                offer_throughput=ThroughputProperties(auto_scale_max_throughput=-200, auto_scale_increment_percent=0),
            )
        assert "Requested throughput -200 is less than required minimum throughput 1000" in str(caught.exception)
        container = self.database.create_container_if_not_exists(
            id="auto_scale_2", partition_key=PartitionKey(path="/id"),
            offer_throughput=ThroughputProperties(auto_scale_max_throughput=1000, auto_scale_increment_percent=3),
        )
        result = container.get_throughput()
        assert result.auto_scale_max_throughput == 1000
        assert result.auto_scale_increment_percent == 3
