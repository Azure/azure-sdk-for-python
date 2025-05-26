# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import unittest
from unittest.mock import MagicMock

import pytest
import uuid

import azure.cosmos.cosmos_client as cosmos_client
import test_config
import azure.cosmos.exceptions as exceptions
from azure.cosmos import http_constants, DatabaseProxy, _endpoint_discovery_retry_policy
from azure.cosmos.partition_key import PartitionKey

client_throughput_bucket_number = 2
request_throughput_bucket_number = 3
def client_raw_response_hook(response):
    assert (response.http_request.headers[http_constants.HttpHeaders.ThroughputBucket]
            == str(client_throughput_bucket_number))

def request_raw_response_hook(response):
        assert (response.http_request.headers[http_constants.HttpHeaders.ThroughputBucket]
                == str(request_throughput_bucket_number))

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
        original_connection_post = cosmos_client_connection._CosmosClientConnection__Post
        cosmos_client_connection._CosmosClientConnection__Post = MagicMock(
            side_effect=self.side_effect_correlated_activity_id)
        try:
            list(self.container.query_items(query=query, partition_key="pk-1"))
        except StopIteration:
            pass
        finally:
            cosmos_client_connection._CosmosClientConnection__Post = original_connection_post

    def test_max_integrated_cache_staleness(self):
        cosmos_client_connection = self.container.client_connection
        original_connection_get = cosmos_client_connection._CosmosClientConnection__Get
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
        finally:
            cosmos_client_connection._CosmosClientConnection__Get = original_connection_get

    def test_negative_max_integrated_cache_staleness(self):
        try:
            self.container.read_item(item="id-1", partition_key="pk-1",
                                     max_integrated_cache_staleness_in_ms=self.dedicated_gateway_max_age_negative)
        except Exception as exception:
            assert isinstance(exception, ValueError)

    def test_client_level_throughput_bucket(self):
        cosmos_client.CosmosClient(self.host, self.masterKey,
            throughput_bucket=client_throughput_bucket_number,
            raw_response_hook=client_raw_response_hook)

    def test_request_precedence_throughput_bucket(self):
        client = cosmos_client.CosmosClient(self.host, self.masterKey,
                                   throughput_bucket=client_throughput_bucket_number)
        created_db = client.get_database_client(self.configs.TEST_DATABASE_ID)
        created_container = created_db.create_container(
            str(uuid.uuid4()),
            PartitionKey(path="/pk"))
        created_container.create_item(
            body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)
        created_db.delete_container(created_container.id)

    def test_container_read_item_throughput_bucket(self):
        created_document = self.container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        self.container.read_item(
             item=created_document['id'],
             partition_key="mypk",
             throughput_bucket=request_throughput_bucket_number,
             raw_response_hook=request_raw_response_hook)

    def test_container_read_all_items_throughput_bucket(self):
        for i in range(10):
            self.container.create_item(body={'id': ''.format(i) + str(uuid.uuid4()), 'pk': 'mypk'})

        self.container.read_all_items(
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

    def test_container_query_items_throughput_bucket(self):
        doc_id = 'MyId' + str(uuid.uuid4())
        document_definition = {'pk': 'pk', 'id': doc_id}
        self.container.create_item(body=document_definition)

        query = 'SELECT * from c'
        self.container.query_items(
            query=query,
            partition_key='pk',
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

    def test_container_replace_item_throughput_bucket(self):
        created_document = self.container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        self.container.replace_item(
            item=created_document['id'],
            body={'id': '2' + str(uuid.uuid4()), 'pk': 'mypk'},
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

    def test_container_upsert_item_throughput_bucket(self):
       self.container.upsert_item(
            body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

    def test_container_create_item_throughput_bucket(self):
        self.container.create_item(
            body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

    def test_container_patch_item_throughput_bucket(self):
        pkValue = "patch_item_pk" + str(uuid.uuid4())
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
        self.container.patch_item(
            item="patch_item",
            partition_key=pkValue,
            patch_operations=operations,
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

    def test_container_execute_item_batch_throughput_bucket(self):
        created_collection = self.database.create_container(
            id='test_execute_item ' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/company'))
        batch = []
        for i in range(100):
            batch.append(("create", ({"id": "item" + str(i), "company": "Microsoft"},)))

        created_collection.execute_item_batch(
            batch_operations=batch,
            partition_key="Microsoft",
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

        self.database.delete_container(created_collection)

    def test_container_delete_item_throughput_bucket(self):
        created_item = self.container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})

        self.container.delete_item(
            created_item['id'],
            partition_key='mypk',
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

    def test_container_delete_all_items_by_partition_key_throughput_bucket(self):
        created_collection = self.database.create_container(
            id='test_delete_all_items_by_partition_key ' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/pk', kind='Hash'))

        # Create two partition keys
        partition_key1 = "{}-{}".format("Partition Key 1", str(uuid.uuid4()))
        partition_key2 = "{}-{}".format("Partition Key 2", str(uuid.uuid4()))

        # add items for partition key 1
        for i in range(1, 3):
            created_collection.upsert_item(
                dict(id="item{}".format(i), pk=partition_key1))

        # add items for partition key 2
        pk2_item = created_collection.upsert_item(dict(id="item{}".format(3), pk=partition_key2))

        # delete all items for partition key 1
        created_collection.delete_all_items_by_partition_key(
            partition_key1,
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)

        self.database.delete_container(created_collection)

    # TODO Re-enable once Throughput Bucket Validation Changes are rolled out
    """
    def test_container_read_item_negative_throughput_bucket(self):
        # Creates an item and then tries to read item with an invalid throughput bucket
        created_document = self.container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})
        try:
            self.container.read_item(
                 item=created_document['id'],
                 partition_key="mypk",
                 throughput_bucket=256)
            pytest.fail("Read Item should have failed invalid throughput bucket.")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == 400
            assert "specified for the header 'x-ms-cosmos-throughput-bucket' is invalid." in e.http_error_message

    """

if __name__ == "__main__":
    unittest.main()
