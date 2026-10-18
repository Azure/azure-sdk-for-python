# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original async container offer assertions with write responses disabled."""

import os
import unittest
import uuid

from azure.cosmos import PartitionKey, documents
from azure.cosmos.aio import CosmosClient


class TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust", no_response_on_write=True,
        )
        self.addAsyncCleanup(self.client.close)
        self.database = await self.client.create_database("throughput_noresponse_" + uuid.uuid4().hex)
        self.addAsyncCleanup(self.client.delete_database, self.database.id)
        self.container = await self.database.create_container(
            "orders", partition_key=PartitionKey(path="/id"), offer_throughput=400,
        )

    def __validate_offer_response_body(self, offer, expected_coll_link, expected_offer_type):
        assert offer.properties.get('id') is not None
        assert offer.properties.get('_rid') is not None
        assert offer.properties.get('_self') is not None
        assert offer.properties.get('resource') is not None
        assert offer.properties['_self'].find(offer.properties['id']) != -1
        assert expected_coll_link.strip('/') == offer.properties['resource'].strip('/')
        if expected_offer_type:
            assert expected_offer_type == offer.properties.get('offerType')

    async def test_offer_read_and_query_async(self):
        # Source: tests/test_crud_response_payload_on_write_disabled_async.py::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_offer_read_and_query_async
        collection = self.container
        expected_offer = await collection.get_throughput()
        collection_properties = await collection.read()
        self.__validate_offer_response_body(expected_offer, collection_properties.get('_self'), None)

    async def test_offer_replace_async(self):
        # Source: tests/test_crud_response_payload_on_write_disabled_async.py::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_offer_replace_async
        collection = self.container
        expected_offer = await collection.get_throughput()
        collection_properties = await collection.read()
        self.__validate_offer_response_body(expected_offer, collection_properties.get('_self'), None)
        replaced_offer = await collection.replace_throughput(expected_offer.offer_throughput + 100)
        collection_properties = await collection.read()
        self.__validate_offer_response_body(replaced_offer, collection_properties.get('_self'), None)
        assert (expected_offer.properties.get('content').get('offerThroughput') + 100 ==
                replaced_offer.properties.get('content').get('offerThroughput'))
        assert expected_offer.offer_throughput + 100 == replaced_offer.offer_throughput

    async def test_partitioned_collection_async(self):
        # Source: tests/test_crud_response_payload_on_write_disabled_async.py::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_partitioned_collection_async
        created_db = self.database
        collection_definition = {
            "id": "partitioned", "partitionKey": {"paths": ["/id"], "kind": documents.PartitionKind.Hash},
        }
        offer_throughput = 10100
        created_collection = await created_db.create_container(
            id=collection_definition["id"], partition_key=collection_definition["partitionKey"],
            offer_throughput=offer_throughput,
        )
        assert collection_definition.get('id') == created_collection.id
        created_collection_properties = await created_collection.read()
        assert collection_definition.get('partitionKey').get('paths')[0] == \
               created_collection_properties['partitionKey']['paths'][0]
        assert collection_definition.get('partitionKey').get('kind') == created_collection_properties['partitionKey']['kind']
        expected_offer = await created_collection.get_throughput()
        assert expected_offer is not None
        assert expected_offer.offer_throughput == offer_throughput
        await created_db.delete_container(created_collection.id)
