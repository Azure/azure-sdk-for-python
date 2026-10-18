# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original container offer assertions with write responses disabled."""

import os
import unittest
import uuid

from azure.cosmos import CosmosClient, PartitionKey, documents


class TestCRUDOperationsResponsePayloadOnWriteDisabled(unittest.TestCase):
    def setUp(self):
        self.client = CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust", no_response_on_write=True,
        )
        self.addCleanup(self.client.close)
        self.database = self.client.create_database("throughput_noresponse_" + uuid.uuid4().hex)
        self.addCleanup(self.client.delete_database, self.database.id)
        self.container = self.database.create_container(
            "orders", partition_key=PartitionKey(path="/id"), offer_throughput=400,
        )

    def __ValidateOfferResponseBody(self, offer, expected_coll_link, expected_offer_type):
        self.assertIsNotNone(offer.properties['id'], 'Id cannot be null.')
        self.assertIsNotNone(offer.properties.get('_rid'), 'Resource Id (Rid) cannot be null.')
        self.assertIsNotNone(offer.properties.get('_self'), 'Self Link cannot be null.')
        self.assertIsNotNone(offer.properties.get('resource'), 'Resource Link cannot be null.')
        self.assertTrue(offer.properties['_self'].find(offer.properties['id']) != -1,
                        'Offer id not contained in offer self link.')
        self.assertEqual(expected_coll_link.strip('/'), offer.properties['resource'].strip('/'))
        if expected_offer_type:
            self.assertEqual(expected_offer_type, offer.properties.get('offerType'))

    def test_offer_read_and_query(self):
        # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_offer_read_and_query
        collection = self.container
        expected_offer = collection.get_throughput()
        collection_properties = collection.read()
        self.__ValidateOfferResponseBody(expected_offer, collection_properties.get('_self'), None)

    def test_partitioned_collection(self):
        # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_partitioned_collection
        created_db = self.database
        collection_definition = {
            "id": "partitioned", "partitionKey": {"paths": ["/id"], "kind": documents.PartitionKind.Hash},
        }
        offer_throughput = 10100
        created_collection = created_db.create_container(
            id=collection_definition["id"], partition_key=collection_definition["partitionKey"],
            offer_throughput=offer_throughput,
        )
        self.assertEqual(collection_definition.get('id'), created_collection.id)
        created_collection_properties = created_collection.read(
            populate_partition_key_range_statistics=True, populate_quota_info=True,
        )
        self.assertEqual(collection_definition.get('partitionKey').get('paths')[0],
                         created_collection_properties['partitionKey']['paths'][0])
        self.assertEqual(collection_definition.get('partitionKey').get('kind'),
                         created_collection_properties['partitionKey']['kind'])
        self.assertIsNotNone(created_collection_properties.get("statistics"))
        self.assertIsNotNone(created_db.client_connection.last_response_headers.get("x-ms-resource-usage"))
        expected_offer = created_collection.get_throughput()
        self.assertIsNotNone(expected_offer)
        self.assertEqual(expected_offer.offer_throughput, offer_throughput)
        created_db.delete_container(created_collection.id)

    def test_offer_replace(self):
        # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_offer_replace
        collection = self.container
        expected_offer = collection.get_throughput()
        collection_properties = collection.read()
        self.__ValidateOfferResponseBody(expected_offer, collection_properties.get('_self'), None)
        replaced_offer = collection.replace_throughput(expected_offer.offer_throughput + 100)
        collection_properties = collection.read()
        self.__ValidateOfferResponseBody(replaced_offer, collection_properties.get('_self'), None)
        self.assertEqual(expected_offer.properties.get('content').get('offerThroughput') + 100,
                         replaced_offer.properties.get('content').get('offerThroughput'))
        self.assertEqual(expected_offer.offer_throughput + 100, replaced_offer.offer_throughput)
