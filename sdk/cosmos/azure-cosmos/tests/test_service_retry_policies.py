# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from azure.core.exceptions import ServiceRequestError, ServiceResponseError

import test_config
from _retry_test_utils import configure_retry_regions, retry_test_client, send_to_test_host
from azure.core.pipeline.transport import HttpRequest
from azure.cosmos import (CosmosClient, _retry_utility, DatabaseAccount, _global_endpoint_manager,
                          _location_cache)
from azure.cosmos.documents import ConnectionPolicy
from azure.cosmos.documents import _OperationType
from azure.cosmos.http_constants import HttpHeaders


@pytest.mark.cosmosEmulator
class TestServiceRetryPolicies(unittest.TestCase):
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_ID = test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID

    REGION1 = "West US"
    REGION2 = "East US"
    REGION3 = "West US 2"

    @classmethod
    def setUpClass(cls):
        if (cls.masterKey == '[YOUR_KEY_HERE]' or
                cls.host == '[YOUR_ENDPOINT_HERE]'):
            raise Exception(
                "You must specify your Azure Cosmos account values for "
                "'masterKey' and 'host' at the top of this class to run the "
                "tests.")
        cls.client = CosmosClient(cls.host, cls.masterKey)
        cls.created_database = cls.client.get_database_client(cls.TEST_DATABASE_ID)
        cls.created_container = cls.created_database.get_container_client(cls.TEST_CONTAINER_ID)

    def _setup_read_regions(self, location_cache, regions):
        configure_retry_regions(location_cache, regions)
        self.assertEqual(len(location_cache.read_regional_routing_contexts), len(regions))

    def _setup_write_regions(self, location_cache, regions):
        configure_retry_regions(location_cache, regions, regions)
        self.assertEqual(len(location_cache.write_regional_routing_contexts), len(regions))

    def _create_retry_client(self):
        context = retry_test_client(self.host, self.masterKey)
        client = context.__enter__()
        self.addCleanup(context.__exit__, None, None, None)
        return client

    def test_service_request_retry_policy(self):
        mock_client = self._create_retry_client()
        db = mock_client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_ID)

        created_item = container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})

        # Change the location cache to have 3 preferred read regions
        original_location_cache = mock_client.client_connection._global_endpoint_manager.location_cache
        self._setup_read_regions(original_location_cache, [self.REGION1, self.REGION2, self.REGION3])

        expected_counter = len(original_location_cache.read_regional_routing_contexts)

        # Test read with IgnoreQuery mock (allows query/pkranges requests through)
        mf = self.MockExecuteServiceRequestExceptionIgnoreQuery(_retry_utility.ExecuteFunction)
        with patch.object(_retry_utility, 'ExecuteFunction', mf):
            with pytest.raises(ServiceRequestError):
                container.read_item(created_item['id'], created_item['pk'])
            assert mf.counter == expected_counter

        # Now we test with a query operation
        self._setup_read_regions(original_location_cache, [self.REGION1, self.REGION2, self.REGION3])

        expected_counter = len(original_location_cache.read_regional_routing_contexts)
        mf = self.MockExecuteServiceRequestException()
        with patch.object(_retry_utility, 'ExecuteFunction', mf):
            with pytest.raises(ServiceRequestError):
                list(container.query_items(query="SELECT * FROM c", partition_key=created_item['pk']))
            assert mf.counter == expected_counter

        # Now we change the location cache to have only 1 preferred read region
        self._setup_read_regions(original_location_cache, [self.REGION1])
        expected_counter = len(original_location_cache.read_regional_routing_contexts)
        mf = self.MockExecuteServiceRequestException()
        with patch.object(_retry_utility, 'ExecuteFunction', mf):
            with pytest.raises(ServiceRequestError):
                container.read_item(created_item['id'], created_item['pk'])
            assert mf.counter == expected_counter

        # Now we try it out with a write request
        self._setup_write_regions(original_location_cache, [self.REGION1, self.REGION2])
        expected_counter = len(original_location_cache.write_regional_routing_contexts)
        mf = self.MockExecuteServiceRequestException()
        with patch.object(_retry_utility, 'ExecuteFunction', mf):
            with pytest.raises(ServiceRequestError):
                container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
            assert mf.counter == expected_counter

    def test_service_response_retry_policy(self):
        mock_client = self._create_retry_client()
        db = mock_client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_ID)

        created_item = container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})

        # Change the location cache to have 3 preferred read regions
        original_location_cache = mock_client.client_connection._global_endpoint_manager.location_cache
        self._setup_read_regions(original_location_cache, [self.REGION1, self.REGION2, self.REGION3])

        mf = self.MockExecuteServiceResponseExceptionIgnoreQuery(Exception, _retry_utility.ExecuteFunction)
        with patch.object(_retry_utility, 'ExecuteFunction', mf):
            with pytest.raises(ServiceResponseError):
                container.read_item(created_item['id'], created_item['pk'])
            assert mf.counter == 3

        # Now we change the location cache to have only 1 preferred read region
        self._setup_read_regions(original_location_cache, [self.REGION1])
        expected_counter = len(original_location_cache.read_regional_routing_contexts)
        mf = self.MockExecuteServiceResponseExceptionIgnoreQuery(Exception, _retry_utility.ExecuteFunction)
        with patch.object(_retry_utility, 'ExecuteFunction', mf):
            with pytest.raises(ServiceResponseError):
                container.read_item(created_item['id'], created_item['pk'])
            assert mf.counter == expected_counter

        # Now we try it out with a write request
        self._setup_write_regions(original_location_cache, [self.REGION1, self.REGION2])
        mf = self.MockExecuteServiceResponseException(Exception)
        with patch.object(_retry_utility, 'ExecuteFunction', mf):
            with pytest.raises(ServiceResponseError):
                # Even though we have 2 preferred write endpoints,
                # we will only run the exception once due to no retries on write requests
                container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
            assert mf.counter == 1

        # Now we try it out with a write request with retry write enabled - which should retry once
        mf = self.MockExecuteServiceResponseException(Exception)
        with patch.object(_retry_utility, 'ExecuteFunction', mf):
            with pytest.raises(ServiceResponseError):
                container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())}, retry_write=2)
            assert mf.counter == 2

    def test_service_request_connection_retry_policy(self):
        # Mock the client retry policy to see the same-region retries that happen there
        exception = ServiceRequestError("mock exception")
        exception.exc_type = Exception
        connection_retry_policy = test_config.MockConnectionRetryPolicy(resource_type="docs", error=exception)
        mock_client = CosmosClient(self.host, self.masterKey, connection_retry_policy=connection_retry_policy)
        db = mock_client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_ID)

        # We retry ServiceRequestExceptions 3 times in the to the same endpoint before raising the exception
        # regardless of operation type
        try:
            container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
            pytest.fail("Exception was not raised.")
        except ServiceRequestError:
            assert connection_retry_policy.counter == 3

        try:
            container.read_item("some_id", "some_pk")
            pytest.fail("Exception was not raised.")
        except ServiceRequestError:
            assert connection_retry_policy.counter == 3

    def test_service_response_connection_retry_policy(self):
        # Mock the client retry policy to see the same-region retries that happen there
        exception = ServiceResponseError("mock exception")
        exception.exc_type = Exception
        connection_retry_policy = test_config.MockConnectionRetryPolicy(resource_type="docs", error=exception)
        mock_client = CosmosClient(self.host, self.masterKey, connection_retry_policy=connection_retry_policy)
        db = mock_client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_ID)

        # We retry ServiceResponseExceptions 3 times in the to the same endpoint before raising the exception
        # for read operations, but 0 times for write requests
        try:
            container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
            pytest.fail("Exception was not raised.")
        except ServiceResponseError:
            assert connection_retry_policy.counter == 0

        try:
            container.read_item("some_id", "some_pk")
            pytest.fail("Exception was not raised.")
        except ServiceResponseError:
            assert connection_retry_policy.counter == 3

    def test_global_endpoint_manager_retry(self):
        # For this test we mock both the ConnectionRetryPolicy and the GetDatabaseAccountStub
        # - ConnectionRetryPolicy allows us to raise Service exceptions only for chosen requests and track endpoints used
        # - GetDatabaseAccountStub allows us to receive any number of endpoints for that call independent of account used
        exception = ServiceRequestError("mock exception")
        exception.exc_type = Exception
        connection_retry_policy = test_config.MockConnectionRetryPolicy(resource_type="docs", error=exception)
        with patch.object(_global_endpoint_manager._GlobalEndpointManager, '_GetDatabaseAccountStub',
                          self.MockGetDatabaseAccountStub):
            mock_client = CosmosClient(self.host, self.masterKey, connection_retry_policy=connection_retry_policy,
                                       preferred_locations=[self.REGION1, self.REGION2])

        db = mock_client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_ID)

        with patch.object(_global_endpoint_manager._GlobalEndpointManager, '_GetDatabaseAccountStub',
                          self.MockGetDatabaseAccountStub):
            with pytest.raises(ServiceRequestError):
                container.create_item({"id": str(uuid.uuid4()), "pk": str(uuid.uuid4())})
            assert connection_retry_policy.counter == 3
            # 4 total in region retries
            assert len(connection_retry_policy.request_endpoints) == 4

        # Now we try with a read request - reset the policy to reset the counter
        connection_retry_policy.request_endpoints = []
        with patch.object(_global_endpoint_manager._GlobalEndpointManager, '_GetDatabaseAccountStub',
                          self.MockGetDatabaseAccountStub):
            with pytest.raises(ServiceRequestError):
                container.read_item("some_id", "some_pk")
            assert connection_retry_policy.counter == 3
            # 4 total requests in each main region (preferred read region 1 -> preferred read region 2)
            assert len(connection_retry_policy.request_endpoints) == 8

    class MockExecuteServiceRequestException(object):
        def __init__(self):
            self.counter = 0

        def __call__(self, func, *args, **kwargs):
            self.counter = self.counter + 1
            exception = ServiceRequestError("mock exception")
            exception.exc_type = Exception
            raise exception

    class MockExecuteServiceRequestExceptionIgnoreQuery(object):
        def __init__(self, original_execute_function):
            self.counter = 0
            self.original_execute_function = original_execute_function

        def __call__(self, func, *args, **kwargs):
            if len(args) > 1:
                request_obj = args[1]
                if not (hasattr(request_obj, "resource_type") and hasattr(request_obj, "operation_type")):
                    return self.original_execute_function(func, *args, **kwargs)
                if ((request_obj.resource_type == "docs" and request_obj.operation_type == "Query") or
                        (request_obj.resource_type == "pkranges" and request_obj.operation_type == "ReadFeed")):
                    # Ignore query requests, As an additional ReadFeed might occur during a regular Read operation
                    return self.original_execute_function(func, *args, **kwargs)
                self.counter = self.counter + 1
                exception = ServiceRequestError("mock exception")
                exception.exc_type = Exception
                raise exception
            return self.original_execute_function(func, *args, **kwargs)

    class MockExecuteServiceResponseException(object):
        def __init__(self, err_type):
            self.err_type = err_type
            self.counter = 0

        def __call__(self, func, *args, **kwargs):
            self.counter = self.counter + 1
            exception = ServiceResponseError("mock exception")
            exception.exc_type = self.err_type
            raise exception

    class MockExecuteServiceResponseExceptionIgnoreQuery(object):
        def __init__(self, err_type, original_execute_function):
            self.err_type = err_type
            self.counter = 0
            self.original_execute_function = original_execute_function

        def __call__(self, func, *args, **kwargs):
            if len(args) > 1:
                request_obj = args[1]
                if not (hasattr(request_obj, "resource_type") and hasattr(request_obj, "operation_type")):
                    return self.original_execute_function(func, *args, **kwargs)
                if ((request_obj.resource_type == "docs" and request_obj.operation_type == "Query") or
                        (request_obj.resource_type == "pkranges" and request_obj.operation_type == "ReadFeed")):
                    # Ignore query requests, As an additional ReadFeed might occur during a regular Read operation
                    return self.original_execute_function(func, *args, **kwargs)
                self.counter = self.counter + 1
                exception = ServiceResponseError("mock exception")
                exception.exc_type = self.err_type
                raise exception
            return self.original_execute_function(func, *args, **kwargs)

    def MockGetDatabaseAccountStub(self, endpoint):
        read_regions = ["West US", "East US"]
        read_locations = []
        for loc in read_regions:
            read_locations.append({'databaseAccountEndpoint': endpoint, 'name': loc})
        write_regions = ["West US"]
        write_locations = []
        for loc in write_regions:
            locational_endpoint = _location_cache.LocationCache.GetLocationalEndpoint(endpoint, loc)
            write_locations.append({'databaseAccountEndpoint': locational_endpoint, 'name': loc})
        multi_write = False

        db_acc = DatabaseAccount()
        db_acc.DatabasesLink = "/dbs/"
        db_acc.MediaLink = "/media/"
        db_acc._ReadableLocations = read_locations
        db_acc._WritableLocations = write_locations
        db_acc._EnableMultipleWritableLocations = multi_write
        db_acc.ConsistencyPolicy = {"defaultConsistencyLevel": "Session"}
        return db_acc


