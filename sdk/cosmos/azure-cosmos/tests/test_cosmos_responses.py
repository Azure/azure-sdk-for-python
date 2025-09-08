# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import test_config
from azure.cosmos import CosmosClient, PartitionKey, ContainerProxy, DatabaseProxy
from azure.cosmos.http_constants import HttpHeaders


# TODO: add more tests in this file once we have response headers in control plane operations
# TODO: add query tests once those changes are available

@pytest.mark.cosmosEmulator
class TestCosmosResponses(unittest.TestCase):
    """Python Cosmos Responses Tests.
    """

    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    client: CosmosClient = None
    test_database: DatabaseProxy = None
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.client = CosmosClient(cls.host, cls.masterKey)
        cls.test_database = cls.client.get_database_client(cls.TEST_DATABASE_ID)

    def test_point_operation_headers(self):
        container = self.test_database.create_container(id="responses_test" + str(uuid.uuid4()),
                                                        partition_key=PartitionKey(path="/company"))
        first_response = container.upsert_item({"id": str(uuid.uuid4()), "company": "Microsoft"})
        lsn = first_response.get_response_headers()['lsn']

        create_response = container.create_item({"id": str(uuid.uuid4()), "company": "Microsoft"})
        assert len(create_response.get_response_headers()) > 0
        assert int(lsn) + 1 == int(create_response.get_response_headers()['lsn'])
        lsn = create_response.get_response_headers()['lsn']

        read_response = container.read_item(create_response['id'], create_response['company'])
        assert len(read_response.get_response_headers()) > 0

        upsert_response = container.upsert_item({"id": str(uuid.uuid4()), "company": "Microsoft"})
        assert len(upsert_response.get_response_headers()) > 0
        assert int(lsn) + 1 == int(upsert_response.get_response_headers()['lsn'])
        lsn = upsert_response.get_response_headers()['lsn']

        upsert_response['replace'] = True
        replace_response = container.replace_item(upsert_response['id'], upsert_response)
        assert replace_response['replace'] is not None
        assert len(replace_response.get_response_headers()) > 0
        assert int(lsn) + 1 == int(replace_response.get_response_headers()['lsn'])

        batch = []
        for i in range(50):
            batch.append(("create", ({"id": "item" + str(i), "company": "Microsoft"},)))
        batch_response = container.execute_item_batch(batch_operations=batch, partition_key="Microsoft")
        assert len(batch_response.get_response_headers()) > 0
        assert int(lsn) + 1 < int(batch_response.get_response_headers()['lsn'])

    def test_create_database_headers(self):
        first_response = self.client.create_database(id="responses_test" + str(uuid.uuid4()), return_properties=True)

        assert len(first_response[1].get_response_headers()) > 0

    def test_create_database_returns_database_proxy(self):
        first_response = self.client.create_database(id="responses_test" + str(uuid.uuid4()))
        assert isinstance(first_response, DatabaseProxy)

    def test_create_database_if_not_exists_headers(self):
        first_response = self.client.create_database_if_not_exists(id="responses_test" + str(uuid.uuid4()), return_properties=True)
        assert len(first_response[1].get_response_headers()) > 0

    def test_create_database_if_not_exists_headers_negative(self):
        first_response = self.client.create_database_if_not_exists(id="responses_test", return_properties=True)
        second_response = self.client.create_database_if_not_exists(id="responses_test", return_properties=True)
        assert len(second_response[1].get_response_headers()) > 0

    def test_create_container_headers(self):
        first_response = self.test_database.create_container(id="responses_test" + str(uuid.uuid4()),
                                                             partition_key=PartitionKey(path="/company"), return_properties=True)
        assert len(first_response[1].get_response_headers()) > 0

    def test_create_container_returns_container_proxy(self):
        first_response = self.test_database.create_container(id="responses_test" + str(uuid.uuid4()),
                                                        partition_key=PartitionKey(path="/company"))
        assert isinstance(first_response, ContainerProxy)

    def test_create_container_if_not_exists_headers(self):
        first_response = self.test_database.create_container_if_not_exists(id="responses_test" + str(uuid.uuid4()),
                                                        partition_key=PartitionKey(path="/company"), return_properties=True)
        assert len(first_response[1].get_response_headers()) > 0

    def test_create_container_if_not_exists_headers_negative(self):
        first_response = self.test_database.create_container_if_not_exists(id="responses_test",
                                                        partition_key=PartitionKey(path="/company"), return_properties=True)
        second_response = self.test_database.create_container_if_not_exists(id="responses_test",
                                                        partition_key=PartitionKey(path="/company"), return_properties=True)
        assert len(second_response[1].get_response_headers()) > 0

    def test_replace_container_headers(self):
        first_response = self.test_database.create_container_if_not_exists(id="responses_test" + str(uuid.uuid4()),
                                                        partition_key=PartitionKey(path="/company"))
        second_response = self.test_database.replace_container(first_response.id,
                                                               partition_key=PartitionKey(path="/company"), return_properties=True)
        assert len(second_response[1].get_response_headers()) > 0

    def test_database_read_headers(self):
        db = self.client.create_database(id="responses_test" + str(uuid.uuid4()))
        first_response = db.read()
        assert len(first_response.get_response_headers()) > 0

    def test_container_read_headers(self):
        container = self.test_database.create_container(id="responses_test" + str(uuid.uuid4()),
                                                             partition_key=PartitionKey(path="/company"))
        first_response = container.read()
        assert len(first_response.get_response_headers()) > 0

    def test_container_replace_throughput(self):
        container = self.test_database.create_container(id="responses_test" + str(uuid.uuid4()),
                                                        partition_key=PartitionKey(path="/company"), offer_throughput=400)
        replace_throughput_value = 500
        first_response = container.replace_throughput(replace_throughput_value)
        assert len(first_response.get_response_headers()) > 0
        assert replace_throughput_value == container.get_throughput().offer_throughput

    def test_database_replace_throughput(self):
        db = self.client.create_database(id="responses_test" + str(uuid.uuid4()), offer_throughput=400)
        replace_throughput_value = 500
        first_response = db.replace_throughput(replace_throughput_value)
        assert len(first_response.get_response_headers()) > 0
        assert replace_throughput_value == db.get_throughput().offer_throughput

if __name__ == '__main__':
    unittest.main()
