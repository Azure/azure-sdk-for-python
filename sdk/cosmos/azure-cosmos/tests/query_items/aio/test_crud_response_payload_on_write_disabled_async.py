# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original async document CRUD tests with write responses disabled that call ``query_items``, run on the Rust path.

Source: ``tests/test_crud_response_payload_on_write_disabled_async.py::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled``.
Each method keeps the original steps, query inputs and assertions; only setup changed. The
client uses ``_backend="rust"`` with ``no_response_on_write=True`` like the
original clients. Each test owns a uniquely named database. The multi-partition
container mirrors the shared ``TEST_MULTI_PARTITION_CONTAINER_ID`` container
(``/pk``, 30000 RU/s). Known Rust gaps are skipped at the failing step.
"""

import unittest
import uuid
from types import SimpleNamespace
from typing import Any, Dict, Optional

import pytest
from azure.core import MatchConditions

import azure.cosmos.exceptions as exceptions
from azure.cosmos.http_constants import StatusCodes
from common.priority_contract import assert_priority_contract_async
from azure.cosmos.partition_key import PartitionKey
from config.clients import create_data_client_async, create_setup_client_async


class CosmosResponseHeaderEnvelope:
    def __init__(self):
        self.headers: Optional[Dict[str, Any]] = None

    def capture_response_headers(self, headers: Dict[str, Any], response: Dict[str, Any]):
        self.headers = headers


@pytest.mark.cosmosLong
@pytest.mark.cosmosAADLong
class TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled(unittest.IsolatedAsyncioTestCase):

    async def __assert_http_failure_with_status(self, status_code, func, *args, **kwargs):
        try:
            await func(*args, **kwargs)
            self.fail('function should fail.')
        except exceptions.CosmosHttpResponseError as inst:
            assert inst.status_code == status_code

    async def asyncSetUp(self):
        # Same split as the original: both clients keep no_response_on_write=True;
        # the key client provisions, the data client (AAD in the cosmosAAD* lanes)
        # backs database_for_test.
        self.key_client = create_setup_client_async(no_response_on_write=True)
        await self.key_client.__aenter__()
        self.addAsyncCleanup(self.key_client.close)
        self.client = create_data_client_async(_backend="rust", no_response_on_write=True)
        await self.client.__aenter__()
        self.addAsyncCleanup(self.client.close)
        self._db_id = "qi_noresponse_async_" + uuid.uuid4().hex
        self.key_database_for_test = await self.key_client.create_database(self._db_id)
        self.addAsyncCleanup(self._delete_database)
        self.database_for_test = self.client.get_database_client(self._db_id)
        self.multi_partition_container_id = "multi_partition_" + uuid.uuid4().hex[:8]
        await self.key_database_for_test.create_container(
            id=self.multi_partition_container_id,
            partition_key=PartitionKey(path="/pk", kind="Hash"),
            offer_throughput=30000,
        )
        self.configs = SimpleNamespace(TEST_MULTI_PARTITION_CONTAINER_ID=self.multi_partition_container_id)

    async def _delete_database(self):
        try:
            await self.key_client.delete_database(self._db_id)
        except exceptions.CosmosResourceNotFoundError:
            pass

    async def test_partitioned_collection_document_crud_and_query_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_crud_response_payload_on_write_disabled_async.py::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_partitioned_collection_document_crud_and_query_async
        created_collection = await self.key_database_for_test.create_container(str(uuid.uuid4()), PartitionKey(path="/id"))

        document_definition = {'id': 'document',
                               'key': 'value'}

        created_document = await created_collection.create_item(body=document_definition)
        self.assertDictEqual(created_document, {})
        created_document = await created_collection.upsert_item(body=document_definition)
        self.assertDictEqual(created_document, {})
        created_document = await created_collection.upsert_item(body=document_definition, no_response=True)
        self.assertDictEqual(created_document, {})
        created_document = await created_collection.upsert_item(body=document_definition, no_response=False)
        assert created_document is not {}

        assert created_document.get('id') == document_definition.get('id')
        assert created_document.get('key') == document_definition.get('key')

        # read document
        read_document = await created_collection.read_item(
            item=created_document.get('id'),
            partition_key=created_document.get('id')
        )

        assert read_document.get('id') == created_document.get('id')
        assert read_document.get('key') == created_document.get('key')

        # Read document feed doesn't require partitionKey as it's always a cross partition query
        document_list = [document async for document in created_collection.read_all_items()]
        assert 1 == len(document_list)

        # replace document
        document_definition['key'] = 'new value'

        replaced_document = await created_collection.replace_item(
            item=read_document,
            body=document_definition
        )
        self.assertDictEqual(replaced_document, {})
        replaced_document = await created_collection.replace_item(
            item=read_document,
            body=document_definition,
            no_response=True
        )
        self.assertDictEqual(replaced_document, {})
        replaced_document = await created_collection.replace_item(
            item=read_document,
            body=document_definition,
            no_response=False
        )
        assert replaced_document is not None

        assert replaced_document.get('key') == document_definition.get('key')

        # upsert document(create scenario)
        document_definition['id'] = 'document2'
        document_definition['key'] = 'value2'

        upserted_document = await created_collection.upsert_item(body=document_definition, no_response=False)

        assert upserted_document.get('id') == document_definition.get('id')
        assert upserted_document.get('key') == document_definition.get('key')

        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == 2

        # delete document
        await created_collection.delete_item(item=upserted_document, partition_key=upserted_document.get('id'))

        # query document on the partition key specified in the predicate will pass even without setting enableCrossPartitionQuery or passing in the partitionKey value
        document_list = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.id=\'' + replaced_document.get('id') + '\''  # nosec
        )]
        assert len(document_list) == 1

        # cross partition query
        document_list = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'')]

        assert len(document_list) == 1

        # query document by providing the partitionKey value
        document_list = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.key=\'' + replaced_document.get('key') + '\'',  # nosec
            partition_key=replaced_document.get('id')
        )]

        assert len(document_list) == 1
        await self.key_database_for_test.delete_container(created_collection.id)

    async def test_document_crud_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_crud_response_payload_on_write_disabled_async.py::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_document_crud_async

        # create collection
        created_collection = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        # read documents
        document_list = [document async for document in created_collection.read_all_items()]
        # create a document
        before_create_documents_count = len(document_list)

        # create a document with auto ID generation
        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk'}

        created_document = await created_collection.create_item(body=document_definition,
                                                                enable_automatic_id_generation=True,
                                                                no_response=False)
        assert created_document.get('name') == document_definition['name']

        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk',
                               'id': str(uuid.uuid4())}

        created_document = await created_collection.create_item(body=document_definition)
        self.assertDictEqual(created_document, {})

        document_definition["id"] = str(uuid.uuid4())
        created_document = await created_collection.create_item(body=document_definition, no_response=True)
        self.assertDictEqual(created_document, {})

        document_definition["id"] = str(uuid.uuid4())
        created_document = await created_collection.create_item(body=document_definition, no_response=False)
        assert created_document is not {}

        assert created_document.get('name') == document_definition['name']
        assert created_document.get('id') == document_definition['id']

        # duplicated documents are not allowed when 'id' is provided.
        duplicated_definition_with_id = document_definition.copy()
        await self.__assert_http_failure_with_status(StatusCodes.CONFLICT,
                                                     created_collection.create_item,
                                                     duplicated_definition_with_id)
        # read documents after creation
        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == before_create_documents_count + 4
        # query documents
        document_list = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.name=@name',
            parameters=[{'name': '@name', 'value': document_definition['name']}]
        )]
        assert document_list is not None
        document_list = [document async for document in created_collection.query_items(
            query='SELECT * FROM root r WHERE r.name=@name',
            parameters=[
                {'name': '@name', 'value': document_definition['name']}
            ],
            enable_scan_in_query=True
        )]
        assert document_list is not None

        # replace document.
        created_document['name'] = 'replaced document'
        created_document['spam'] = 'not eggs'
        old_etag = created_document['_etag']
        replaced_document = await created_collection.replace_item(
            item=created_document['id'],
            body=created_document
        )
        self.assertDictEqual(replaced_document, {})

        replaced_document = await created_collection.replace_item(
            item=created_document['id'],
            body=created_document,
            no_response=True
        )
        self.assertDictEqual(replaced_document, {})

        replaced_document = await created_collection.replace_item(
            item=created_document['id'],
            body=created_document,
            no_response=False
        )
        assert replaced_document is not None

        assert replaced_document['name'] == 'replaced document'
        assert replaced_document['spam'] == 'not eggs'
        assert created_document['id'] == replaced_document['id']

        # replace document based on condition
        replaced_document['name'] = 'replaced document based on condition'
        replaced_document['spam'] = 'new spam field'

        # should fail for stale etag
        await self.__assert_http_failure_with_status(
            StatusCodes.PRECONDITION_FAILED,
            created_collection.replace_item,
            replaced_document['id'],
            replaced_document,
            if_match=old_etag,
        )

        # should fail if only etag specified
        try:
            await created_collection.replace_item(
                etag=replaced_document['_etag'],
                item=replaced_document['id'],
                body=replaced_document)
            self.fail("should fail if only etag specified")
        except ValueError:
            pass

        # should fail if only match condition specified
        try:
            await created_collection.replace_item(
                match_condition=MatchConditions.IfNotModified,
                item=replaced_document['id'],
                body=replaced_document)
            self.fail("should fail if only match condition specified")
        except ValueError:
            pass

        try:
            await created_collection.replace_item(
                match_condition=MatchConditions.IfModified,
                item=replaced_document['id'],
                body=replaced_document)
            self.fail("should fail if only match condition specified")
        except ValueError:
            pass

        # should fail if invalid match condition specified
        try:
            await created_collection.replace_item(
                match_condition=replaced_document['_etag'],
                item=replaced_document['id'],
                body=replaced_document)
            self.fail("should fail if invalid match condition specified")
        except TypeError:
            pass

        # should pass for most recent etag
        headerEnvelope=CosmosResponseHeaderEnvelope()
        replaced_document_conditional = await created_collection.replace_item(
            match_condition=MatchConditions.IfNotModified,
            etag=replaced_document['_etag'],
            item=replaced_document['id'],
            body=replaced_document,
            response_hook=headerEnvelope.capture_response_headers
        )
        self.assertDictEqual(replaced_document_conditional, {})
        replaced_document_conditional = await created_collection.read_item(
            item=replaced_document['id'],
            partition_key=replaced_document['pk'])

        assert replaced_document_conditional is not None
        assert replaced_document_conditional['_etag'] == headerEnvelope.headers["etag"]
        assert replaced_document_conditional['name'] == 'replaced document based on condition'
        assert replaced_document_conditional['spam'] == 'new spam field'
        assert replaced_document_conditional['id'] == replaced_document['id']

        # read document
        one_document_from_read = await created_collection.read_item(
            item=replaced_document['id'],
            partition_key=replaced_document['pk']
        )
        assert replaced_document['id'] == one_document_from_read['id']
        # delete document
        await created_collection.delete_item(
            item=replaced_document,
            partition_key=replaced_document['pk']
        )
        # read documents after deletion
        await self.__assert_http_failure_with_status(StatusCodes.NOT_FOUND,
                                                     created_collection.read_item,
                                                     replaced_document['id'],
                                                     replaced_document['id'])

    async def test_geospatial_index_async_rust(self):
        # pylint: disable-next=line-too-long
        # Source: tests/test_crud_response_payload_on_write_disabled_async.py::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_geospatial_index_async
        db = self.key_database_for_test
        # partial policy specified
        collection = await db.create_container(
            id='collection with spatial index ' + str(uuid.uuid4()),
            indexing_policy={
                'includedPaths': [
                    {
                        'path': '/"Location"/?',
                        'indexes': [
                            {
                                'kind': 'Spatial',
                                'dataType': 'Point'
                            }
                        ]
                    },
                    {
                        'path': '/'
                    }
                ]
            },
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        await collection.create_item(
            body={
                'id': 'loc1',
                'Location': {
                    'type': 'Point',
                    'coordinates': [20.0, 20.0]
                }
            }
        )
        await collection.create_item(
            body={
                'id': 'loc2',
                'Location': {
                    'type': 'Point',
                    'coordinates': [100.0, 100.0]
                }
            }
        )
        results = [result async for result in collection.query_items(
            query="SELECT * FROM root WHERE (ST_DISTANCE(root.Location, {type: 'Point', coordinates: [20.1, 20]}) < 20000)")]
        assert len(results) == 1
        assert 'loc1' == results[0]['id']

    async def test_priority_level_async_rust(self):
        # Source: tests/test_crud_response_payload_on_write_disabled_async.py::TestCRUDOperationsAsyncResponsePayloadOnWriteDisabled.test_priority_level_async
        container = self.database_for_test.get_container_client(
            self.configs.TEST_MULTI_PARTITION_CONTAINER_ID
        )
        await assert_priority_contract_async(container)
