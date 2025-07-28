import unittest
import uuid
from unittest import SkipTest
from unittest.mock import patch

import pytest

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import test_config
from azure.cosmos import PartitionKey, CosmosDict
from _fault_injection_transport import FaultInjectionTransport
from azure.cosmos._gone_retry_policy import PartitionKeyRangeGoneRetryPolicy
from azure.cosmos._resource_throttle_retry_policy import ResourceThrottleRetryPolicy
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.documents import _OperationType
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos.partition_key import NonePartitionKeyValue


@pytest.mark.cosmosEmulator
class TestReadManyItems(unittest.TestCase):
    """Test cases for the read_many_items API."""

    configs = test_config.TestConfig
    host = configs.host
    masterKey = configs.masterKey
    client: cosmos_client = None
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

    def setUp(self):
        self.client = cosmos_client.CosmosClient(self.host, self.masterKey)
        self.database = self.client.get_database_client(self.configs.TEST_DATABASE_ID)
        self.container = self.database.create_container(
            id='read_many_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path="/id")
        )

    def tearDown(self):
        """Clean up async resources after each test."""
        if self.container:
            try:
                self.database.delete_container(self.container)
            except exceptions.CosmosHttpResponseError as e:
                # Container may have been deleted by the test itself
                if e.status_code != 404:
                    raise

    @staticmethod
    def _create_items_for_read_many(container, count, id_prefix="item"):
        """Helper to create items and return a list for read_many_items."""
        items_to_read = []
        item_ids = []
        for i in range(count):
            doc_id = f"{id_prefix}_{i}_{uuid.uuid4()}"
            item_ids.append(doc_id)
            items_to_read.append((doc_id, doc_id))
            container.create_item({'id': doc_id, 'data': i})
        return items_to_read, item_ids

    def _setup_fault_injection(self, error_to_inject, inject_once=False):
        """Helper to set up a client with fault injection for read_many_items queries."""
        fault_injection_transport = FaultInjectionTransport()
        client_with_faults = cosmos_client.CosmosClient(self.host, self.masterKey, transport=fault_injection_transport)
        container_with_faults = client_with_faults.get_database_client(self.database.id).get_container_client(
            self.container.id)

        fault_has_been_injected = False

        def predicate(request):
            nonlocal fault_has_been_injected
            is_query = (request.method == 'POST' and
                        FaultInjectionTransport.predicate_is_operation_type(request, _OperationType.SqlQuery))
            if is_query:
                if inject_once:
                    if not fault_has_been_injected:
                        fault_has_been_injected = True
                        return True
                    return False
                return True
            return False

        def fault_action(request):
            raise error_to_inject

        fault_injection_transport.add_fault(predicate, fault_action)
        return container_with_faults

    def test_read_many_items_with_missing_items(self):
        """Tests read_many_items with a mix of existing and non-existent items."""
        items_to_read, _ = self._create_items_for_read_many(self.container, 3, "existing_item")

        # Add 2 non-existent items
        items_to_read.append(("non_existent_item1" + str(uuid.uuid4()), "non_existent_pk1"))
        items_to_read.append(("non_existent_item2" + str(uuid.uuid4()), "non_existent_pk2"))
        read_items = self.container.read_many_items(items=items_to_read)

        self.assertEqual(len(read_items), 3)
        returned_ids = {item['id'] for item in read_items}
        expected_ids = {item_tuple[0] for item_tuple in items_to_read if "existing" in item_tuple[0]}
        self.assertSetEqual(returned_ids, expected_ids)

    def test_read_many_items_single_item(self):
        # Create one item using the helper. This also creates the item in the container.
        items_to_read, item_ids = self._create_items_for_read_many(self.container, 1)

        # Read the single item using read_many_items
        read_items = self.container.read_many_items(items=items_to_read)

        # Verify that one item was returned and it's the correct one
        self.assertEqual(len(read_items), 1)
        self.assertEqual(read_items[0]['id'], item_ids[0])

    def test_read_many_single_item_uses_point_read(self):
        """Test that for a single item, read_many_items uses the read_item optimization."""
        with unittest.mock.patch.object(self.container, 'read_item', autospec=True) as mock_read_item:
            # Mock the return value of read_item to be a CosmosDict with headers
            mock_headers = CaseInsensitiveDict({'x-ms-request-charge': '1.23'})
            mock_read_item.return_value = CosmosDict(
                {"id": "item1", "_rid": "some_rid"},
                response_headers = mock_headers
            )

            items_to_read = [("item1", "pk1")]
            result = self.container.read_many_items(items=items_to_read)

            # Verify that read_item was called exactly once with the correct arguments
            mock_read_item.assert_called_once_with(item="item1", partition_key="pk1")

            # Verify the result contains the item and headers
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['id'], 'item1')

    def test_read_many_items_different_partition_key(self):
        """Tests read_many_items with partition key different from id."""
        container_pk = self.database.create_container(
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
                container_pk.create_item({'id': doc_id, 'pk': pk_value, 'data': i})
                items_to_read.append((doc_id, pk_value))

            read_items = container_pk.read_many_items(items=items_to_read)

            self.assertEqual(len(read_items), len(item_ids))
            read_ids = {item['id'] for item in read_items}
            self.assertSetEqual(read_ids, set(item_ids))
        finally:
            self.database.delete_container(container_pk)


    def test_read_many_items_fails_with_incomplete_hierarchical_pk(self):
        """Tests that read_many_items raises ValueError for an incomplete hierarchical partition key."""
        container_hpk = self.database.create_container(
            id='read_many_hpk_incomplete_container_' + str(uuid.uuid4()),
            partition_key=PartitionKey(path=["/tenantId", "/userId"], kind="MultiHash")
        )
        try:
            items_to_read = []
            # Create a valid item
            doc_id = f"item_valid_{uuid.uuid4()}"
            tenant_id = "tenant1"
            user_id = "user1"
            container_hpk.create_item({'id': doc_id, 'tenantId': tenant_id, 'userId': user_id})
            items_to_read.append((doc_id, [tenant_id, user_id]))

            # Add an item with an incomplete partition key
            incomplete_pk_item_id = f"item_incomplete_{uuid.uuid4()}"
            items_to_read.append((incomplete_pk_item_id, ["tenant_only"]))

            # The operation should fail with a ValueError
            with self.assertRaises(ValueError) as context:
                container_hpk.read_many_items(items=items_to_read)

            self.assertIn("Number of components in partition key value (1) does not match definition (2)",
                          str(context.exception))
        finally:
            self.database.delete_container(container_hpk)

    def test_read_many_items_hierarchical_partition_key(self):
        """Tests read_many_items with hierarchical partition key."""
        container_hpk = self.database.create_container(
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
                container_hpk.create_item({'id': doc_id, 'tenantId': tenant_id, 'userId': user_id, 'data': i})
                items_to_read.append((doc_id, [tenant_id, user_id]))

            read_items = container_hpk.read_many_items(items=items_to_read)

            self.assertEqual(len(read_items), len(item_ids))
            read_ids = {item['id'] for item in read_items}
            self.assertSetEqual(read_ids, set(item_ids))
        finally:
            self.database.delete_container(container_hpk)

    def test_headers_being_returned(self):
        """Tests that response headers are available."""
        items_to_read, item_ids = self._create_items_for_read_many(self.container, 5)

        read_items = self.container.read_many_items(items=items_to_read)
        headers = read_items.get_response_headers()

        self.assertEqual(len(read_items), len(item_ids))
        self.assertIsNotNone(headers)
        self.assertIn('x-ms-request-charge', headers)
        self.assertIn('x-ms-activity-id', headers)
        self.assertGreaterEqual(float(headers.get('x-ms-request-charge', 0)), 0)
        self.assertTrue(headers.get('x-ms-activity-id'))

    @SkipTest
    def test_read_many_items_large_count(self):
        """Tests read_many_items with a large number of items."""
        items_to_read, item_ids = self._create_items_for_read_many(self.container, 3100)

        read_items = self.container.read_many_items(items=items_to_read)

        self.assertEqual(len(read_items), len(item_ids))
        read_ids = {item['id'] for item in read_items}
        self.assertSetEqual(read_ids, set(item_ids))

    def test_read_many_items_surfaces_exceptions(self):
        """Tests that read_many_items surfaces exceptions from the transport layer."""
        error_to_inject = CosmosHttpResponseError(status_code=503, message="Injected Service Unavailable Error")
        container_with_faults = self._setup_fault_injection(error_to_inject)
        items_to_read, _ = self._create_items_for_read_many(self.container, 10)

        with self.assertRaises(CosmosHttpResponseError) as context:
            container_with_faults.read_many_items(items=items_to_read)

        self.assertEqual(context.exception.status_code, 503)
        self.assertIn("Injected Service Unavailable Error", str(context.exception))

    def test_read_many_items_with_throttling_retry(self):
        """Tests that the retry policy handles a throttling error (429) and succeeds."""
        error_to_inject = CosmosHttpResponseError(
            status_code=429,
            message="Throttling error injected for testing",
            headers={'x-ms-retry-after-ms': '10'}
        )
        container_with_faults = self._setup_fault_injection(error_to_inject, inject_once=True)
        items_to_read, item_ids = self._create_items_for_read_many(self.container, 5, "item_for_throttle")

        original_should_retry = ResourceThrottleRetryPolicy.ShouldRetry

        def side_effect_should_retry(self_instance, exception, *args, **kwargs):
            return original_should_retry(self_instance, exception)

        with patch(
                'azure.cosmos._resource_throttle_retry_policy.ResourceThrottleRetryPolicy.ShouldRetry',
                side_effect=side_effect_should_retry,
                autospec=True
        ) as mock_should_retry:
            read_items = container_with_faults.read_many_items(items=items_to_read)
            mock_should_retry.assert_called_once()
            self.assertEqual(len(read_items), len(item_ids))
            read_ids = {item['id'] for item in read_items}
            self.assertSetEqual(read_ids, set(item_ids))

    def test_read_many_items_with_gone_retry(self):
        """Tests that the retry policy handles a Gone (410) error and succeeds."""
        error_to_inject = CosmosHttpResponseError(
            status_code=410,
            message="Gone error injected for testing",
        )
        # Substatus for PartitionKeyRangeGone is required for the policy to trigger
        error_to_inject.sub_status = 1002
        container_with_faults = self._setup_fault_injection(error_to_inject, inject_once=True)
        items_to_read, item_ids = self._create_items_for_read_many(self.container, 20, "item_for_gone")

        with patch(
                'azure.cosmos._gone_retry_policy.PartitionKeyRangeGoneRetryPolicy.ShouldRetry',
                autospec=True
        ) as mock_should_retry:
            read_items = container_with_faults.read_many_items(items=items_to_read)
            mock_should_retry.assert_called_once()
            self.assertEqual(len(read_items), len(item_ids))
            read_ids = {item['id'] for item in read_items}
            self.assertSetEqual(read_ids, set(item_ids))

    def test_read_many_after_container_recreation(self):
        """Tests read_many_items after a container is deleted and recreated."""
        container_id = self.container.id
        initial_items_to_read, initial_item_ids = self._create_items_for_read_many(self.container, 3, "initial")
        read_items_before = self.container.read_many_items(items=initial_items_to_read)
        self.assertEqual(len(read_items_before), len(initial_item_ids))
        self.database.delete_container(self.container)

        # Recreate the container and re-assign self.container so it's cleaned up in tearDown
        self.container = self.database.create_container(id=container_id,
                                                         partition_key=PartitionKey(path="/id"))

        new_items_to_read, new_item_ids = self._create_items_for_read_many(self.container, 5, "new")

        read_items_after = self.container.read_many_items(items=new_items_to_read)
        self.assertEqual(len(read_items_after), len(new_item_ids))
        read_ids = {item['id'] for item in read_items_after}
        self.assertSetEqual(read_ids, set(new_item_ids))

    def test_read_many_items_concurrency_internals(self):
        """Tests that read_many_items properly chunks large requests."""
        items_to_read = []
        for i in range(2500):
            doc_id = f"chunk_item_{i}_{uuid.uuid4()}"
            items_to_read.append((doc_id, doc_id))

        with patch.object(self.container.client_connection, 'QueryItems') as mock_query:
            mock_query.return_value = []

            self.container.read_many_items(items=items_to_read)

            self.assertEqual(mock_query.call_count, 3)
            call_args = mock_query.call_args_list

            self.assertEqual(len(call_args[0][0][1]['parameters']), 1000)
            self.assertEqual(len(call_args[1][0][1]['parameters']), 1000)
            self.assertEqual(len(call_args[2][0][1]['parameters']), 500)