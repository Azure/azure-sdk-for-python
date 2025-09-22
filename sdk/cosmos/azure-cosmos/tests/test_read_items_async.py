# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""End-to-end test for read_items API."""
import asyncio
import unittest
import uuid
from unittest.mock import patch
import pytest
from azure.core.utils import CaseInsensitiveDict

import test_config
from azure.cosmos import PartitionKey, CosmosDict
from azure.cosmos.aio import CosmosClient
from azure.cosmos.documents import _OperationType
from azure.cosmos.exceptions import CosmosHttpResponseError
from _fault_injection_transport_async import FaultInjectionTransportAsync
from azure.cosmos._resource_throttle_retry_policy import ResourceThrottleRetryPolicy

@pytest.mark.cosmosEmulator
class TestReadItemsAsync(unittest.IsolatedAsyncioTestCase):
    """Test cases for the read_items API."""

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
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")

    async def asyncSetUp(self):
        self.client = CosmosClient(self.host, self.masterKey)
        self.database = self.client.get_database_client(self.configs.TEST_DATABASE_ID)
        self.container = await self.database.create_container(
            id='read_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id")
        )

    async def asyncTearDown(self):
        """Clean up async resources after each test."""
        if self.container:
            try:
                await self.database.delete_container(self.container)
            except CosmosHttpResponseError as e:
                # Container may have been deleted by the test itself
                if e.status_code != 404:
                    raise
        if self.client:
            await self.client.close()

    @staticmethod
    async def _create_records_for_read_items(container, count, id_prefix="item"):
        """Helper to create items and return a list for read_items."""
        items_to_read = []
        item_ids = []
        tasks = []
        for i in range(count):
            doc_id = f"{id_prefix}_{i}_{uuid.uuid4()}"
            item_ids.append(doc_id)
            items_to_read.append((doc_id, doc_id))
            tasks.append(container.create_item({'id': doc_id, 'data': i}))

        await asyncio.gather(*tasks)
        return items_to_read, item_ids

    def _setup_fault_injection_async(self, error_to_inject, inject_once=False):
        """Helper to set up a client with fault injection for async read_items queries."""
        fault_injection_transport = FaultInjectionTransportAsync()
        client_with_faults = CosmosClient(self.host, self.masterKey, transport=fault_injection_transport)
        container_with_faults = client_with_faults.get_database_client(self.database.id).get_container_client(
            self.container.id)

        fault_has_been_injected = False

        def predicate(request):
            nonlocal fault_has_been_injected
            is_query = (request.method == 'POST' and
                        FaultInjectionTransportAsync.predicate_is_operation_type(request, _OperationType.SqlQuery))
            if is_query:
                if inject_once:
                    if not fault_has_been_injected:
                        fault_has_been_injected = True
                        return True
                    return False
                return True
            return False

        async def fault_action(request):
            raise error_to_inject

        fault_injection_transport.add_fault(predicate, fault_action)
        return container_with_faults, client_with_faults

    async def test_read_items_with_missing_items_async(self):
        """Tests read_items with a mix of existing and non-existent items."""
        items_to_read, _ = await self._create_records_for_read_items(self.container, 3, "existing_item")

        # Add 2 non-existent items
        items_to_read.append(("non_existent_item1" + str(uuid.uuid4()), "non_existent_pk1"))
        items_to_read.append(("non_existent_item2" + str(uuid.uuid4()), "non_existent_pk2"))

        read_items = await self.container.read_items(items=items_to_read)

        self.assertEqual(len(read_items), 3)
        returned_ids = {item['id'] for item in read_items}
        expected_ids = {item_tuple[0] for item_tuple in items_to_read if "existing" in item_tuple[0]}
        self.assertSetEqual(returned_ids, expected_ids)

    async def test_read_items_single_item_async(self):
        # Create one item using the helper. This also creates the item in the container.
        items_to_read, item_ids = await self._create_records_for_read_items(self.container, 1)

        # Read the single item using read_items
        read_items = await self.container.read_items(items=items_to_read)

        # Verify that one item was returned and it's the correct one
        self.assertEqual(len(read_items), 1)
        self.assertEqual(read_items[0]['id'], item_ids[0])


    async def test_read_items_different_partition_key_async(self):
        """Tests read_items with partition key different from id."""
        container_pk = await self.database.create_container(
            id='read_pk_container_' + str(uuid.uuid4()),
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

            read_items = await container_pk.read_items(items=items_to_read)

            self.assertEqual(len(read_items), len(item_ids))
            read_ids = {item['id'] for item in read_items}
            self.assertSetEqual(read_ids, set(item_ids))
        finally:
            await self.database.delete_container(container_pk)

    async def test_read_items_fails_with_incomplete_hierarchical_pk_async(self):
        """Tests that read_items raises ValueError for an incomplete hierarchical partition key."""
        container_hpk = await self.database.create_container(
            id='read_hpk_incomplete_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path=["/tenantId", "/userId"], kind="MultiHash")
        )
        try:
            items_to_read = []
            # Create a valid item
            doc_id = f"item_valid_{uuid.uuid4()}"
            tenant_id = "tenant1"
            user_id = "user1"
            await container_hpk.create_item({'id': doc_id, 'tenantId': tenant_id, 'userId': user_id})
            items_to_read.append((doc_id, [tenant_id, user_id]))

            # Add an item with an incomplete partition key
            incomplete_pk_item_id = f"item_incomplete_{uuid.uuid4()}"
            items_to_read.append((incomplete_pk_item_id, ["tenant_only"]))

            # The operation should fail with a ValueError
            with self.assertRaises(ValueError) as context:
                await container_hpk.read_items(items=items_to_read)

            self.assertIn("Number of components in partition key value (1) does not match definition (2)",
                          str(context.exception))
        finally:
            await self.database.delete_container(container_hpk)

    async def test_read_items_hierarchical_partition_key_async(self):
        """Tests read_items with hierarchical partition key."""
        container_hpk = await self.database.create_container(
            id='read_hpk_container_' + str(uuid.uuid4()),
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

            read_items = await container_hpk.read_items(items=items_to_read)

            self.assertEqual(len(read_items), len(item_ids))
            read_ids = {item['id'] for item in read_items}
            self.assertSetEqual(read_ids, set(item_ids))
        finally:
            await self.database.delete_container(container_hpk)

    async def test_read_items_preserves_input_order_async(self):
        """Tests that read_items preserves the original order of input items."""
        container_pk = await self.database.create_container(
            id='read_order_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk")
        )

        try:
            # Create items with varied partition keys to ensure cross-partition queries
            all_items = []

            # Create items with alternating partition keys to ensure they span partitions
            for i in range(50):
                doc_id = f"order_item_{i}_{uuid.uuid4()}"
                # Use different partition keys to ensure items are spread across partitions
                pk_value = f"pk_{i % 5}"

                # Create the item in the container
                await container_pk.create_item({'id': doc_id, 'pk': pk_value, 'order_value': i})
                all_items.append((doc_id, pk_value))

            # Create a complex order for the read operation
            scrambled_items = []
            scrambled_items.extend(all_items[25:])  # Second half first
            scrambled_items.extend(all_items[:25])  # Then first half

            # Add a few more out-of-order items
            if len(all_items) >= 30:
                # Move some items from the middle to the end
                moved_items = scrambled_items[10:15]
                scrambled_items = scrambled_items[:10] + scrambled_items[15:]
                scrambled_items.extend(moved_items)

            # Read items using read_items with scrambled order
            read_items = await container_pk.read_items(items=scrambled_items)

            # Verify that all items were returned
            self.assertEqual(len(read_items), len(scrambled_items))

            # Verify the order matches the scrambled input order
            for i, item in enumerate(read_items):
                expected_id = scrambled_items[i][0]
                expected_pk = scrambled_items[i][1]
                self.assertEqual(
                    item['id'],
                    expected_id,
                    f"Item at position {i} does not match input order. Expected ID {expected_id}, got {item['id']}"
                )
                self.assertEqual(
                    item['pk'],
                    expected_pk,
                    f"Item at position {i} does not match input order. Expected PK {expected_pk}, got {item['pk']}"
                )

        finally:
            # Clean up
            await self.database.delete_container(container_pk)

    async def test_read_items_order_using_zip_comparison_async(self):
        """Tests that read_items_async preserves the original order using zip and boolean comparison."""
        container_pk = await self.database.create_container(
            id='read_order_zip_async_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk")
        )

        try:
            # Create items with varied partition keys
            all_items = []
            for i in range(30):
                doc_id = f"zip_async_item_{i}_{uuid.uuid4()}"
                pk_value = f"pk_{i % 5}"  # Distribute across 5 partition keys

                # Create the item in the container
                await container_pk.create_item({'id': doc_id, 'pk': pk_value, 'order_value': i})

                # Add to our list
                all_items.append((doc_id, pk_value))

            # Read items asynchronously
            read_items = await container_pk.read_items(items=all_items)

            # Verify correct count
            self.assertEqual(len(read_items), len(all_items))

            # Use the zip method to verify order preservation
            consolidated = zip(all_items, read_items)
            matching = [x[0][0] == x[1]["id"] and x[0][1] == x[1]["pk"] for x in consolidated]

            # Assert all items match in order
            self.assertTrue(all(matching),
                            "Order was not preserved in async version. Input order doesn't match output order.")

        finally:
            await self.database.delete_container(container_pk)

    async def test_read_failure_preserves_headers_async(self):
        """Tests that if a query fails, the exception contains the headers from the failed request."""
        # 1. Define headers and the error to inject
        failed_headers = CaseInsensitiveDict({
            'x-ms-request-charge': '12.34',
            'x-ms-activity-id': 'a-fake-activity-id',
            'x-ms-session-token': 'session-token-for-failure'
        })

        # CosmosHttpResponseError populates the headers attribute from the response object passed during initialization
        # So we need to create a mock response object with the headers we want to inject.
        mock_response = type('MockResponse', (), {
            'headers': failed_headers,
            'reason': 'Mock reason for failure',
            'status_code': 429,
            'request': 'mock_request'  # Add request attribute
        })

        # 3. Create the error to inject, passing the mock response
        error_to_inject = CosmosHttpResponseError(
            message = "Simulated query failure with headers",
            response = mock_response()
        )

        # 2. Use the fault injection helper to get a container that will raise the error
        container_with_faults, client_with_faults = self._setup_fault_injection_async(error_to_inject)
        try:
            # 3. Create items to trigger a query
            items_to_read, _ = await self._create_records_for_read_items(self.container, 5)

            # 4. Call read_items and assert that the correct exception is raised
            with self.assertRaises(CosmosHttpResponseError) as context:
                await container_with_faults.read_items(items=items_to_read)

            # 5. Verify the exception contains the injected headers
            exc = context.exception
            self.assertEqual(exc.status_code, 429)
            self.assertIsNotNone(exc.headers)
            self.assertEqual(exc.headers.get('x-ms-request-charge'), '12.34')
            self.assertEqual(exc.headers.get('x-ms-activity-id'), 'a-fake-activity-id')
            self.assertEqual(exc.headers.get('x-ms-session-token'), 'session-token-for-failure')

        finally:
            # 6. Clean up the client with fault injection
            await client_with_faults.close()


    async def test_read_items_with_no_results_preserve_headers_async(self):
        """Tests read_items with only non-existent items, expecting an empty result."""
        items_to_read = [
            ("non_existent_item_1_" + str(uuid.uuid4()), "non_existent_pk_1"),
            ("non_existent_item_2_" + str(uuid.uuid4()), "non_existent_pk_2")
        ]

        # Call read_items with the list of non-existent items.
        read_items = await self.container.read_items(items=items_to_read)
        headers = read_items.get_response_headers()
        # Verify that the result is an empty list.
        self.assertEqual(len(read_items), 0)
        self.assertListEqual(list(headers.keys()), ['x-ms-request-charge'])
        # Verify the request charge is a positive value.
        self.assertGreater(float(headers.get('x-ms-request-charge')), 0)

    async def test_headers_being_returned_on_success_async(self):
        """Tests that on success, only the aggregated request charge header is returned."""
        # Create enough items to trigger at least two query chunks.
        items_to_read, item_ids = await self._create_records_for_read_items(self.container, 5)

        read_items = await self.container.read_items(items=items_to_read)
        headers = read_items.get_response_headers()

        self.assertEqual(len(read_items), len(item_ids))
        self.assertIsNotNone(headers)

        # On success, only the aggregated request charge should be returned.
        self.assertListEqual(list(headers.keys()), ['x-ms-request-charge'])
        # Verify the request charge is a positive value.
        self.assertGreater(float(headers.get('x-ms-request-charge')), 0)


    async def test_read_items_large_count_async(self):
        """Tests read_items with a large number of items."""
        items_to_read, item_ids = await self._create_records_for_read_items(self.container, 3100)

        read_items = await self.container.read_items(items=items_to_read)

        self.assertEqual(len(read_items), len(item_ids))
        read_ids = {item['id'] for item in read_items}
        self.assertSetEqual(read_ids, set(item_ids))

    async def test_read_items_surfaces_exceptions_async(self):
        """Tests that read_items surfaces exceptions from the transport layer."""
        error_to_inject = CosmosHttpResponseError(status_code=503, message="Injected Service Unavailable Error")
        container_with_faults, client_with_faults = self._setup_fault_injection_async(error_to_inject)
        try:
            items_to_read, _ = await self._create_records_for_read_items(self.container, 10)

            with self.assertRaises(CosmosHttpResponseError) as context:
                await container_with_faults.read_items(items=items_to_read)

            self.assertEqual(context.exception.status_code, 503)
            self.assertIn("Injected Service Unavailable Error", str(context.exception))
        finally:
            await client_with_faults.close()

    async def test_read_items_with_throttling_retry_async(self):
        """Tests that the retry policy handles a throttling error (429) and succeeds."""
        error_to_inject = CosmosHttpResponseError(
            status_code=429,
            message="Throttling error injected for testing",
            headers={'x-ms-retry-after-ms': '10'}
        )
        container_with_faults, client_with_faults = self._setup_fault_injection_async(error_to_inject,
                                                                                       inject_once=True)
        try:
            items_to_read, item_ids = await self._create_records_for_read_items(self.container, 5, "item_for_throttle")

            original_should_retry = ResourceThrottleRetryPolicy.ShouldRetry

            def side_effect_should_retry(self_instance, exception, *args, **kwargs):
                return original_should_retry(self_instance, exception)

            with patch(
                    'azure.cosmos._resource_throttle_retry_policy.ResourceThrottleRetryPolicy.ShouldRetry',
                    side_effect=side_effect_should_retry,
                    autospec=True
            ) as mock_should_retry:
                read_items = await container_with_faults.read_items(items=items_to_read)
                mock_should_retry.assert_called_once()
                self.assertEqual(len(read_items), len(item_ids))
                read_ids = {item['id'] for item in read_items}
                self.assertSetEqual(read_ids, set(item_ids))
        finally:
            await client_with_faults.close()

    async def test_read_items_with_gone_retry_async(self):
        """Tests that the retry policy handles a Gone (410) error and succeeds."""
        error_to_inject = CosmosHttpResponseError(
            status_code=410,
            message="Gone error injected for testing",
        )
        error_to_inject.sub_status = 1002  # Substatus for PartitionKeyRangeGone is required
        container_with_faults, client_with_faults = self._setup_fault_injection_async(error_to_inject,
                                                                                       inject_once=True)
        try:
            items_to_read, item_ids = await self._create_records_for_read_items(self.container, 20, "item_for_gone")

            with patch(
                    'azure.cosmos._gone_retry_policy.PartitionKeyRangeGoneRetryPolicy.ShouldRetry',
                    autospec=True
            ) as mock_should_retry:
                read_items = await container_with_faults.read_items(items=items_to_read)
                mock_should_retry.assert_called_once()
                self.assertEqual(len(read_items), len(item_ids))
                read_ids = {item['id'] for item in read_items}
                self.assertSetEqual(read_ids, set(item_ids))
        finally:
            await client_with_faults.close()

    async def test_read_after_container_recreation_async(self):
        """Tests read_items after a container is deleted and recreated with a different configuration."""
        container_id = self.container.id
        initial_items_to_read, initial_item_ids = await self._create_records_for_read_items(self.container, 3,
                                                                                             "initial")

        read_items_before = await self.container.read_items(items=initial_items_to_read)
        self.assertEqual(len(read_items_before), len(initial_item_ids))

        await self.database.delete_container(self.container)

        # Recreate the container with a different partition key and throughput
        self.container = await self.database.create_container(
            id=container_id,
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=10100
        )

        # Create new items with the new partition key structure
        new_items_to_read = []
        new_item_ids = []
        creation_tasks = []
        for i in range(5):
            doc_id = f"new_item_{i}_{uuid.uuid4()}"
            pk_value = f"new_pk_{i}"
            new_item_ids.append(doc_id)
            new_items_to_read.append((doc_id, pk_value))
            task = self.container.create_item({'id': doc_id, 'pk': pk_value, 'data': i})
            creation_tasks.append(task)
        await asyncio.gather(*creation_tasks)

        read_items_after = await self.container.read_items(items=new_items_to_read)
        self.assertEqual(len(read_items_after), len(new_item_ids))
        read_ids = {item['id'] for item in read_items_after}
        self.assertSetEqual(read_ids, set(new_item_ids))

    async def test_read_items_concurrency_internals_async(self):
        """Tests that read_items properly chunks large requests."""
        items_to_read = []
        for i in range(2500):
            doc_id = f"chunk_item_{i}_{uuid.uuid4()}"
            items_to_read.append((doc_id, doc_id))

        with patch.object(self.container.client_connection, 'QueryItems') as mock_query:
            # The mock now needs to return an object with a .by_page() method,
            # which in turn returns an async iterator.
            class MockPageIterator:
                def __aiter__(self):
                    return self

                async def __anext__(self):
                    raise StopAsyncIteration

            class MockQueryIterator:
                def by_page(self, **kwargs):
                    return MockPageIterator()

            mock_query.return_value = MockQueryIterator()

            await self.container.read_items(items=items_to_read)

            self.assertEqual(mock_query.call_count, 3)
            call_args = mock_query.call_args_list
            self.assertEqual(len(call_args[0][0][1]['parameters']), 1000)
            self.assertEqual(len(call_args[1][0][1]['parameters']), 1000)
            self.assertEqual(len(call_args[2][0][1]['parameters']), 500)

    async def test_read_items_multiple_physical_partitions_and_hook_async(self):
        """Tests async read_items on a container with multiple physical partitions and verifies response_hook."""
        # Create a container with high throughput to force multiple physical partitions
        multi_partition_container = await self.database.create_container(
            id='multi_partition_container_async_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/pk"),
            offer_throughput=11000
        )
        try:
            # 1. Verify that we have more than one physical partition
            # We must consume the async iterator to get the list of partition key ranges.
            pk_ranges = [
                pk_range async for pk_range in
                multi_partition_container.client_connection._ReadPartitionKeyRanges(
                    multi_partition_container.container_link
                )
            ]
            self.assertGreater(len(pk_ranges), 1, "Container should have multiple physical partitions.")


            # 2. Create items across different logical partitions
            creation_tasks = []
            items_to_read = []
            all_item_ids = set()
            for i in range(200):
                doc_id = f"item_{i}_{uuid.uuid4()}"
                pk = i % 2
                all_item_ids.add(doc_id)
                task = multi_partition_container.create_item({'id': doc_id, 'pk': pk, 'data': i})
                creation_tasks.append(task)
                items_to_read.append((doc_id, pk))
            await asyncio.gather(*creation_tasks)

            # 3. Check item distribution across physical partitions
            partition_item_map = {}
            for pk_range in pk_ranges:
                pk_range_id = pk_range['id']
                # Query items within this specific physical partition
                items_in_partition = [
                    item async for item in multi_partition_container.query_items(
                        "SELECT c.id FROM c",
                        partition_key_range_id=pk_range_id
                    )
                ]
                if items_in_partition:
                    partition_item_map[pk_range_id] = {item['id'] for item in items_in_partition}

            # Assert that items were created on more than one physical partition
            self.assertGreater(len(partition_item_map), 1,
                               "Items were not distributed across multiple physical partitions.")

            # 3. Set up a response hook to capture both headers and results
            hook_captured_data = {}

            def response_hook(headers, results_list):
                hook_captured_data['headers'] = headers
                hook_captured_data['results'] = results_list
                hook_captured_data['call_count'] = hook_captured_data.get('call_count', 0) + 1

            # 4. Execute read_items with the hook
            read_items_result = await multi_partition_container.read_items(
                items=items_to_read,
                response_hook=response_hook
            )

            # 5. Verify the response_hook was called correctly
            self.assertEqual(hook_captured_data.get('call_count'), 1,
                             "Response hook should be called exactly once.")

            # Verify the headers passed to the hook
            hook_headers = hook_captured_data.get('headers', {})
            self.assertIn('x-ms-request-charge', hook_headers)
            self.assertGreater(float(hook_headers['x-ms-request-charge']), 0)

            # Verify the CosmosList passed to the hook
            hook_results = hook_captured_data.get('results')
            self.assertIsNotNone(hook_results, "CosmosList should be passed to the hook.")
            self.assertIsInstance(hook_results, list)  # CosmosList inherits from list
            self.assertEqual(len(hook_results), len(items_to_read))
            hook_read_ids = {item['id'] for item in hook_results}
            self.assertSetEqual(hook_read_ids, all_item_ids)

            # Verify that the CosmosList passed to the hook is the same object as the one returned
            self.assertIs(read_items_result, hook_results)

        finally:
            await self.database.delete_container(multi_partition_container)

if __name__ == '__main__':
    unittest.main()