@pytest.mark.cosmosEmulator
class TestServiceRetryPolicyHelpers(unittest.TestCase):
    def test_synthetic_regions_survive_refresh_and_unavailability(self):
        cache = _location_cache.LocationCache("https://127.0.0.1:8081/", ConnectionPolicy())
        regions = ["West US", "East US", "West US 2"]
        configure_retry_regions(cache, regions, regions[:2])
        cache.update_location_cache()
        self.assertFalse(cache.is_default_endpoint_regional())
        self.assertEqual(len({c.get_primary() for c in cache.read_regional_routing_contexts}), 3)
        self.assertEqual(len({c.get_primary() for c in cache.write_regional_routing_contexts}), 2)
        first = cache.read_regional_routing_contexts[0].get_primary()
        self.assertEqual(cache.get_location_from_endpoint(first), regions[0])
        cache.mark_endpoint_unavailable_for_read(first, True)
        self.assertEqual(len(cache.read_regional_routing_contexts), 3)
        self.assertEqual(cache.read_regional_routing_contexts[-1].get_primary(), first)
        configure_retry_regions(cache, regions[:1])
        self.assertEqual(len(cache.read_regional_routing_contexts), 1)
        self.assertEqual(cache.location_unavailability_info_by_endpoint, {})

    def test_synthetic_transport_uses_real_test_host_and_restores_url(self):
        url = "https://westus.retry-test.invalid/dbs/test/colls/items?value=1"
        request = HttpRequest("GET", url)
        seen = []

        def send(outgoing, **kwargs):
            seen.append(outgoing.url)
            raise ServiceRequestError("transport error")

        with self.assertRaises(ServiceRequestError):
            send_to_test_host(send, "https://127.0.0.1:8081/", request)
        self.assertEqual(seen, ["https://127.0.0.1:8081/dbs/test/colls/items?value=1"])
        self.assertEqual(request.url, url)
        real = HttpRequest("GET", "https://127.0.0.1:8081/dbs")
        sender = Mock(return_value="response")
        self.assertEqual(send_to_test_host(sender, "https://127.0.0.1:8081/", real), "response")
        sender.assert_called_once_with(real)

    def test_is_read_retryable_request_uses_operation_type_fallback(self):
        request = SimpleNamespace(headers={})
        request_params = SimpleNamespace(operation_type=_OperationType.Read)
        assert _retry_utility._is_read_retryable_request(request, request_params) is True

    def test_non_synthetic_transport_does_not_change_tls_options(self):
        request = HttpRequest("GET", "https://localhost:8081/dbs/test")
        sender = Mock(return_value="response")
        send_to_test_host(sender, "https://localhost:8081/", request, connection_verify=True)
        sender.assert_called_once_with(request, connection_verify=True)

    def test_is_read_retryable_request_write_without_header_is_not_retryable(self):
        request = SimpleNamespace(headers={})
        request_params = SimpleNamespace(operation_type=_OperationType.Create)
        assert _retry_utility._is_read_retryable_request(request, request_params) is False

    def test_is_read_retryable_request_matches_thin_client_header(self):
        # Thin-client proxy sets the operation type as a request header; the
        # helper must recognise reads from that header even when request_params
        # is not threaded through (older call paths).
        request = SimpleNamespace(
            headers={HttpHeaders.ThinClientProxyOperationType: _OperationType.Read}
        )
        assert _retry_utility._is_read_retryable_request(request, None) is True

    def test_is_read_retryable_request_with_no_request_uses_params_only(self):
        # ConnectionRetryPolicy.send pops request_params from context options;
        # confirm the helper still classifies correctly when only request_params
        # is available (request is None).
        request_params = SimpleNamespace(operation_type=_OperationType.Read)
        assert _retry_utility._is_read_retryable_request(None, request_params) is True


@pytest.mark.cosmosEmulator
@pytest.mark.parametrize(
    "host,supplied,expected",
    [
        ("https://localhost:8081/", True, False),
        ("https://127.0.0.1:8081/", True, False),
        ("https://account.documents.azure.com/", True, True),
        ("https://account.documents.azure.com/", "custom-ca.pem", "custom-ca.pem"),
        ("https://localhost.example.com/", True, True),
        ("https://127.0.0.10/", True, True),
    ],
)
def test_synthetic_transport_preserves_target_tls_behavior(host, supplied, expected):
    request = HttpRequest("GET", "https://westus.retry-test.invalid/dbs/test")
    original_url = request.url
    seen = []

    def send(outgoing, **kwargs):
        seen.append((outgoing.url, kwargs["connection_verify"]))
        raise ServiceRequestError("transport error")

    with pytest.raises(ServiceRequestError):
        send_to_test_host(send, host, request, connection_verify=supplied)
    assert seen == [(host + "dbs/test", expected)]
    assert request.url == original_url
