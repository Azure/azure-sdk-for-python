# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original document CRUD tests with write responses disabled, run on the Rust path.

Each test owns a uniquely named database. The multi-partition container mirrors
the shared ``TEST_MULTI_PARTITION_CONTAINER_ID`` container (``/pk``, 30000 RU/s).
"""

import os
import unittest
import uuid
from typing import Any, Dict, Optional

import pytest
from azure.core import MatchConditions

import azure.cosmos.exceptions as exceptions
from azure.cosmos import CosmosClient
from azure.cosmos.http_constants import StatusCodes
from azure.cosmos.partition_key import PartitionKey


class CosmosResponseHeaderEnvelope:
    def __init__(self):
        self.headers: Optional[Dict[str, Any]] = None

    def capture_response_headers(self, headers: Dict[str, Any], response: Dict[str, Any]):
        self.headers = headers


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestCRUDOperationsResponsePayloadOnWriteDisabled(unittest.TestCase):

    def __AssertHTTPFailureWithStatus(self, status_code, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
            self.assertFalse(True, 'function should fail.')
        except exceptions.CosmosHttpResponseError as inst:
            self.assertEqual(inst.status_code, status_code)

    def setUp(self):
        self.client = CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust", no_response_on_write=True,
        )
        self.addCleanup(self.client.close)
        self._db_id = "delete_noresponse_" + uuid.uuid4().hex
        self.key_databaseForTest = self.client.create_database(self._db_id)
        self.addCleanup(self._delete_database)
        self.databaseForTest = self.key_databaseForTest
        self.multi_partition_container_id = "multi_partition_" + uuid.uuid4().hex[:8]
        self.key_databaseForTest.create_container(
            id=self.multi_partition_container_id,
            partition_key=PartitionKey(path="/pk", kind="Hash"),
            offer_throughput=30000,
        )

    def _delete_database(self):
        try:
            self.client.delete_database(self._db_id)
        except exceptions.CosmosResourceNotFoundError:
            pass

    def test_partitioned_collection_document_crud_and_query_rust(self):
        # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_partitioned_collection_document_crud_and_query
        created_db = self.key_databaseForTest

        created_collection = created_db.create_container("crud-query-container", partition_key=PartitionKey("/pk"))

        document_definition = {'id': 'document',
                               'key': 'value',
                               'pk': 'pk'}

        headerEnvelope=CosmosResponseHeaderEnvelope()
        no_response = created_collection.create_item(
            body=document_definition,
            response_hook=headerEnvelope.capture_response_headers
        )

        self.assertDictEqual(no_response, {})

        # read document
        read_document = created_collection.read_item(
            item=document_definition.get('id'),
            partition_key=document_definition.get('pk')
        )

        self.assertEqual(headerEnvelope.headers['etag'], read_document['_etag'])
        self.assertEqual(read_document.get('id'), document_definition.get('id'))
        self.assertEqual(read_document.get('key'), document_definition.get('key'))

        # Read document feed doesn't require partitionKey as it's always a cross partition query
        documentlist = list(created_collection.read_all_items())
        self.assertEqual(1, len(documentlist))

        # replace document
        document_definition['key'] = 'new value'

        no_Response = created_collection.replace_item(
            item=read_document,
            body=document_definition,
            response_hook=headerEnvelope.capture_response_headers
        )
        self.assertDictEqual(no_response, {})

        # read document
        replaced_document = created_collection.read_item(
            item=document_definition.get('id'),
            partition_key=document_definition.get('pk')
        )

        self.assertEqual(headerEnvelope.headers['etag'], replaced_document.get('_etag'))
        self.assertEqual(replaced_document.get('key'), document_definition.get('key'))

        # upsert document(create scenario)
        document_definition['id'] = 'document2'
        document_definition['key'] = 'value2'

        no_Response = created_collection.upsert_item(body=document_definition, response_hook=headerEnvelope.capture_response_headers)
        self.assertDictEqual(no_response, {})

        upserted_document = created_collection.read_item(
            item=document_definition.get('id'),
            partition_key=document_definition.get('pk')
        )

        self.assertEqual(headerEnvelope.headers['etag'], upserted_document.get('_etag'))
        self.assertEqual(upserted_document.get('id'), document_definition.get('id'))
        self.assertEqual(upserted_document.get('key'), document_definition.get('key'))

        documentlist = list(created_collection.read_all_items())
        self.assertEqual(2, len(documentlist))

        # delete document
        created_collection.delete_item(item=upserted_document, partition_key=upserted_document.get('pk'))

        # query document on the partition key specified in the predicate will pass even without setting enableCrossPartitionQuery or passing in the partitionKey value
        documentlist = list(created_collection.query_items(
            {
                'query': 'SELECT * FROM root r WHERE r.id=\'' + replaced_document.get('id') + '\''  # nosec
            }, enable_cross_partition_query=True))
        self.assertEqual(1, len(documentlist))

        # query document on any property other than partitionKey will fail without setting enableCrossPartitionQuery or passing in the partitionKey value
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
            partition_key=replaced_document.get('pk')
        ))

        self.assertEqual(1, len(documentlist))
        created_db.delete_container(created_collection.id)

    def test_document_crud_response_payload_enabled_via_override_rust(self):
        # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_document_crud_response_payload_enabled_via_override
        # create database
        created_db = self.key_databaseForTest
        # create collection
        created_collection = self.databaseForTest.get_container_client(self.multi_partition_container_id)
        # read documents
        documents = list(created_collection.read_all_items())
        # create a document
        before_create_documents_count = len(documents)

        # create a document with auto ID generation
        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk'}

        created_document = created_collection.create_item(body=document_definition, enable_automatic_id_generation=True, no_response=False)
        self.assertEqual(created_document.get('name'),
                         document_definition['name'])

        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk',
                               'id': str(uuid.uuid4())}

        created_document = created_collection.create_item(body=document_definition, no_response=False)
        self.assertEqual(created_document.get('name'),
                         document_definition['name'])
        self.assertEqual(created_document.get('id'),
                         document_definition['id'])

        # duplicated documents are not allowed when 'id' is provided.
        duplicated_definition_with_id = document_definition.copy()
        self.__AssertHTTPFailureWithStatus(StatusCodes.CONFLICT,
                                           created_collection.create_item,
                                           duplicated_definition_with_id)
        # read documents after creation
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 2,
            'create should increase the number of documents')
        # query documents
        documents = list(created_collection.query_items(
            {
                'query': 'SELECT * FROM root r WHERE r.name=@name',
                'parameters': [
                    {'name': '@name', 'value': document_definition['name']}
                ]
            }, enable_cross_partition_query=True
        ))
        self.assertTrue(documents)
        documents = list(created_collection.query_items(
            {
                'query': 'SELECT * FROM root r WHERE r.name=@name',
                'parameters': [
                    {'name': '@name', 'value': document_definition['name']}
                ],
            }, enable_cross_partition_query=True,
            enable_scan_in_query=True
        ))
        self.assertTrue(documents)
        # replace document.
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'
        old_etag = created_document['_etag']
        replaced_document = created_collection.replace_item(
            item=created_document['id'],
            body=created_document,
            no_response=False
        )
        self.assertEqual(replaced_document['name'],
                         'replaced document',
                         'document id property should change')
        self.assertEqual(replaced_document['spam'],
                         'not eggs',
                         'property should have changed')
        self.assertEqual(created_document['id'],
                         replaced_document['id'],
                         'document id should stay the same')

        # replace document based on condition
        replaced_document['name'] = 'replaced document based on condition'
        replaced_document['spam'] = 'new spam field'

        # should fail for stale etag
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.PRECONDITION_FAILED,
            created_collection.replace_item,
            replaced_document['id'],
            replaced_document,
            if_match=old_etag,
        )

        # should fail if only etag specified
        with self.assertRaises(ValueError):
            created_collection.replace_item(
                etag=replaced_document['_etag'],
                item=replaced_document['id'],
                body=replaced_document,
                no_response=False
            )

        # should fail if only match condition specified
        with self.assertRaises(ValueError):
            created_collection.replace_item(
                match_condition=MatchConditions.IfNotModified,
                item=replaced_document['id'],
                body=replaced_document,
                no_response=False
            )
        with self.assertRaises(ValueError):
            created_collection.replace_item(
                match_condition=MatchConditions.IfModified,
                item=replaced_document['id'],
                body=replaced_document,
                no_response=False
            )

        # should fail if invalid match condition specified
        with self.assertRaises(TypeError):
            created_collection.replace_item(
                match_condition=replaced_document['_etag'],
                item=replaced_document['id'],
                body=replaced_document,
                no_response=False
            )

        # should pass for most recent etag
        replaced_document_conditional = created_collection.replace_item(
            match_condition=MatchConditions.IfNotModified,
            etag=replaced_document['_etag'],
            item=replaced_document['id'],
            body=replaced_document,
            no_response=False
        )
        self.assertEqual(replaced_document_conditional['name'],
                         'replaced document based on condition',
                         'document id property should change')
        self.assertEqual(replaced_document_conditional['spam'],
                         'new spam field',
                         'property should have changed')
        self.assertEqual(replaced_document_conditional['id'],
                         replaced_document['id'],
                         'document id should stay the same')
        # read document
        one_document_from_read = created_collection.read_item(
            item=replaced_document['id'],
            partition_key=replaced_document['pk']
        )
        self.assertEqual(replaced_document['id'],
                         one_document_from_read['id'])
        # delete document
        created_collection.delete_item(
            item=replaced_document,
            partition_key=replaced_document['pk']
        )
        # read documents after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           created_collection.read_item,
                                           replaced_document['id'],
                                           replaced_document['id'])

    def test_document_crud_rust(self):
        # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_document_crud
        # create database
        created_db = self.key_databaseForTest
        # create collection
        created_collection = self.databaseForTest.get_container_client(self.multi_partition_container_id)
        # read documents
        documents = list(created_collection.read_all_items())
        # create a document
        before_create_documents_count = len(documents)

        id = str(uuid.uuid4())

        # create a document with auto ID generation
        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk',
                               'id': id}

        headerEnvelope = CosmosResponseHeaderEnvelope()
        self.assertIsNone(headerEnvelope.headers)
        created_document = created_collection.create_item(body=document_definition, enable_automatic_id_generation=False, response_hook=headerEnvelope.capture_response_headers)
        self.assertDictEqual(created_document, {})
        self.assertIsNotNone(headerEnvelope.headers)

        expectedEtag = headerEnvelope.headers['etag']
        read_document = created_collection.read_item(item=id, partition_key=document_definition['pk'])

        self.assertIsNotNone(read_document)
        self.assertEqual(id, read_document['id'])
        self.assertEqual(expectedEtag, read_document['_etag'])
        self.assertEqual(read_document['name'], document_definition['name'])

        # duplicated documents are not allowed when 'id' is provided.
        duplicated_definition_with_id = document_definition.copy()
        self.__AssertHTTPFailureWithStatus(StatusCodes.CONFLICT,
                                           created_collection.create_item,
                                           duplicated_definition_with_id)
        # read documents after creation
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 1,
            'create should increase the number of documents')
        # query documents
        documents = list(created_collection.query_items(
            {
                'query': 'SELECT * FROM root r WHERE r.name=@name',
                'parameters': [
                    {'name': '@name', 'value': document_definition['name']}
                ]
            }, enable_cross_partition_query=True
        ))
        self.assertTrue(documents)
        documents = list(created_collection.query_items(
            {
                'query': 'SELECT * FROM root r WHERE r.name=@name',
                'parameters': [
                    {'name': '@name', 'value': document_definition['name']}
                ],
            }, enable_cross_partition_query=True,
            enable_scan_in_query=True
        ))
        self.assertTrue(documents)
        # replace document.
        to_be_replaced_document = read_document.copy()
        to_be_replaced_document['name'] = 'replaced document'
        to_be_replaced_document['spam'] = 'not eggs'
        old_etag = expectedEtag
        replaced_document = created_collection.replace_item(
            item=to_be_replaced_document['id'],
            body=to_be_replaced_document,
            response_hook=headerEnvelope.capture_response_headers
        )

        self.assertDictEqual(replaced_document, {})
        read_document = created_collection.read_item(item=id, partition_key=document_definition['pk'])

        self.assertIsNotNone(read_document)
        self.assertEqual(id, read_document['id'])
        self.assertNotEqual(expectedEtag, headerEnvelope.headers['etag'])
        self.assertNotEqual(expectedEtag, read_document['_etag'])
        self.assertEqual(headerEnvelope.headers['etag'], read_document['_etag'])
        self.assertEqual(read_document['name'], to_be_replaced_document['name'])
        self.assertEqual(read_document['spam'], to_be_replaced_document['spam'])

        self.assertEqual(read_document['name'], 'replaced document')
        self.assertEqual(read_document['spam'], 'not eggs')
        self.assertEqual(id,  read_document['id'])

        # replace document based on condition
        to_be_replaced_document = read_document.copy()
        to_be_replaced_document['name'] = 'replaced document based on condition'
        to_be_replaced_document['spam'] = 'new spam field'

        # should fail for stale etag
        self.__AssertHTTPFailureWithStatus(
            StatusCodes.PRECONDITION_FAILED,
            created_collection.replace_item,
            to_be_replaced_document['id'],
            to_be_replaced_document,
            if_match=old_etag,
        )

        # should fail if only etag specified
        with self.assertRaises(ValueError):
            created_collection.replace_item(
                etag=to_be_replaced_document['_etag'],
                item=to_be_replaced_document['id'],
                body=to_be_replaced_document
            )

        # should fail if only match condition specified
        with self.assertRaises(ValueError):
            created_collection.replace_item(
                match_condition=MatchConditions.IfNotModified,
                item=to_be_replaced_document['id'],
                body=to_be_replaced_document
            )
        with self.assertRaises(ValueError):
            created_collection.replace_item(
                match_condition=MatchConditions.IfModified,
                item=to_be_replaced_document['id'],
                body=to_be_replaced_document
            )

        # should fail if invalid match condition specified
        with self.assertRaises(TypeError):
            created_collection.replace_item(
                match_condition=to_be_replaced_document['_etag'],
                item=to_be_replaced_document['id'],
                body=to_be_replaced_document
            )

        # should pass for most recent etag
        replaced_document_conditional = created_collection.replace_item(
            match_condition=MatchConditions.IfNotModified,
            etag=to_be_replaced_document['_etag'],
            item=to_be_replaced_document['id'],
            body=to_be_replaced_document,
            no_response=False
        )
        self.assertEqual(replaced_document_conditional['name'],
                         'replaced document based on condition',
                         'document id property should change')
        self.assertEqual(replaced_document_conditional['spam'],
                         'new spam field',
                         'property should have changed')
        self.assertEqual(replaced_document_conditional['id'],
                         to_be_replaced_document['id'],
                         'document id should stay the same')
        # read document
        one_document_from_read = created_collection.read_item(
            item=to_be_replaced_document['id'],
            partition_key=to_be_replaced_document['pk']
        )
        self.assertEqual(to_be_replaced_document['id'],
                         one_document_from_read['id'])
        # delete document
        created_collection.delete_item(
            item=to_be_replaced_document,
            partition_key=to_be_replaced_document['pk']
        )
        # read documents after deletion
        self.__AssertHTTPFailureWithStatus(StatusCodes.NOT_FOUND,
                                           created_collection.read_item,
                                           to_be_replaced_document['id'],
                                           to_be_replaced_document['id'])

    def test_document_upsert_rust(self):
        # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_document_upsert
        # create database
        created_db = self.key_databaseForTest

        # create collection
        created_collection = self.databaseForTest.get_container_client(self.multi_partition_container_id)

        # read documents and check count
        documents = list(created_collection.read_all_items())
        before_create_documents_count = len(documents)

        # create document definition
        id = 'doc'
        document_definition = {'id': id,
                               'name': 'sample document',
                               'spam': 'eggs',
                               'pk': 'pk',
                               'key': 'value'}

        # create document using Upsert API
        headerEnvelope = CosmosResponseHeaderEnvelope()
        none_response = created_collection.upsert_item(body=document_definition, response_hook=headerEnvelope.capture_response_headers)
        self.assertDictEqual(none_response, {})

        created_document = created_collection.read_item(item='doc', partition_key=document_definition['pk'])
        self.assertEqual(headerEnvelope.headers['etag'], created_document['_etag'])

        # verify id property
        self.assertEqual(created_document['id'],
                         document_definition['id'])

        # test error for non-string id
        with self.assertRaises(TypeError):
            document_definition['id'] = 7
            created_collection.upsert_item(body=document_definition)

        # read documents after creation and verify updated count
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 1,
            'create should increase the number of documents')

        # update document
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'

        # should replace document since it already exists
        none_response = created_collection.upsert_item(body=created_document, response_hook=headerEnvelope.capture_response_headers)
        self.assertDictEqual(none_response, {})

        upserted_document = created_collection.read_item(item=id, partition_key=document_definition['pk'])
        self.assertEqual(headerEnvelope.headers['etag'], upserted_document['_etag'])

        # verify the changed properties
        self.assertEqual(upserted_document['name'],
                         created_document['name'],
                         'document name property should change')
        self.assertEqual(upserted_document['spam'],
                         created_document['spam'],
                         'property should have changed')

        # verify id property
        self.assertEqual(upserted_document['id'],
                         created_document['id'],
                         'document id should stay the same')

        # read documents after upsert and verify count doesn't increases again
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 1,
            'number of documents should remain same')

        created_document['id'] = 'new id'

        # Upsert should create new document since the id is different
        no_response = created_collection.upsert_item(body=created_document, response_hook=headerEnvelope.capture_response_headers)
        self.assertDictEqual(none_response, {})

        new_document = created_collection.read_item(item='new id', partition_key=document_definition['pk'])
        self.assertEqual(headerEnvelope.headers['etag'], new_document['_etag'])

        # Test modified access conditions
        created_document['spam'] = 'more eggs'
        created_collection.upsert_item(body=created_document)
        with self.assertRaises(exceptions.CosmosHttpResponseError):
            created_collection.upsert_item(
                body=created_document,
                match_condition=MatchConditions.IfNotModified,
                etag=new_document['_etag'])

        # verify id property
        self.assertEqual(created_document['id'],
                         new_document['id'],
                         'document id should be same')

        # read documents after upsert and verify count increases
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count + 2,
            'upsert should increase the number of documents')

        # delete documents
        created_collection.delete_item(item=upserted_document, partition_key=upserted_document['pk'])
        created_collection.delete_item(item=new_document, partition_key=new_document['pk'])

        # read documents after delete and verify count is same as original
        documents = list(created_collection.read_all_items())
        self.assertEqual(
            len(documents),
            before_create_documents_count,
            'number of documents should remain same')
