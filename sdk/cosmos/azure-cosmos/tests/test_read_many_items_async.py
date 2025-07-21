# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""End-to-end test for read_many_items API."""
import asyncio
import time
import unittest
import uuid
from unittest.mock import patch
import pytest
import test_config
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
from azure.cosmos.documents import _OperationType
from azure.cosmos.exceptions import CosmosHttpResponseError
from _fault_injection_transport_async import FaultInjectionTransportAsync
from azure.cosmos._resource_throttle_retry_policy import ResourceThrottleRetryPolicy


@pytest.mark.cosmosEmulator
class TestReadManyItems(unittest.IsolatedAsyncioTestCase):
    """Test cases for the read_many_items API."""

    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    client: CosmosClient = None
    database = None
    container = None

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' in the test_config class to run the "
                "tests.")
        cls.client = CosmosClient(cls.host, cls.masterKey)

    async def asyncSetUp(self):
        """Set up async resources before each test."""
        self.database = self.client.get_database_client(self.configs.TEST_DATABASE_ID)

        # Create container asynchronously
        self.container = await self.database.create_container(
            id='read_many_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id")
        )

    async def asyncTearDown(self):
        """Clean up async resources after each test."""
        if self.container:
            await self.database.delete_container(self.container)

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # Close async client
            import asyncio
            asyncio.run(cls.client.close())

    async def test_read_many_items_with_missing_items(self):
        """Tests read_many_items with a mix of existing and non-existent items."""
        items_to_read, _ = await self._create_items_for_read_many(self.container, 3, "existing_item")

        # Add 2 non-existent items
        items_to_read.append(("non_existent_item1" + str(uuid.uuid4()), "non_existent_pk1"))
        items_to_read.append(("non_existent_item2" + str(uuid.uuid4()), "non_existent_pk2"))

        read_items = await self.container.read_many_items(items=items_to_read)

        self.assertEqual(len(read_items), 3)
        returned_ids = {item['id'] for item in read_items}
        expected_ids = {item_tuple[0] for item_tuple in items_to_read if "existing" in item_tuple[0]}
        self.assertSetEqual(returned_ids, expected_ids)

    async def test_read_many_items_different_partition_key(self):
        """Tests read_many_items with partition key different from id."""
        container_pk = await self.database.create_container(
            id='read_many_pk_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk")
        )
        try:
            items_to_read = []
            item_ids = []
            for i in range(5):
                doc_id = f"item{i}_{uuid.uuid4()}"
                pk_value = f"pk_{i}"
                item_ids.append(doc_id)
                await container_pk.create_item({'id': doc_id, 'pk': pk_value, 'data': i})
                items_to_read.append((doc_id, pk_value))

            read_items = await container_pk.read_many_items(items=items_to_read)

            self.assertEqual(len(read_items), len(item_ids))
            read_ids = {item['id'] for item in read_items}
            self.assertSetEqual(read_ids, set(item_ids))
        finally:
            await self.database.delete_container(container_pk)

    async def test_read_many_items_hierarchical_partition_key(self):
        """Tests read_many_items with hierarchical partition key."""
        container_hpk = await self.database.create_container(
            id='read_many_hpk_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path=["/tenantId", "/userId"], kind="MultiHash")
        )
        try:
            items_to_read = []
            item_ids = []
            for i in range(3):
                doc_id = f"item{i}_{uuid.uuid4()}"
                tenant_id = f"tenant{i % 2}"
                user_id = f"user{i}"
                item_ids.append(doc_id)
                await container_hpk.create_item({'id': doc_id, 'tenantId': tenant_id, 'userId': user_id, 'data': i})
                items_to_read.append((doc_id, [tenant_id, user_id]))

            read_items = await container_hpk.read_many_items(items=items_to_read)

            self.assertEqual(len(read_items), len(item_ids))
            read_ids = {item['id'] for item in read_items}
            self.assertSetEqual(read_ids, set(item_ids))
        finally:
            await self.database.delete_container(container_hpk)

    async def test_headers_being_returned(self):
        """Tests that response headers are available."""
        items_to_read, item_ids = await self._create_items_for_read_many(self.container, 5)

        read_items = await self.container.read_many_items(items=items_to_read)
        headers = read_items.get_response_headers()

        self.assertEqual(len(read_items), len(item_ids))
        self.assertIsNotNone(headers)
        self.assertIn('x-ms-request-charge', headers)
        self.assertIn('x-ms-activity-id', headers)
        self.assertGreaterEqual(float(headers.get('x-ms-request-charge', 0)), 0)
        self.assertTrue(headers.get('x-ms-activity-id'))

    async def test_read_many_items(self):
        """Tests the basic functionality of read_many_items."""
        items_to_read, item_ids = await self._create_items_for_read_many(self.container, 5)

        read_items = await self.container.read_many_items(items=items_to_read)

        self.assertEqual(len(read_items), len(item_ids))
        read_ids = {item['id'] for item in read_items}
        self.assertSetEqual(read_ids, set(item_ids))

    async def test_read_many_items_large_count(self):
        """Tests read_many_items with a large number of items."""
        items_to_read, item_ids = await self._create_items_for_read_many(self.container, 3100)

        read_items = await self.container.read_many_items(items=items_to_read)

        self.assertEqual(len(read_items), len(item_ids))
        read_ids = {item['id'] for item in read_items}
        self.assertSetEqual(read_ids, set(item_ids))

    async def test_read_many_items_with_injected_fault_async(self):
        """Tests that read_many_items surfaces exceptions from the transport layer."""
        fault_injection_transport = FaultInjectionTransportAsync()
        client_with_faults = CosmosClient(self.host, self.masterKey, transport=fault_injection_transport)
        try:
            container_with_faults = client_with_faults.get_database_client(self.database.id).get_container_client(
                self.container.id)
            items_to_read, _ = await self._create_items_for_read_many(self.container, 2100)

            predicate = lambda r: FaultInjectionTransportAsync.predicate_is_operation_type(r, _OperationType.SqlQuery)
            error_to_inject = CosmosHttpResponseError(status_code=503, message="Injected Service Unavailable Error")

            async def fault_action(request):
                raise error_to_inject

            fault_injection_transport.add_fault(predicate, fault_action)

            with self.assertRaises(CosmosHttpResponseError) as context:
                await container_with_faults.read_many_items(items=items_to_read)

            self.assertEqual(context.exception.status_code, 503)
            self.assertIn("Injected Service Unavailable Error", str(context.exception))
        finally:
            await client_with_faults.close()

    async def test_read_many_items_with_throttling_retry_async(self):
        """Tests that the retry policy handles a throttling error (429) and succeeds."""
        fault_injection_transport = FaultInjectionTransportAsync()
        client_with_faults = CosmosClient(self.host, self.masterKey, transport=fault_injection_transport)
        try:
            container_with_faults = client_with_faults.get_database_client(self.database.id).get_container_client(
                self.container.id)
            items_to_read, item_ids = await self._create_items_for_read_many(self.container, 1100, "item_for_throttle")

            original_should_retry = ResourceThrottleRetryPolicy.ShouldRetry

            def side_effect_should_retry(self_instance, exception, *args, **kwargs):
                return original_should_retry(self_instance, exception, *args, **kwargs)

            with patch(
                    'azure.cosmos._resource_throttle_retry_policy.ResourceThrottleRetryPolicy.ShouldRetry',
                    side_effect=side_effect_should_retry,
                    autospec=True
            ) as mock_should_retry:
                fault_has_been_injected = False
                error_to_inject = CosmosHttpResponseError(
                    status_code=429,
                    message="Throttling error injected for testing",
                    headers={'x-ms-retry-after-ms': '10'}
                )

                def predicate(request):
                    nonlocal fault_has_been_injected
                    is_query = (request.method == 'POST' and
                                FaultInjectionTransportAsync.predicate_is_operation_type(request,
                                                                                         _OperationType.SqlQuery))
                    if is_query and not fault_has_been_injected:
                        fault_has_been_injected = True
                        return True
                    return False

                async def fault_action(request):
                    raise error_to_inject

                fault_injection_transport.add_fault(predicate, fault_action)

                read_items = await container_with_faults.read_many_items(items=items_to_read)

                mock_should_retry.assert_called_once()
                self.assertEqual(len(read_items), len(item_ids))
                read_ids = {item['id'] for item in read_items}
                self.assertSetEqual(read_ids, set(item_ids))
        finally:
            await client_with_faults.close()

    async def test_read_many_after_container_recreation(self):
        """Tests read_many_items after a container is deleted and recreated."""
        container_proxy = self.container
        initial_items_to_read, initial_item_ids = await self._create_items_for_read_many(container_proxy, 3, "initial")

        read_items_before = await container_proxy.read_many_items(items=initial_items_to_read)
        self.assertEqual(len(read_items_before), len(initial_item_ids))

        await self.database.delete_container(container_proxy)

        with self.assertRaises(CosmosHttpResponseError) as context:
            await container_proxy.read_many_items(items=initial_items_to_read)
        self.assertEqual(context.exception.status_code, 404)

        await self.database.create_container(id=container_proxy.id, partition_key=PartitionKey(path="/id"))

        new_items_to_read, new_item_ids = await self._create_items_for_read_many(container_proxy, 5, "new")

        read_items_after = await container_proxy.read_many_items(items=new_items_to_read)
        self.assertEqual(len(read_items_after), len(new_item_ids))
        read_ids = {item['id'] for item in read_items_after}
        self.assertSetEqual(read_ids, set(new_item_ids))

    async def test_read_many_items_concurrency_internals(self):
        """Tests that read_many_items properly chunks large requests."""
        items_to_read = []
        for i in range(2500):
            doc_id = f"chunk_item_{i}_{uuid.uuid4()}"
            items_to_read.append((doc_id, doc_id))

        with patch.object(self.container.client_connection, 'QueryItems') as mock_query:
            class MockAsyncIterator:
                def __aiter__(self):
                    return self

                async def __anext__(self):
                    raise StopAsyncIteration

            mock_query.return_value = MockAsyncIterator()

            await self.container.read_many_items(items=items_to_read)

            self.assertEqual(mock_query.call_count, 3)
            call_args = mock_query.call_args_list
            self.assertEqual(len(call_args[0][0][1]['parameters']), 1000)
            self.assertEqual(len(call_args[1][0][1]['parameters']), 1000)
            self.assertEqual(len(call_args[2][0][1]['parameters']), 500)

    async def _create_items_for_read_many(self, container, count, id_prefix="item"):
        """Helper to create items and return a list for read_many_items."""
        items_to_read = []
        item_ids = []
        for i in range(count):
            doc_id = f"{id_prefix}_{i}_{uuid.uuid4()}"
            item_ids.append(doc_id)
            await container.create_item({'id': doc_id, 'data': i})
            items_to_read.append((doc_id, doc_id))
        return items_to_read, item_ids

if __name__ == '__main__':
    unittest.main()