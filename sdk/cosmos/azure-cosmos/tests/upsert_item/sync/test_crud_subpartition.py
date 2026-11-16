# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original sync hierarchical-partition document CRUD test, re-run on the Rust path.

Source: ``tests/test_crud_subpartition.py::TestSubpartitionCrud``. The method
keeps the original steps and assertions; only setup changed. The client uses
``_backend="rust"`` and the test owns a uniquely named database (the original
creates its own ``/city``, ``/zipcode`` MultiHash container inside it),
deleted afterwards.
"""

import pytest
import os
import unittest
import uuid

import azure.cosmos.documents as documents
import azure.cosmos.exceptions as exceptions
from azure.cosmos import CosmosClient
from azure.cosmos.http_constants import StatusCodes, SubStatusCodes
from azure.cosmos.partition_key import PartitionKey


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestSubpartitionCrud(unittest.TestCase):

    def setUp(self):
        self.client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
        self.addCleanup(self.client.close)
        self._db_id = "upsert_item_crud_subpartition_" + uuid.uuid4().hex
        self.databaseForTest = self.client.create_database(self._db_id)
        self.addCleanup(self.client.delete_database, self._db_id)

    def _create_container_for_test(self, container_id, partition_key, **kwargs):
        self.databaseForTest.create_container(id=container_id, partition_key=partition_key, **kwargs)
        return self.databaseForTest.get_container_client(container_id)

    def _delete_container_for_test(self, container_id_or_container):
        cid = container_id_or_container if isinstance(container_id_or_container, str) else container_id_or_container.id
        self.databaseForTest.delete_container(cid)

    def test_partitioned_collection_document_crud_and_query_subpartition_rust(self):
        # Source: tests/test_crud_subpartition.py::TestSubpartitionCrud.test_partitioned_collection_document_crud_and_query_subpartition
        created_db = self.databaseForTest

        collection_id = 'test_partitioned_collection_partition_document_crud_and_query_MH ' + str(uuid.uuid4())
        created_collection = self._create_container_for_test(
            container_id=collection_id,
            partition_key=PartitionKey(path=['/city', '/zipcode'], kind=documents.PartitionKind.MultiHash)
        )

        document_definition = {'id': 'document',
                               'key': 'value',
                               'city': 'Redmond',
                               'zipcode': '98052'}

        created_document = created_collection.create_item(
            body=document_definition
        )

        self.assertEqual(created_document.get('id'), document_definition.get('id'))
        self.assertEqual(created_document.get('key'), document_definition.get('key'))
        self.assertEqual(created_document.get('city'), document_definition.get('city'))
        self.assertEqual(created_document.get('zipcode'), document_definition.get('zipcode'))

        # read document
        read_document = created_collection.read_item(
            item=created_document.get('id'),
            partition_key=[created_document.get('city'), created_document.get('zipcode')]
        )

        self.assertEqual(read_document.get('id'), created_document.get('id'))
        self.assertEqual(read_document.get('key'), created_document.get('key'))
        self.assertEqual(read_document.get('city'), created_document.get('city'))
        self.assertEqual(read_document.get('zipcode'), created_document.get('zipcode'))

        # Read document feed doesn't require partitionKey as it's always a cross partition query
        documentlist = list(created_collection.read_all_items())
        self.assertEqual(1, len(documentlist))

        # replace document
        document_definition['key'] = 'new value'

        replaced_document = created_collection.replace_item(
            item=read_document,
            body=document_definition
        )

        self.assertEqual(replaced_document.get('key'), document_definition.get('key'))

        # upsert document(create scenario)
        document_definition['id'] = 'document2'
        document_definition['key'] = 'value2'
        document_definition['city'] = 'Atlanta'
        document_definition['zipcode'] = '30363'

        upserted_document = created_collection.upsert_item(body=document_definition)

        self.assertEqual(upserted_document.get('id'), document_definition.get('id'))
        self.assertEqual(upserted_document.get('key'), document_definition.get('key'))
        self.assertEqual(upserted_document.get('city'), document_definition.get('city'))
        self.assertEqual(upserted_document.get('zipcode'), document_definition.get('zipcode'))

        documentlist = list(created_collection.read_all_items())
        self.assertEqual(2, len(documentlist))

        # delete document
        created_collection.delete_item(item=upserted_document, partition_key=[upserted_document.get('city'),
                                                                              upserted_document.get('zipcode')])

        # query document on the partition key specified in the predicate will pass even without setting
        # enableCrossPartitionQuery or passing in the partitionKey value
        documentlist = list(created_collection.query_items(
            {
                'query': 'SELECT * FROM root r WHERE r.city=\'' + replaced_document.get(
                    'city') + '\' and r.zipcode=\'' + replaced_document.get('zipcode') + '\''
                # pylint: disable=line-too-long
            }))
        self.assertEqual(1, len(documentlist))

        # query document on any property other than partitionKey will fail without setting enableCrossPartitionQuery
        # or passing in the partitionKey value
        try:
            list(created_collection.query_items(
                {
                    'query': 'SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\''  # nosec
                }))
        except Exception:
            pass

        # cross partition query
        documentlist = list(created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
            enable_cross_partition_query=True
        ))

        self.assertEqual(1, len(documentlist))

        # query document by providing the partitionKey value
        documentlist = list(created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
            partition_key=[replaced_document.get('city'), replaced_document.get('zipcode')]
        ))

        self.assertEqual(1, len(documentlist))

        # Using incomplete extracted partition key in item body
        incomplete_document = {'id': 'document3',
                               'key': 'value3',
                               'city': 'Vancouver'}

        try:
            created_collection.create_item(body=incomplete_document)
            self.fail("Test did not fail as expected")
        except exceptions.CosmosHttpResponseError as error:
            self.assertEqual(error.status_code, StatusCodes.BAD_REQUEST)
            self.assertEqual(error.sub_status, SubStatusCodes.PARTITION_KEY_MISMATCH)

        # using incomplete partition key in read item
        try:
            created_collection.read_item(created_document, partition_key=["Redmond"])
            self.fail("Test did not fail as expected")
        except exceptions.CosmosHttpResponseError as error:
            self.assertEqual(error.status_code, StatusCodes.BAD_REQUEST)
            self.assertEqual(error.sub_status, SubStatusCodes.PARTITION_KEY_MISMATCH)

        # using mix value types for partition key
        doc_mixed_types = {'id': "doc4",
                           'key': 'value4',
                           'city': None,
                           'zipcode': 1000}
        created_mixed_type_doc = created_collection.create_item(body=doc_mixed_types)
        self.assertEqual(doc_mixed_types.get('city'), created_mixed_type_doc.get('city'))
        self.assertEqual(doc_mixed_types.get('zipcode'), created_mixed_type_doc.get('zipcode'))

        # Known gap 23: Container delete and replace require preliminary metadata (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-23). On Rust this delete_container step first resolves container metadata (possible extra GET) before the DELETE; the step still executes.
        self._delete_container_for_test(collection_id)


if __name__ == "__main__":
    unittest.main()
