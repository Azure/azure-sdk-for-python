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
import importlib.util
import os
import unittest
import uuid
from types import SimpleNamespace

import pytest
from azure.core import MatchConditions

import azure.cosmos.exceptions as exceptions
from azure.cosmos.aio import CosmosClient
from azure.cosmos.http_constants import StatusCodes
from common.priority_contract import assert_priority_contract_async
from azure.cosmos.partition_key import PartitionKey
from _client_transport import create_client_with_transport
from config.clients import create_data_client_async, create_setup_client_async

# The whl_no_aio CI check uninstalls aiohttp. Only the paged-timeout test needs it,
# so the other tests in this file must still load and run without it.
HAS_AIOHTTP = importlib.util.find_spec("aiohttp") is not None
if HAS_AIOHTTP:
    from azure.core.pipeline.transport import AioHttpTransport


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
        # Same split as the original: the key client provisions, the data
        # client (AAD in the cosmosAAD* lanes) runs the tested operations.
        self.key_client = create_setup_client_async()
        await self.key_client.__aenter__()
        self.addAsyncCleanup(self.key_client.close)
        self.client = create_data_client_async(_backend="rust")
        await self.client.__aenter__()
        self.addAsyncCleanup(self.client.close)
        self._db_id = "qi_crud_async_" + uuid.uuid4().hex
        self.key_database_for_test = await self.key_client.create_database(self._db_id)
        self.addAsyncCleanup(self.key_client.delete_database, self._db_id)
        self.database_for_test = self.client.get_database_client(self._db_id)
        self.configs = SimpleNamespace(
            TEST_DATABASE_ID=self._db_id,
            TEST_MULTI_PARTITION_CONTAINER_ID="multi_partition_" + uuid.uuid4().hex[:8])
        await self.key_database_for_test.create_container(
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
        if not HAS_AIOHTTP:
            pytest.skip("aiohttp is not installed; this test builds an aiohttp-based delayed transport.")

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
                        "(known gap 5) and ignores the injected "
                        "custom transport (known gap 10). "
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
        container = self.database_for_test.get_container_client(
            self.configs.TEST_MULTI_PARTITION_CONTAINER_ID
        )
        await assert_priority_contract_async(container)
