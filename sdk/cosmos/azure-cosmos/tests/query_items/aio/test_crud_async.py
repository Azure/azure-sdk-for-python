# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Original async CRUD tests that call ``query_items``, re-run on the Rust path.

Source: ``tests/test_crud_async.py::TestCRUDOperationsAsync``. Each method
keeps the original steps, query inputs and assertions; only setup changed.
Every client uses ``_backend="rust"`` and each test owns a uniquely named
database with the ``/pk`` multi-partition container the original setup
provided, deleted afterwards. Known Rust gaps are skipped at the failing step.
"""

import asyncio
import os
import unittest
import uuid
from types import SimpleNamespace

import pytest
from azure.core import MatchConditions
from azure.core.pipeline.transport import AioHttpTransport

import azure.cosmos.exceptions as exceptions
from azure.cosmos.aio import CosmosClient, _retry_utility_async
from azure.cosmos.http_constants import HttpHeaders, StatusCodes
from azure.cosmos.partition_key import PartitionKey
from _client_transport import create_client_with_transport


@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosLong
@pytest.mark.cosmosAADCircuitBreaker
class TestCRUDOperationsAsync(unittest.IsolatedAsyncioTestCase):
    """Python CRUD Tests.
    """

    async def __assert_http_failure_with_status(self, status_code, func, *args, **kwargs):
        """Assert HTTP failure with status.

        :Parameters:
            - `status_code`: int
            - `func`: function
        """
        try:
            await func(*args, **kwargs)
            self.fail('function should fail.')
        except exceptions.CosmosHttpResponseError as inst:
            assert inst.status_code == status_code

    async def asyncSetUp(self):
        self.host = os.environ["ACCOUNT_HOST"]
        self.masterKey = os.environ["ACCOUNT_KEY"]
        self.client = CosmosClient(self.host, self.masterKey, _backend="rust")
        self.addAsyncCleanup(self.client.close)
        await self.client.__aenter__()
        self._db_id = "qi_crud_async_" + uuid.uuid4().hex
        self.database_for_test = await self.client.create_database(self._db_id)
        self.addAsyncCleanup(self.client.delete_database, self._db_id)
        self.key_database_for_test = self.database_for_test
        self.configs = SimpleNamespace(
            TEST_DATABASE_ID=self._db_id,
            TEST_MULTI_PARTITION_CONTAINER_ID="multi_partition_" + uuid.uuid4().hex[:8])
        await self.database_for_test.create_container(
            id=self.configs.TEST_MULTI_PARTITION_CONTAINER_ID, partition_key=PartitionKey(path="/pk"))

    async def _create_container_for_test(self, container_id, partition_key, **kwargs):
        """Create container via key-auth setup client (control-plane), return data-plane proxy."""
        await self.key_database_for_test.create_container(id=container_id, partition_key=partition_key, **kwargs)
        return self.database_for_test.get_container_client(container_id)

    async def _delete_container_for_test(self, container_id_or_container):
        """Delete container via key-auth setup client (control-plane)."""
        cid = container_id_or_container if isinstance(container_id_or_container, str) else container_id_or_container.id
        await self.key_database_for_test.delete_container(cid)

    async def test_document_crud_async_rust(self):
        # Source: tests/test_crud_async.py::TestCRUDOperationsAsync.test_document_crud_async

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
                                                                enable_automatic_id_generation=True)
        assert created_document.get('name') == document_definition['name']

        document_definition = {'name': 'sample document',
                               'spam': 'eggs',
                               'key': 'value',
                               'pk': 'pk',
                               'id': str(uuid.uuid4())}

        created_document = await created_collection.create_item(body=document_definition)
        assert created_document.get('name') == document_definition['name']
        assert created_document.get('id') == document_definition['id']

        # duplicated documents are not allowed when 'id' is provided.
        duplicated_definition_with_id = document_definition.copy()
        await self.__assert_http_failure_with_status(StatusCodes.CONFLICT,
                                                     created_collection.create_item,
                                                     duplicated_definition_with_id)
        # read documents after creation
        document_list = [document async for document in created_collection.read_all_items()]
        assert len(document_list) == before_create_documents_count + 2
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
        replaced_document_conditional = await created_collection.replace_item(
            match_condition=MatchConditions.IfNotModified,
            etag=replaced_document['_etag'],
            item=replaced_document['id'],
            body=replaced_document
        )
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
        # Source: tests/test_crud_async.py::TestCRUDOperationsAsync.test_geospatial_index_async
        db = self.database_for_test
        # partial policy specified
        collection = await self._create_container_for_test(
            container_id='collection with spatial index ' + str(uuid.uuid4()),
            partition_key=PartitionKey(path='/id', kind='Hash'),
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
            }
        )
        try:
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
        finally:
            await self._delete_container_for_test(collection.id)

    async def test_timeout_for_paged_request_async_rust(self):
        # Source: tests/test_crud_async.py::TestCRUDOperationsAsync.test_timeout_for_paged_request_async
        """Test that timeout applies to each individual page request, not cumulatively"""

        # Create container and add items
        created_container = await self._create_container_for_test(
            container_id='paged_timeout_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk")
        )

        # Create enough items to ensure multiple pages
        for i in range(100):
            await created_container.create_item({'id': f'item_{i}', 'pk': i % 10, 'data': 'x' * 1000})

        # Create a transport that delays each request
        class DelayedTransport(AioHttpTransport):
            def __init__(self, delay_seconds=1):
                self.delay_seconds = delay_seconds
                super().__init__()

            async def send(self, request, **kwargs):
                await asyncio.sleep(self.delay_seconds)
                return await super().send(request, **kwargs)

        # Test with delayed transport - reduced delay to 1 second for stability
        delayed_transport = DelayedTransport(delay_seconds=1)
        async with create_client_with_transport(CosmosClient,
                self.host, self.masterKey, transport=delayed_transport, _backend="rust"
        ) as client_with_delay:
            container_with_delay = client_with_delay.get_database_client(
                self.database_for_test.id
            ).get_container_client(created_container.id)

            # Test 1: Timeout should apply per page
            item_pages = container_with_delay.query_items(
                query="SELECT * FROM c",
                #enable_cross_partition_query=True,
                max_item_count=10,  # Small page size
                timeout=3  # 3s timeout > 1s delay, should succeed
            ).by_page()

            # First page should succeed with 3s timeout (1s delay < 3s timeout)
            first_page = [item async for item in await item_pages.__anext__()]
            self.assertGreater(len(first_page), 0)

            # Second page should also succeed (timeout resets per page)
            second_page = [item async for item in await item_pages.__anext__()]
            self.assertGreater(len(second_page), 0)

            # Test 2: Timeout too short should fail
            # Known gap 5: Closed: runtime and operation timeout scopes (sub-second budgets are rejected).
            # Known gap 10: the Rust client also ignores the injected DelayedTransport, so no request is delayed.
            pytest.skip("accepted-vnext-change: Rust rejects the sub-second per-call timeout=0.5 with ValueError "
                        "(known gap 5, docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-5) and ignores the injected "
                        "custom transport (known gap 10, docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-10). "
                        "The per-page 3 s timeout steps ran.")
            item_pages_short_timeout = container_with_delay.query_items(
                query="SELECT * FROM c",
                #enable_cross_partition_query=True,
                max_item_count=10,
                timeout=0.5  # 0.5s timeout < 1s delay, should fail
            ).by_page()

            with self.assertRaises(exceptions.CosmosClientTimeoutError):
                first_page = [item async for item in await item_pages_short_timeout.__anext__()]

        # Cleanup
        await self.key_database_for_test.delete_container(created_container.id)

    async def test_priority_level_async_rust(self):
        # Source: tests/test_crud_async.py::TestCRUDOperationsAsync.test_priority_level_async
        # These test verify if headers for priority level are sent
        # Feature must be enabled at the account level
        # If feature is not enabled the test will still pass as we just verify the headers were sent

        created_container = self.database_for_test.get_container_client(self.configs.TEST_MULTI_PARTITION_CONTAINER_ID)
        item1 = {"id": "item1", "pk": "pk1"}
        item2 = {"id": "item2", "pk": "pk2"}
        self.OriginalExecuteFunction = _retry_utility_async.ExecuteFunctionAsync
        self.addCleanup(setattr, _retry_utility_async, "ExecuteFunctionAsync", self.OriginalExecuteFunction)
        priority_headers = []

        # mock execute function to check if priority level set in headers

        async def priority_mock_execute_function(function, *args, **kwargs):
            if args:
                priority_headers.append(args[4].headers[HttpHeaders.PriorityLevel]
                                              if HttpHeaders.PriorityLevel in args[4].headers else '')
            return await self.OriginalExecuteFunction(function, *args, **kwargs)

        _retry_utility_async.ExecuteFunctionAsync = priority_mock_execute_function
        # upsert item with high priority
        await created_container.upsert_item(body=item1, priority="High")
        # check if the priority level was passed
        # Known gap 6: Closed by design: `raw_request_hook` removed from both backends. Rust never calls legacy
        # _retry_utility_async.ExecuteFunctionAsync and its outgoing request headers are not observable.
        pytest.skip("internals-only: the priority header was observed by patching legacy "
                    "_retry_utility_async.ExecuteFunctionAsync; Rust outgoing request headers are not observable "
                    "(known gap 6, docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#gap-6). The High-priority upsert ran.")
        assert priority_headers[-1] == "High"
        # upsert item with low priority
        await created_container.upsert_item(body=item2, priority="Low")
        # check that headers passed low priority
        assert priority_headers[-1] == "Low"
        # Repeat for read operations
        item1_read = await created_container.read_item("item1", "pk1", priority="High")
        assert priority_headers[-1] == "High"
        item2_read = await created_container.read_item("item2", "pk2", priority="Low")
        assert priority_headers[-1] == "Low"
        # repeat for query
        query = [doc async for doc in created_container.query_items("Select * from c",
                                                                    partition_key="pk1", priority="High")]

        assert priority_headers[-1] == "High"

        # Negative Test: Verify that if we send a value other than High or Low that it will not set the header value
        # and result in bad request
        try:
            item2_read = await created_container.read_item("item2", "pk2", priority="Medium")
        except exceptions.CosmosHttpResponseError as e:
            assert e.status_code == StatusCodes.BAD_REQUEST
        _retry_utility_async.ExecuteFunctionAsync = self.OriginalExecuteFunction
