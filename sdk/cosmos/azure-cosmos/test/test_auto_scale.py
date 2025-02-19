# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import CosmosClient, cosmos_client
from azure.cosmos import ThroughputProperties, PartitionKey

@pytest.mark.cosmosLong
class TestAutoScale(unittest.TestCase):
    client: CosmosClient = None
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.created_database = cls.client.get_database_client(test_config.TestConfig.TEST_DATABASE_ID)

    def test_autoscale_create_container(self):
        container_id = None
        try:
            container_id = 'auto_scale'
            created_container = self.created_database.create_container(
                id=container_id,
                partition_key=PartitionKey(path="/id"),
                offer_throughput=ThroughputProperties(auto_scale_max_throughput=7000, auto_scale_increment_percent=0)

            )
            created_container_properties = created_container.get_throughput()
            # Testing the input value of the max_throughput
            assert created_container_properties.auto_scale_max_throughput == 7000
            assert created_container_properties.auto_scale_increment_percent == 0
            assert created_container_properties.offer_throughput is None

            self.created_database.delete_container(created_container)

            # Testing the incorrect passing of an input value of the max_throughput to verify negative behavior
            with self.assertRaises(exceptions.CosmosHttpResponseError) as e:
                self.created_database.create_container(
                    id='container_with_wrong_auto_scale_settings',
                    partition_key=PartitionKey(path="/id"),
                    offer_throughput=ThroughputProperties(auto_scale_max_throughput=-200, auto_scale_increment_percent=0))
            assert "Requested throughput -200 is less than required minimum throughput 1000" in str(e.exception)

            # Testing auto_scale_settings for the create_container_if_not_exists method
            container_id = 'auto_scale_2'
            created_container = self.created_database.create_container_if_not_exists(
                id=container_id,
                partition_key=PartitionKey(path="/id"),
                offer_throughput=ThroughputProperties(auto_scale_max_throughput=1000, auto_scale_increment_percent=3)
            )
            created_container_properties = created_container.get_throughput()
            # Testing the input value of the max_throughput
            assert created_container_properties.auto_scale_max_throughput == 1000
            # Testing the input value of the increment_percentage
            assert created_container_properties.auto_scale_increment_percent == 3
        finally:
            self.created_database.delete_container(container_id)

    def test_autoscale_create_database(self):
        database_id = "db_auto_scale_" + str(uuid.uuid4())
        try:
            # Testing auto_scale_settings for the create_database method
            created_database = self.client.create_database(database_id, offer_throughput=ThroughputProperties(
                auto_scale_max_throughput=5000,
                auto_scale_increment_percent=2))
            created_db_properties = created_database.get_throughput()
            # Testing the input value of the max_throughput
            assert created_db_properties.auto_scale_max_throughput == 5000
            # Testing the input value of the increment_percentage
            assert created_db_properties.auto_scale_increment_percent == 2

            self.client.delete_database(created_database.id)

            # Testing auto_scale_settings for the create_database_if_not_exists method
            database_id = "db_auto_scale_2_" + str(uuid.uuid4())
            created_database = self.client.create_database_if_not_exists(database_id,
                                                                         offer_throughput=ThroughputProperties(
                                                                             auto_scale_max_throughput=9000,
                                                                             auto_scale_increment_percent=11))
            created_db_properties = created_database.get_throughput()
            # Testing the input value of the max_throughput
            assert created_db_properties.auto_scale_max_throughput == 9000
            # Testing the input value of the increment_percentage
            assert created_db_properties.auto_scale_increment_percent == 11
        finally:
            self.client.delete_database(database_id)

    def test_autoscale_replace_throughput(self):
        database_id = "replace_db" + str(uuid.uuid4())
        container_id = None
        try:
            created_database = self.client.create_database(database_id, offer_throughput=ThroughputProperties(
                auto_scale_max_throughput=5000,
                auto_scale_increment_percent=2))
            created_database.replace_throughput(
                throughput=ThroughputProperties(auto_scale_max_throughput=7000, auto_scale_increment_percent=20))
            created_db_properties = created_database.get_throughput()
            # Testing the input value of the max_throughput
            assert created_db_properties.auto_scale_max_throughput == 7000
            # Testing the input value of the increment_percentage
            assert created_db_properties.auto_scale_increment_percent == 20
            self.client.delete_database(database_id)

            container_id = "container_with_auto_scale_settings" + str(uuid.uuid4())
            created_container = self.created_database.create_container(
                id=container_id,
                partition_key=PartitionKey(path="/id"),
                offer_throughput=ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=0))
            created_container.replace_throughput(
                throughput=ThroughputProperties(auto_scale_max_throughput=7000, auto_scale_increment_percent=20))
            created_container_properties = created_container.get_throughput()
            # Testing the input value of the replaced auto_scale settings
            assert created_container_properties.auto_scale_max_throughput == 7000
            assert created_container_properties.auto_scale_increment_percent == 20

        finally:
            self.created_database.delete_container(container_id)


if __name__ == '__main__':
    unittest.main()
