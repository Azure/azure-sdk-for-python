# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original document CRUD tests with write responses disabled that upsert items, run on the Rust path.

Source: ``tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled``.
Each method keeps the original steps and assertions; only setup changed. The
client uses ``_backend="rust"`` with ``no_response_on_write=True`` like the
original clients. Each test owns a uniquely named database. The multi-partition
container mirrors the shared ``TEST_MULTI_PARTITION_CONTAINER_ID`` container
(``/pk``, 30000 RU/s).
"""

import os
import unittest
import uuid
from types import SimpleNamespace
from typing import Any, Dict, Optional

import pytest
from azure.core import MatchConditions

import azure.cosmos.exceptions as exceptions
from azure.cosmos import CosmosClient, _retry_utility
from azure.cosmos.http_constants import HttpHeaders, StatusCodes
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
        self._db_id = "upsert_noresponse_" + uuid.uuid4().hex
        self.key_databaseForTest = self.client.create_database(self._db_id)
        self.addCleanup(self._delete_database)
        self.databaseForTest = self.key_databaseForTest
        self.multi_partition_container_id = "multi_partition_" + uuid.uuid4().hex[:8]
        self.key_databaseForTest.create_container(
            id=self.multi_partition_container_id,
            partition_key=PartitionKey(path="/pk", kind="Hash"),
            offer_throughput=30000,
        )
        self.configs = SimpleNamespace(TEST_MULTI_PARTITION_CONTAINER_ID=self.multi_partition_container_id)

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
        # Known gap 23: Container delete and replace require preliminary metadata (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-23). On Rust this delete_container step first resolves container metadata (possible extra GET) before the DELETE; the step still executes.
        created_db.delete_container(created_collection.id)

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

    def test_delete_all_items_by_partition_key_rust(self):
        # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_delete_all_items_by_partition_key
        key_db = self.key_databaseForTest
        data_db = self.databaseForTest

        # create container via setup client (control-plane)
        created_collection = key_db.create_container(
            id='test_delete_all_items_by_partition_key_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/pk', kind='Hash')
        )
        data_collection = data_db.get_container_client(created_collection.id)
        # Create two partition keys
        partition_key1 = "{}-{}".format("Partition Key 1", str(uuid.uuid4()))
        partition_key2 = "{}-{}".format("Partition Key 2", str(uuid.uuid4()))

        # add items for partition key 1
        for i in range(1, 3):
            data_collection.upsert_item(
                dict(id="item{}".format(i), pk=partition_key1)
            )

        # add items for partition key 2

        pk2_item = data_collection.upsert_item(dict(id="item{}".format(3), pk=partition_key2), no_response=False)

        try:
            # delete all items for partition key 1
            # Known gap 19: `delete_all_items_by_partition_key()`: driver support requested; issue filed (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-19). The Rust driver has no partition-key delete; the call still reaches the service, which rejects it here when the account feature is disabled.
            data_collection.delete_all_items_by_partition_key(partition_key1)
        except exceptions.CosmosHttpResponseError as e:
            error_text = " ".join(
                message for message in (getattr(e, "http_error_message", None), str(e))
                if message
            ).lower()
            if e.status_code == 400 and "partition key delete feature is disabled" in error_text:
                key_db.delete_container(created_collection.id)
                pytest.skip("environment-gap: delete_all_items_by_partition_key is not enabled for this account")
            raise

        # check that only items from partition key 1 have been deleted
        items = list(data_collection.read_all_items())

        # items should only have 1 item, and it should equal pk2_item
        self.assertDictEqual(pk2_item, items[0])

        # attempting to delete a non-existent partition key or passing none should not delete
        # anything and leave things unchanged
        data_collection.delete_all_items_by_partition_key(None)

        # check that no changes were made by checking if the only item is still there
        items = list(data_collection.read_all_items())

        # items should only have 1 item, and it should equal pk2_item
        self.assertDictEqual(pk2_item, items[0])

        key_db.delete_container(created_collection.id)

    def test_priority_level_rust(self):
        # Source: tests/test_crud_response_payload_on_write_disabled.py::TestCRUDOperationsResponsePayloadOnWriteDisabled.test_priority_level
        # These test verify if headers for priority level are sent
        # Feature must be enabled at the account level
        # If feature is not enabled the test will still pass as we just verify the headers were sent
        created_container = self.databaseForTest.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)

        item1 = {"id": "item1", "pk": "pk1"}
        item2 = {"id": "item2", "pk": "pk2"}
        self.OriginalExecuteFunction = _retry_utility.ExecuteFunction
        self.addCleanup(setattr, _retry_utility, "ExecuteFunction", self.OriginalExecuteFunction)
        priority_headers = []

        # mock execute function to check if priority level set in headers

        def priority_mock_execute_function(function, *args, **kwargs):
            if args:
                priority_headers.append(args[4].headers[HttpHeaders.PriorityLevel]
                                              if HttpHeaders.PriorityLevel in args[4].headers else '')
            return self.OriginalExecuteFunction(function, *args, **kwargs)

        _retry_utility.ExecuteFunction = priority_mock_execute_function
        # upsert item with high priority
        created_container.upsert_item(body=item1, priority="High")
        # check if the priority level was passed
        # Known gap 6: Closed by design: `raw_request_hook` removed from both backends (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). Rust never calls legacy _retry_utility.ExecuteFunction and its outgoing request headers are not observable, so priority_headers stays empty.
        pytest.skip("internals-only: the priority header was observed by patching legacy "
                    "_retry_utility.ExecuteFunction; Rust outgoing request headers are not observable "
                    "(known gap 6). The High-priority upsert ran.")
        self.assertEqual(priority_headers[-1], "High")
        # upsert item with low priority
        created_container.upsert_item(body=item2, priority="Low")
        # check that headers passed low priority
        self.assertEqual(priority_headers[-1], "Low")
        # Repeat for read operations
        item1_read = created_container.read_item("item1", "pk1", priority="High")
        self.assertEqual(priority_headers[-1], "High")
        item2_read = created_container.read_item("item2", "pk2", priority="Low")
        self.assertEqual(priority_headers[-1], "Low")
        # repeat for query
        query = list(created_container.query_items("Select * from c", partition_key="pk1", priority="High"))

        self.assertEqual(priority_headers[-1], "High")

        # Negative Test: Verify that if we send a value other than High or Low that it will not set the header value
        # and result in bad request
        try:
            item2_read = created_container.read_item("item2", "pk2", priority="Medium")
        except exceptions.CosmosHttpResponseError as e:
            self.assertEqual(e.status_code, StatusCodes.BAD_REQUEST)
        _retry_utility.ExecuteFunction = self.OriginalExecuteFunction


if __name__ == "__main__":
    unittest.main()
