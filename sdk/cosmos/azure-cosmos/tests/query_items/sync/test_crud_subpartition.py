# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Original sync hierarchical-partition CRUD tests that call ``query_items``, re-run on the Rust path.

Source: ``tests/test_crud_subpartition.py::TestSubpartitionCrud``. Each method
keeps the original steps, query inputs and assertions; only setup changed. The
client uses ``_backend="rust"`` and each test owns a uniquely named database
(the originals create their own MultiHash containers inside it), deleted
afterwards. Known Rust gaps are skipped at the failing step.
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
        self._db_id = "qi_crud_subpartition_" + uuid.uuid4().hex
        self.databaseForTest = self.client.create_database(self._db_id)
        self.addCleanup(self.client.delete_database, self._db_id)

    def _create_container_for_test(self, container_id, partition_key, **kwargs):
        self.databaseForTest.create_container(id=container_id, partition_key=partition_key, **kwargs)
        return self.databaseForTest.get_container_client(container_id)

    def _delete_container_for_test(self, container_id_or_container):
        cid = container_id_or_container if isinstance(container_id_or_container, str) else container_id_or_container.id
        self.databaseForTest.delete_container(cid)

    def test_partitioned_collection_document_crud_and_query_subpartition_rust(self):
        # pylint: disable-next=line-too-long
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

        self._delete_container_for_test(collection_id)

    def test_partitioned_collection_prefix_partition_query_subpartition_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_crud_subpartition.py::TestSubpartitionCrud.test_partitioned_collection_prefix_partition_query_subpartition
        created_db = self.databaseForTest

        collection_id = 'test_partitioned_collection_partition_key_prefix_query_MH ' + str(uuid.uuid4())
        created_collection = self._create_container_for_test(
            container_id=collection_id,
            partition_key=PartitionKey(path=['/state', '/city', '/zipcode'], kind=documents.PartitionKind.MultiHash)
        )

        item_values = [
            ["CA", "Newbury Park", "91319"],
            ["CA", "Oxnard", "93033"],
            ["CA", "Oxnard", "93030"],
            ["CA", "Oxnard", "93036"],
            ["CA", "Thousand Oaks", "91358"],
            ["CA", "Ventura", "93002"],
            ["CA", "Ojai", "93023"],  # cspell:disable-line
            ["CA", "Port Hueneme", "93041"],  # cspell:disable-line
            ["WA", "Seattle", "98101"],
            ["WA", "Bellevue", "98004"]
        ]

        document_definitions = [{'id': 'document1',
                                 'state': item_values[0][0],
                                 'city': item_values[0][1],
                                 'zipcode': item_values[0][2]
                                 },
                                {'id': 'document2',
                                 'state': item_values[1][0],
                                 'city': item_values[1][1],
                                 'zipcode': item_values[1][2]
                                 },
                                {'id': 'document3',
                                 'state': item_values[2][0],
                                 'city': item_values[2][1],
                                 'zipcode': item_values[2][2]
                                 },
                                {'id': 'document4',
                                 'state': item_values[3][0],
                                 'city': item_values[3][1],
                                 'zipcode': item_values[3][2]
                                 },
                                {'id': 'document5',
                                 'state': item_values[4][0],
                                 'city': item_values[4][1],
                                 'zipcode': item_values[4][2]
                                 },
                                {'id': 'document6',
                                 'state': item_values[5][0],
                                 'city': item_values[5][1],
                                 'zipcode': item_values[5][2]
                                 },
                                {'id': 'document7',
                                 'state': item_values[6][0],
                                 'city': item_values[6][1],
                                 'zipcode': item_values[6][2]
                                 },
                                {'id': 'document8',
                                 'state': item_values[7][0],
                                 'city': item_values[7][1],
                                 'zipcode': item_values[7][2]
                                 },
                                {'id': 'document9',
                                 'state': item_values[8][0],
                                 'city': item_values[8][1],
                                 'zipcode': item_values[8][2]
                                 },
                                {'id': 'document10',
                                 'state': item_values[9][0],
                                 'city': item_values[9][1],
                                 'zipcode': item_values[9][2]
                                 }
                                ]
        created_documents = []
        for document_definition in document_definitions:
            created_documents.append(created_collection.create_item(
                body=document_definition))
        self.assertEqual(len(created_documents), len(document_definitions))

        # Query all documents should return all items
        document_list = list(created_collection.query_items(query='Select * from c', enable_cross_partition_query=True))
        self.assertEqual(len(document_list), len(document_definitions))

        # Query all items with only CA for 1st level. Should return only 8 items instead of 10
        document_list = list(created_collection.query_items(query='Select * from c', partition_key=['CA']))
        self.assertEqual(8, len(document_list))

        # Query all items with CA for 1st level and Oxnard for second level. Should only return 3 items
        document_list = list(created_collection.query_items(query='Select * from c', partition_key=['CA', 'Oxnard']))
        self.assertEqual(3, len(document_list))

        # Query for specific zipcode using 1st level of partition key value only:
        document_list = list(created_collection.query_items(query='Select * from c where c.zipcode = "93033"',
                                                            partition_key=['CA']))
        self.assertEqual(1, len(document_list))

        # Query Should work with None values:
        document_list = list(created_collection.query_items(query='Select * from c', partition_key=[None, '93033']))
        self.assertEqual(0, len(document_list))

        # Query Should Work with non string values
        document_list = list(created_collection.query_items(query='Select * from c', partition_key=[0xFF, 0xFF]))
        self.assertEqual(0, len(document_list))

        document_list = list(created_collection.query_items(query='Select * from c', partition_key=[None, None]))
        self.assertEqual(0, len(document_list))

        document_list = list(created_collection.query_items(query='Select * from c', partition_key=["", ""]))
        self.assertEqual(0, len(document_list))

        document_list = list(created_collection.query_items(query='Select * from c', partition_key=[""]))
        self.assertEqual(0, len(document_list))

        # Negative Test, prefix query should not work if no partition is given (empty list is given)
        try:
            document_list = list(
                created_collection.query_items(
                    query="Select * from c", partition_key=[]
                )
            )
            self.fail("Test did not fail as expected")
        except exceptions.CosmosHttpResponseError as error:
            self.assertEqual(error.status_code, StatusCodes.BAD_REQUEST)
            self.assertTrue(
                "Cross partition query is required but disabled" in error.message
            )

        with self.assertRaises(exceptions.CosmosHttpResponseError) as caught:
            list(
                created_collection.query_items(
                    query="Select * from c",
                    partition_key=[],
                    enable_cross_partition_query=False,
                )
            )
        self.assertEqual(caught.exception.status_code, StatusCodes.BAD_REQUEST)
        self.assertIn(
            "Cross partition query is required but disabled", caught.exception.message
        )
        document_list = list(
            created_collection.query_items(
                query="Select * from c",
                partition_key=[],
                enable_cross_partition_query=True,
            )
        )
        self.assertEqual(len(document_list), len(document_definitions))

    def test_partitioned_collection_full_partition_key_pagination_resume_subpartition_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_crud_subpartition.py::TestSubpartitionCrud.test_partitioned_collection_full_partition_key_pagination_resume_subpartition
        created_db = self.databaseForTest
        collection_id = 'test_partitioned_collection_full_partition_key_resume_MH ' + str(uuid.uuid4())
        created_collection = created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path=['/state', '/city', '/zipcode'], kind=documents.PartitionKind.MultiHash)
        )

        partition_key = ['CA', 'Oxnard', '93033']
        total_items = 35
        for i in range(total_items):
            created_collection.create_item(
                body={
                    'id': 'full-pk-doc-{0:03d}'.format(i),
                    'state': partition_key[0],
                    'city': partition_key[1],
                    'zipcode': partition_key[2]
                }
            )

        query = 'SELECT c.id FROM c ORDER BY c.id'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key=partition_key,
            max_item_count=10
        )
        pager = query_iterable.by_page()
        first_page = list(pager.next())
        self.assertGreater(len(first_page), 0)
        token = pager.continuation_token
        self.assertIsNotNone(token)

        expected_remaining_ids = []
        for page in pager:
            expected_remaining_ids.extend(item['id'] for item in page)

        resume_pager = query_iterable.by_page(token)
        resumed_remaining_ids = []
        for page in resume_pager:
            resumed_remaining_ids.extend(item['id'] for item in page)

        self.assertListEqual(expected_remaining_ids, resumed_remaining_ids)

        baseline_ids = [
            item['id'] for item in created_collection.query_items(query=query, partition_key=partition_key)
        ]
        fetched_ids = [item['id'] for item in first_page] + resumed_remaining_ids
        self.assertListEqual(baseline_ids, fetched_ids)

        created_db.delete_container(created_collection.id)

    def test_partitioned_collection_prefix_partition_key_pagination_resume_subpartition_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_crud_subpartition.py::TestSubpartitionCrud.test_partitioned_collection_prefix_partition_key_pagination_resume_subpartition
        created_db = self.databaseForTest
        collection_id = 'test_partitioned_collection_prefix_partition_key_resume_MH ' + str(uuid.uuid4())
        created_collection = created_db.create_container(
            id=collection_id,
            partition_key=PartitionKey(path=['/state', '/city', '/zipcode'], kind=documents.PartitionKind.MultiHash)
        )

        for i in range(30):
            created_collection.create_item(
                body={
                    'id': 'ca-doc-{0:03d}'.format(i),
                    'state': 'CA',
                    'city': 'city-{0}'.format(i % 5),
                    'zipcode': 'zip-{0:03d}'.format(i)
                }
            )
        for i in range(5):
            created_collection.create_item(
                body={
                    'id': 'wa-doc-{0:03d}'.format(i),
                    'state': 'WA',
                    'city': 'city-{0}'.format(i),
                    'zipcode': 'zip-{0:03d}'.format(i)
                }
            )

        query = 'SELECT c.id FROM c ORDER BY c.id'
        query_iterable = created_collection.query_items(
            query=query,
            partition_key=['CA'],
            max_item_count=7
        )
        pager = query_iterable.by_page()
        first_page = list(pager.next())
        self.assertGreater(len(first_page), 0)
        token = pager.continuation_token
        self.assertIsNotNone(token)

        expected_remaining_ids = []
        for page in pager:
            expected_remaining_ids.extend(item['id'] for item in page)

        resume_pager = query_iterable.by_page(token)
        resumed_remaining_ids = []
        for page in resume_pager:
            resumed_remaining_ids.extend(item['id'] for item in page)

        self.assertListEqual(expected_remaining_ids, resumed_remaining_ids)

        baseline_ids = [
            item['id'] for item in created_collection.query_items(query=query, partition_key=['CA'])
        ]
        fetched_ids = [item['id'] for item in first_page] + resumed_remaining_ids
        self.assertListEqual(baseline_ids, fetched_ids)

        created_db.delete_container(created_collection.id)

    def test_partitioned_collection_query_with_tuples_subpartition_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_crud_subpartition.py::TestSubpartitionCrud.test_partitioned_collection_query_with_tuples_subpartition
        created_db = self.databaseForTest

        collection_id = 'test_partitioned_collection_query_with_tuples_MH ' + str(uuid.uuid4())
        created_collection = self._create_container_for_test(
            container_id=collection_id,
            partition_key=PartitionKey(path=['/state', '/city', '/zipcode'], kind=documents.PartitionKind.MultiHash)
        )

        document_definition = {'id': 'document1',
                               'state': 'CA',
                               'city': 'Oxnard',
                               'zipcode': '93033'}

        created_document = created_collection.create_item(body=document_definition)
        self.assertEqual(created_document.get('id'), document_definition.get('id'))

        # Query using tuple instead of list
        document_list = list(
            created_collection.query_items(query='Select * from c', partition_key=('CA', 'Oxnard', '93033')))
        self.assertEqual(1, len(document_list))

        self._delete_container_for_test(created_collection.id)
