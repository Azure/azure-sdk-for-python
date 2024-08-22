# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
from unittest.mock import MagicMock

import pytest

import test_config
from azure.cosmos import Offer, http_constants, CosmosClient, DatabaseProxy, ContainerProxy


@pytest.mark.cosmosEmulator
class TestBackwardsCompatibility(unittest.TestCase):
    configs = test_config.TestConfig
    databaseForTest: DatabaseProxy = None
    client: CosmosClient = None
    containerForTest: ContainerProxy = None
    host = configs.host

    populate_true = True

    @classmethod
    def setUpClass(cls):
        cls.client = CosmosClient(cls.host, test_config.TestConfig.credential)
        cls.databaseForTest = cls.client.get_database_client(cls.configs.TEST_DATABASE_ID)
        cls.containerForTest = cls.databaseForTest.get_container_client(cls.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)

    def test_offer_methods(self):
        database_offer = self.databaseForTest.get_throughput()
        container_offer = self.containerForTest.get_throughput()

        self.assertTrue("ThroughputProperties" in str(type(database_offer)))
        self.assertTrue("ThroughputProperties" in str(type(container_offer)))

        self.assertTrue(isinstance(database_offer, Offer))
        self.assertTrue(isinstance(container_offer, Offer))

    def side_effect_populate_partition_key_range_statistics(self, *args, **kwargs):
        # Extract request headers from args
        self.assertTrue(args[2][http_constants.HttpHeaders.PopulatePartitionKeyRangeStatistics] is True)
        raise StopIteration

    def side_effect_populate_quota_info(self, *args, **kwargs):
        # Extract request headers from args
        self.assertTrue(args[2][http_constants.HttpHeaders.PopulateQuotaInfo] is True)
        raise StopIteration

    def test_populate_quota_info(self):
        cosmos_client_connection = self.containerForTest.client_connection
        cosmos_client_connection._CosmosClientConnection__Get = MagicMock(
            side_effect=self.side_effect_populate_quota_info)
        try:
            self.containerForTest.read(populate_quota_info=True)
        except StopIteration:
            pass
        try:
            self.containerForTest.read(False, False, True)
        except StopIteration:
            pass

    def test_populate_partition_key_range_statistics(self):
        cosmos_client_connection = self.containerForTest.client_connection
        cosmos_client_connection._CosmosClientConnection__Get = MagicMock(
            side_effect=self.side_effect_populate_partition_key_range_statistics)
        try:
            self.containerForTest.read(populate_partition_key_range_statistics=True)
        except StopIteration:
            pass
        try:
            self.containerForTest.read(False, True)
        except StopIteration:
            pass


if __name__ == "__main__":
    unittest.main()
