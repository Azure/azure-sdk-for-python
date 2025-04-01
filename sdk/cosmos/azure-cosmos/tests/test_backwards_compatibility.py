# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
import uuid

import pytest

import test_config
from azure.core import MatchConditions
from azure.cosmos import Offer, http_constants, CosmosClient, DatabaseProxy, ContainerProxy, PartitionKey
from azure.cosmos.exceptions import CosmosHttpResponseError

def check_pk_range_statistics_request_headers(raw_response):
    assert raw_response.http_request.headers[http_constants.HttpHeaders.PopulatePartitionKeyRangeStatistics] == 'True'

def check_quota_info_request_headers(raw_response):
    assert raw_response.http_request.headers[http_constants.HttpHeaders.PopulateQuotaInfo] == 'True'

@pytest.mark.cosmosEmulator
class TestBackwardsCompatibility(unittest.TestCase):
    configs = test_config.TestConfig
    databaseForTest: DatabaseProxy = None
    client: CosmosClient = None
    containerForTest: ContainerProxy = None
    host = configs.host
    masterKey = configs.masterKey

    populate_true = True

    @classmethod
    def setUpClass(cls):
        if cls.masterKey == '[YOUR_KEY_HERE]' or cls.host == '[YOUR_ENDPOINT_HERE]':
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.client = CosmosClient(cls.host, cls.masterKey)
        cls.databaseForTest = cls.client.get_database_client(cls.configs.TEST_DATABASE_ID)
        cls.containerForTest = cls.databaseForTest.get_container_client(cls.configs.TEST_SINGLE_PARTITION_CONTAINER_ID)

    def test_offer_methods(self):
        database_offer = self.databaseForTest.get_throughput()
        container_offer = self.containerForTest.get_throughput()

        self.assertTrue("ThroughputProperties" in str(type(database_offer)))
        self.assertTrue("ThroughputProperties" in str(type(container_offer)))

        self.assertTrue(isinstance(database_offer, Offer))
        self.assertTrue(isinstance(container_offer, Offer))

    def test_populate_quota_info(self):
            self.containerForTest.read(populate_quota_info=True, raw_response_hook=check_quota_info_request_headers)
            self.containerForTest.read(False, False, True, raw_response_hook=check_quota_info_request_headers)

    def test_populate_partition_key_range_statistics(self):
        self.containerForTest.read(populate_partition_key_range_statistics=True, raw_response_hook=check_pk_range_statistics_request_headers)
        self.containerForTest.read(False, True, raw_response_hook=check_pk_range_statistics_request_headers)

    def test_session_token_compatibility(self):
        # Verifying that behavior is unaffected across the board for using `session_token` on irrelevant methods
        # Database
        database = self.client.create_database(str(uuid.uuid4()), session_token=str(uuid.uuid4()))
        assert database is not None
        database2 = self.client.create_database_if_not_exists(str(uuid.uuid4()), session_token=str(uuid.uuid4()))
        assert database2 is not None
        database_list = list(self.client.list_databases(session_token=str(uuid.uuid4())))
        database_list2 = list(self.client.query_databases(query="select * from c", session_token=str(uuid.uuid4())))
        assert len(database_list) > 0
        assert database_list == database_list2
        database_read = database.read(session_token=str(uuid.uuid4()))
        assert database_read is not None
        self.client.delete_database(database2.id, session_token=str(uuid.uuid4()))
        try:
            database2.read()
            pytest.fail("Database read should have failed")
        except CosmosHttpResponseError as e:
            assert e.status_code == 404

        # Container
        container = database.create_container(str(uuid.uuid4()), PartitionKey(path="/pk"), session_token=str(uuid.uuid4()))
        assert container is not None
        container2 = database.create_container_if_not_exists(str(uuid.uuid4()), PartitionKey(path="/pk"), session_token=str(uuid.uuid4()))
        assert container2 is not None
        container_list = list(database.list_containers(session_token=str(uuid.uuid4())))
        container_list2 = list(database.query_containers(query="select * from c", session_token=str(uuid.uuid4())))
        assert len(container_list) > 0
        assert container_list == container_list2
        container2_read = container2.read(session_token=str(uuid.uuid4()))
        assert container2_read is not None
        replace_container = database.replace_container(container2, PartitionKey(path="/pk"), default_ttl=30, session_token=str(uuid.uuid4()))
        replace_container_read = replace_container.read()
        assert replace_container is not None
        assert replace_container_read != container2_read
        assert 'defaultTtl' in replace_container_read # Check for default_ttl as a new additional property
        database.delete_container(replace_container.id, session_token=str(uuid.uuid4()))
        try:
            container2.read()
            pytest.fail("Container read should have failed")
        except CosmosHttpResponseError as e:
            assert e.status_code == 404

        self.client.delete_database(database.id)

    def test_etag_match_condition_compatibility(self):
        # Verifying that behavior is unaffected across the board for using `etag`/`match_condition` on irrelevant methods
        # Database
        database = self.client.create_database(str(uuid.uuid4()), etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        assert database is not None
        database2 = self.client.create_database_if_not_exists(str(uuid.uuid4()), etag=str(uuid.uuid4()), match_condition=MatchConditions.IfNotModified)
        assert database2 is not None
        self.client.delete_database(database2.id, etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        try:
            database2.read()
            pytest.fail("Database read should have failed")
        except CosmosHttpResponseError as e:
            assert e.status_code == 404

        # Container
        container = database.create_container(str(uuid.uuid4()), PartitionKey(path="/pk"),
                                              etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        assert container is not None
        container2 = database.create_container_if_not_exists(str(uuid.uuid4()), PartitionKey(path="/pk"),
                                                             etag=str(uuid.uuid4()), match_condition=MatchConditions.IfNotModified)
        assert container2 is not None
        container2_read = container2.read()
        assert container2_read is not None
        replace_container = database.replace_container(container2, PartitionKey(path="/pk"), default_ttl=30,
                                                       etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        replace_container_read = replace_container.read()
        assert replace_container is not None
        assert replace_container_read != container2_read
        assert 'defaultTtl' in replace_container_read # Check for default_ttl as a new additional property
        database.delete_container(replace_container.id, etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        try:
            container2.read()
            pytest.fail("Container read should have failed")
        except CosmosHttpResponseError as e:
            assert e.status_code == 404

        # Item
        item = container.create_item({"id": str(uuid.uuid4()), "pk": 0}, etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        assert item is not None
        item2 = container.upsert_item({"id": str(uuid.uuid4()), "pk": 0}, etag=str(uuid.uuid4()),
                                     match_condition=MatchConditions.IfNotModified)
        assert item2 is not None
        item = container.create_item({"id": str(uuid.uuid4()), "pk": 0}, etag=None, match_condition=None)
        assert item is not None
        item2 = container.upsert_item({"id": str(uuid.uuid4()), "pk": 0}, etag=None, match_condition=None)
        assert item2 is not None
        batch_operations = [
            ("create", ({"id": str(uuid.uuid4()), "pk": 0},)),
            ("replace", (item2['id'], {"id": str(uuid.uuid4()), "pk": 0})),
            ("read", (item['id'],)),
            ("upsert", ({"id": str(uuid.uuid4()), "pk": 0},)),
        ]
        batch_results = container.execute_item_batch(batch_operations, partition_key=0, etag=str(uuid.uuid4()), match_condition=MatchConditions.IfModified)
        assert len(batch_results) == 4
        for result in batch_results:
            assert result['statusCode'] in (200, 201)

        self.client.delete_database(database.id)

if __name__ == "__main__":
    unittest.main()
