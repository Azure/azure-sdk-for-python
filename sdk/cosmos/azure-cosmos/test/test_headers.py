# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
from unittest.mock import MagicMock

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import DatabaseProxy


@pytest.mark.cosmosEmulator
class TestHeaders(unittest.TestCase):
    database: DatabaseProxy = None
    client: cosmos_client.CosmosClient = None
    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey

    dedicated_gateway_max_age_thousand = 1000
    dedicated_gateway_max_age_million = 1000000
    dedicated_gateway_max_age_negative = -1

    @classmethod
    def setUpClass(cls):
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.database = cls.client.get_database_client(cls.configs.TEST_DATABASE_ID)
        cls.container = cls.database.get_container_client(cls.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

    def side_effect_dedicated_gateway_max_age_thousand(self, *args, **kwargs):
        # Extract request headers from args
        assert args[2]["x-ms-dedicatedgateway-max-age"] == self.dedicated_gateway_max_age_thousand
        raise StopIteration

    def side_effect_dedicated_gateway_max_age_million(self, *args, **kwargs):
        # Extract request headers from args
        assert args[2]["x-ms-dedicatedgateway-max-age"] == self.dedicated_gateway_max_age_million
        raise StopIteration

    def side_effect_correlated_activity_id(self, *args, **kwargs):
        # Extract request headers from args
        assert args[3]["x-ms-cosmos-correlated-activityid"]  # cspell:disable-line
        raise StopIteration

    def test_correlated_activity_id(self):
        query = 'SELECT * from c ORDER BY c._ts'

        cosmos_client_connection = self.container.client_connection
        cosmos_client_connection._CosmosClientConnection__Post = MagicMock(
            side_effect=self.side_effect_correlated_activity_id)
        try:
            list(self.container.query_items(query=query, partition_key="pk-1"))
        except StopIteration:
            pass

    def test_max_integrated_cache_staleness(self):
        cosmos_client_connection = self.container.client_connection
        cosmos_client_connection._CosmosClientConnection__Get = MagicMock(
            side_effect=self.side_effect_dedicated_gateway_max_age_thousand)
        try:
            self.container.read_item(item="id-1", partition_key="pk-1",
                                     max_integrated_cache_staleness_in_ms=self.dedicated_gateway_max_age_thousand)
        except StopIteration:
            pass

        cosmos_client_connection._CosmosClientConnection__Get = MagicMock(
            side_effect=self.side_effect_dedicated_gateway_max_age_million)
        try:
            self.container.read_item(item="id-1", partition_key="pk-1",
                                     max_integrated_cache_staleness_in_ms=self.dedicated_gateway_max_age_million)
        except StopIteration:
            pass

    def test_negative_max_integrated_cache_staleness(self):
        try:
            self.container.read_item(item="id-1", partition_key="pk-1",
                                     max_integrated_cache_staleness_in_ms=self.dedicated_gateway_max_age_negative)
        except Exception as exception:
            assert isinstance(exception, ValueError)


if __name__ == "__main__":
    unittest.main()
