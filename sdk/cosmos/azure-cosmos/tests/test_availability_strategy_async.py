# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import asyncio
import logging
import os
import re
import unittest
import uuid
from typing import Optional, Any

import pytest
import pytest_asyncio
from azure.core.exceptions import ServiceResponseError

import test_config
from _fault_injection_transport_async import FaultInjectionTransportAsync
from azure.cosmos import _location_cache
from azure.cosmos._availability_strategy_config import _validate_hedging_config
from azure.cosmos.aio import CosmosClient
from azure.cosmos.documents import _OperationType as OperationType
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.http_constants import ResourceType

_Unset: Any = object()
class MockHandler(logging.Handler):
    def __init__(self):
        super(MockHandler, self).__init__()
        self.messages = []

    def reset(self):
        self.messages = []

    def emit(self, record):
        self.messages.append(record.msg)

@pytest_asyncio.fixture()
async def setup():
    # Set up logging
    logger = logging.getLogger("azure")
    logger.addHandler(TestAsyncAvailabilityStrategy.MOCK_HANDLER)
    logger.setLevel(logging.DEBUG)

    config = test_config.TestConfig()
    if config.masterKey == '[YOUR_KEY_HERE]' or config.host == '[YOUR_ENDPOINT_HERE]':
        raise Exception(
            "You must specify your Azure Cosmos account values for "
            "'masterKey' and 'host' at the top of this class to run the "
            "tests.")
    test_client = CosmosClient(config.host, config.masterKey)
    database_account = await test_client._get_database_account()
    write_locations = [loc["name"] for loc in database_account._WritableLocations]
    read_locations = [loc["name"] for loc in database_account._ReadableLocations]

    # Use first writable location as primary region and second as failover
    account_location_with_client = {
        "write_locations": write_locations,
        "read_locations": read_locations,
        "region_1": write_locations[0],
        "region_2": write_locations[1] if len(write_locations) > 1 else read_locations[0],
        "client_without_fault": test_client
    }

    yield account_location_with_client
    await test_client.close()
    logger.removeHandler(TestAsyncAvailabilityStrategy.MOCK_HANDLER)

# Operation constants
READ = "read"
CREATE = "create"
UPSERT = "upsert"
REPLACE = "replace"
DELETE = "delete"
PATCH = "patch"
BATCH = "batch"
QUERY = "query"
QUERY_PK = "query_pk"
READ_ALL = "read_all"
CHANGE_FEED = "change_feed"

# Non-transient status codes
NON_TRANSIENT_STATUS_CODES = [
    (400, None),
    (409, None),
    (405, None),
    (412, None),
    (413, None),
    (401, None),
    (404, 0)
]

def _create_doc():
    return {
        'id': str(uuid.uuid4()),
        'pk': 'test_pk',
        'name': 'sample document',
        'key': 'value'
    }

async def _perform_read_operation(
        operation,
        container,
        created_doc,
        expected_uris,
        excluded_uris,
        availability_strategy_config: Optional[dict[str, Any]] = _Unset,
        excluded_locations: Optional[list[str]] = None,
        **kwargs):
    excluded_locations = [] if excluded_locations is None else excluded_locations

    """Execute different types of read operations"""
    if availability_strategy_config is not _Unset:
        kwargs['availability_strategy_config'] = availability_strategy_config

    if operation == READ:
        await container.read_item(
            item=created_doc['id'],
            partition_key=created_doc['pk'],
            excluded_locations=excluded_locations,
            **kwargs)
    elif operation == QUERY:
        response = [item async for item in container.query_items(
            query="SELECT * FROM c WHERE c.id=@id",
            parameters=[{"name": "@id", "value": created_doc['id']}],
            excluded_locations=excluded_locations,
            **kwargs
        )]
        assert response[0]['id'] == created_doc['id']
    elif operation == QUERY_PK:
        response = [item async for item in container.query_items(
            query="SELECT * FROM c WHERE c.id=@id AND c.pk=@pk",
            parameters=[{"name": "@id", "value": created_doc['id']}, {"name": "@pk", "value": created_doc['pk']}],
            partition_key=created_doc['pk'],
            excluded_locations=excluded_locations,
            **kwargs
        )]
        assert response[0]['id'] == created_doc['id']
    elif operation == READ_ALL:
        response = [item async for item in container.read_all_items(
            excluded_locations=excluded_locations,
            **kwargs)]
        assert any(item['id'] == created_doc['id'] for item in response)
    elif operation == CHANGE_FEED:
        response = [item async for item in container.query_items_change_feed(
            partition_key=created_doc['pk'],
            excluded_locations=excluded_locations,
            **kwargs)]
        any(item['id'] == created_doc['id'] for item in response)

    _validate_response_uris(
        expected_uris,
        excluded_uris,
        operation_type=_get_operation_type(operation),
        resource_type=ResourceType.Document)

async def _perform_write_operation(
        operation,
        container,
        created_doc,
        expected_uris,
        excluded_uris,
        retry_write=False,
        availability_strategy_config: Optional[dict[str, Any]] = _Unset,
        excluded_locations: Optional[list[str]] = None,
        **kwargs):
    """Execute different types of write operations"""
    excluded_locations = [] if excluded_locations is None else excluded_locations
    if availability_strategy_config is not _Unset:
        kwargs['availability_strategy_config'] = availability_strategy_config

    if operation == CREATE:
        doc = _create_doc()
        await container.create_item(
            body=doc,
            retry_write=retry_write,
            excluded_locations=excluded_locations,
            **kwargs)
    elif operation == UPSERT:
        doc = _create_doc()
        await container.upsert_item(
            body=doc,
            retry_write=retry_write,
            excluded_locations=excluded_locations,
            **kwargs)
    elif operation == REPLACE:
        created_doc['name'] = 'updated document'
        await container.replace_item(
            item=created_doc['id'],
            body=created_doc,
            retry_write=retry_write,
            excluded_locations=excluded_locations,
            **kwargs)
    elif operation == DELETE:
        await container.delete_item(
            item=created_doc['id'],
            partition_key=created_doc['pk'],
            retry_write=retry_write,
            excluded_locations=excluded_locations,
            **kwargs)
    elif operation == PATCH:
        operations = [{"op": "replace", "path": "/name", "value": "patched document"}]
        await container.patch_item(
            item=created_doc['id'],
            partition_key=created_doc['pk'],
            patch_operations=operations,
            retry_write=retry_write,
            excluded_locations=excluded_locations,
            **kwargs)
    elif operation == BATCH:
        doc = _create_doc()
        batch_ops = [
            ("create", (doc,))
        ]
        await container.execute_item_batch(
            batch_ops,
            partition_key=doc['pk'],
            retry_write=retry_write,
            excluded_locations=excluded_locations,
            **kwargs)

    _validate_response_uris(
        expected_uris,
        excluded_uris,
        operation_type=_get_operation_type(operation),
        resource_type=ResourceType.Document)

def _validate_response_uris(expected_location_uris, excluded_location_uris, operation_type=None, resource_type=None):
    """Validate that response came from expected region and not from excluded regions"""
    # Get Request URLs from mock handler messages
    req_urls = []
    for msg in TestAsyncAvailabilityStrategy.MOCK_HANDLER.messages:
        if 'Request URL:' not in msg:
            continue
        
        # If operation_type and resource_type specified, filter messages
        if operation_type and resource_type:
            req_resource_type = re.search(r"'x-ms-thinclient-proxy-resource-type':\s*'([^']+)'", msg)
            req_operation_type = re.search(r"'x-ms-thinclient-proxy-operation-type':\s*'([^']+)'", msg)
            
            if not (req_resource_type and req_operation_type):
                continue
                
            if resource_type != req_resource_type.group(1) or operation_type != req_operation_type.group(1):
                continue
        
        scheme, rest = msg.split()[2].strip("'").split("//", 1)
        req_location = rest.split("/", 1)[0]
        req_urls.append(f"{scheme}//{req_location}/")

    assert set(req_urls) == set(expected_location_uris), "No matching request URLs found in mock handler messages"
    assert all(location not in excluded_location_uris for location in req_urls), "Found request being routed to excluded regions unexpected"

def _validate_error_uri(exc_info, expected_uri):
    """Validate that error response came from expected region"""
    request = exc_info.value.response.get_response_headers()["_request"]
    assert request.url.startswith(expected_uri)

def _get_operation_type(test_operation_type: str) -> str:
    if test_operation_type == READ:
        return OperationType.Read
    if test_operation_type == CREATE:
        return OperationType.Create
    if test_operation_type == UPSERT:
        return OperationType.Upsert
    if test_operation_type == REPLACE:
        return OperationType.Replace
    if test_operation_type == DELETE:
        return OperationType.Delete
    if test_operation_type == PATCH:
        return OperationType.Patch
    if test_operation_type == BATCH:
        return OperationType.Batch
    if test_operation_type == QUERY:
        return OperationType.SqlQuery
    if test_operation_type == QUERY_PK:
        return OperationType.SqlQuery
    if test_operation_type == READ_ALL:
        return OperationType.ReadFeed
    if test_operation_type == CHANGE_FEED:
        return OperationType.ReadFeed

    raise ValueError("invalid operationType")

@pytest.mark.cosmosMultiRegion
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup")
class TestAsyncAvailabilityStrategy:
    """Test class for async availability strategy tests"""

    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_MULTI_PARTITION_ID = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID
    TEST_SINGLE_PARTITION_CONTAINER_ID = test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID

    # Logger instance for capturing requests
    MOCK_HANDLER = MockHandler()

    def setup_method(self):
        """Reset mock handler before each test"""
        self.MOCK_HANDLER.reset()

    async def _setup_method_with_custom_transport(
            self,
            write_locations,
            read_locations,
            custom_transport,
            default_endpoint=None,
            retry_write=False,
            **kwargs):
        """Initialize test client with optional custom transport and endpoint"""
        if default_endpoint is None:
            default_endpoint = self.host

        # Set preferred locations with write locations first
        preferred_locations = write_locations + [loc for loc in read_locations if loc not in write_locations]

        container_id = kwargs.pop("container_id", None)
        if not container_id:
            container_id = self.TEST_CONTAINER_MULTI_PARTITION_ID

        client = CosmosClient(
            default_endpoint, 
            self.master_key,
            preferred_locations=preferred_locations,
            transport=custom_transport,
            retry_write=retry_write,
            **kwargs
        )
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(container_id)
        return {"client": client, "db": db, "col": container}

    def _get_custom_transport_with_fault_injection(
            self,
            predicate,
            error_lambda):
        """Setup test with fault injection"""
        custom_transport = FaultInjectionTransportAsync()
        custom_transport.add_fault(predicate, error_lambda)
        return custom_transport

    async def _clean_up_container(self, client: CosmosClient, database_id:str, container_id:str):
        container = client.get_database_client(database_id).get_container_client(container_id)
        all_items = [item async for item in container.read_all_items()]
        for item in all_items:
            try:
                await container.delete_item(item['id'], item['pk'])
            except Exception:
                pass

    @pytest.mark.parametrize("threshold_ms,threshold_steps_ms, error_message", [
        (-1, 100, "threshold_ms must be positive"),
        (0, 100, "threshold_ms must be positive"),
        (100, -1, "threshold_steps_ms must be positive"),
        (100, 0, "threshold_steps_ms must be positive")
    ])
    def test_invalid_thresholds(self, threshold_ms, threshold_steps_ms, error_message):
        """Test that creating strategy with non-positive thresholds raises ValueError when enabled"""
        with pytest.raises(ValueError, match=error_message):
            config = {'type': 'CrossRegionHedging', 'threshold_ms': threshold_ms,
                      'threshold_steps_ms': threshold_steps_ms}
            _validate_hedging_config(config)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    @pytest.mark.parametrize("client_availability_strategy, request_availability_strategy", [
        (None, {'type':'CrossRegionHedging', 'threshold_ms':150, 'threshold_steps_ms':50}),
        ({'type':'CrossRegionHedging', 'threshold_ms':150, 'threshold_steps_ms':50}, _Unset),
        ({'type':'CrossRegionHedging', 'threshold_ms':150, 'threshold_steps_ms':50},
         {'type':'CrossRegionHedging', 'threshold_ms':150, 'threshold_steps_ms':50})
    ])
    async def test_availability_strategy_in_steady_state(
            self,
            operation,
            client_availability_strategy,
            request_availability_strategy,
            setup):
        """Test for steady state, operations go to first preferred location even with availability strategy enabled"""
        # Setup client with availability strategy
        setup_with_transport = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            None,
            availability_strategy_config=client_availability_strategy)
        doc = _create_doc()
        await setup_with_transport['col'].create_item(doc)
        await asyncio.sleep(0.5)

        container = setup_with_transport['col']
        expected_uris = [_location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])]
        excluded_uris = [_location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])]

        # Test operation
        if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
            await _perform_read_operation(
                operation,
                container,
                doc,
                expected_uris,
                excluded_uris,
                availability_strategy_config=request_availability_strategy)
        else:
            await _perform_write_operation(
                operation,
                container,
                doc,
                expected_uris,
                excluded_uris,
                availability_strategy_config=request_availability_strategy)
        await setup_with_transport['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_transport['db'].id, setup_with_transport['col'].id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation",[READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    @pytest.mark.parametrize("client_availability_strategy, request_availability_strategy", [
        (None, {'type':'CrossRegionHedging', 'threshold_ms':150, 'threshold_steps_ms':50}),
        ({'type':'CrossRegionHedging', 'threshold_ms':150, 'threshold_steps_ms':50}, _Unset),
        ({'type':'CrossRegionHedging', 'threshold_ms':700, 'threshold_steps_ms':50}, {'type':'CrossRegionHedging', 'threshold_ms':150, 'threshold_steps_ms':50})
    ])
    async def test_client_availability_strategy_failover(
            self,
            operation,
            client_availability_strategy,
            request_availability_strategy,
            setup):
        """Test operations failover to second preferred location on errors"""
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))

        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
            1000,  # Add delay to trigger hedging
            CosmosHttpResponseError(status_code=400, message="Injected Error")
        )
        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)

        setup_with_transport = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            custom_transport,
            multiple_write_locations=True,
            availability_strategy_config=client_availability_strategy)
        setup_without_fault = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            None)

        doc = _create_doc()
        await setup_without_fault['col'].create_item(doc)

        # Test operation with fault injection
        if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
            await _perform_read_operation(
                operation,
                setup_with_transport['col'],
                doc,
                [uri_down, failed_over_uri],
                [],
                availability_strategy_config=request_availability_strategy)
        else:
            await _perform_write_operation(
                operation,
                setup_with_transport['col'],
                doc,
                [uri_down, failed_over_uri],
                [],
                retry_write=True,
                availability_strategy_config=request_availability_strategy)
        await setup_with_transport['client'].close()
        await setup_without_fault['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_transport['db'].id, setup_with_transport['col'].id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    @pytest.mark.parametrize("status_code, sub_status_code", NON_TRANSIENT_STATUS_CODES)
    async def test_non_transient_errors_from_failed_over_region(self, operation, status_code: int, sub_status_code: Optional[int], setup):
        """Test that operations non-transient errors from failed over region will be returned as the final result"""
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

        # fault injection in second preferred region
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, failed_over_uri))
        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
            0,
            CosmosHttpResponseError(status_code=status_code, message=f"Injected {status_code} Error", sub_status=sub_status_code)
        )

        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)

        # setup fault injection in first preferred region
        predicate_first_region = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                                            FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                                            FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))
        error_lambda_first_region = lambda r: FaultInjectionTransportAsync.error_after_delay(
            500,
            CosmosHttpResponseError(status_code=503, message="Injected Error")
        )
        custom_transport.add_fault(predicate_first_region, error_lambda_first_region)

        setup_with_fault = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            custom_transport,
            multiple_write_locations=True)

        setup_without_fault = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            None)

        doc = _create_doc()
        await setup_without_fault['col'].create_item(doc)

        expected_uris = [uri_down, failed_over_uri]

        # Test should fail with original error without failover
        strategy = {'type':'CrossRegionHedging', 'threshold_ms':100, 'threshold_steps_ms':50}
        with pytest.raises(CosmosHttpResponseError) as exc_info:
            if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
                await _perform_read_operation(
                    operation,
                    setup_with_fault['col'],
                    doc,
                    expected_uris,
                    [],
                    availability_strategy_config=strategy)
            else:
                await _perform_write_operation(
                    operation,
                    setup_with_fault['col'],
                    doc,
                    expected_uris,
                    [],
                    retry_write=True,
                    availability_strategy_config=strategy)

        # Verify error code
        assert exc_info.value.status_code == status_code
        await setup_with_fault['client'].close()
        await setup_without_fault['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_fault['db'].id, setup_with_fault['col'].id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    async def test_transient_error_from_failed_over_region(self, operation, setup):
        """Test non-CosmosHttpResponseError exceptions from second region will be treated as transient failure,
        the result from first result will be used as the final result"""

        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

        # fault injection in second preferred region
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, failed_over_uri))
        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
            0,
            ServiceResponseError(message="Generic Service Error")
        )

        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)

        # setup fault injection in first preferred region
        predicate_first_region = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                                            FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                                            FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))
        error_lambda_first_region = lambda r: FaultInjectionTransportAsync.error_after_delay(
            500,
            CosmosHttpResponseError(status_code=400, message="Injected Error") # using a non retryable exception here
        )
        custom_transport.add_fault(predicate_first_region, error_lambda_first_region)

        strategy = {'type':'CrossRegionHedging', 'threshold_ms':100, 'threshold_steps_ms':50}
        setup_with_transport = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            custom_transport,
            multiple_write_locations=True)

        setup_without_fault = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            None)

        doc = _create_doc()
        await setup_without_fault['col'].create_item(doc)

        expected_uris = [uri_down, failed_over_uri]

        # Test should fail with error from the first region
        with pytest.raises(CosmosHttpResponseError) as exc_info:
            if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
                await _perform_read_operation(
                    operation,
                    setup_with_transport['col'],
                    doc,
                    expected_uris,
                    [],
                    availability_strategy_config=strategy)
            else:
                await _perform_write_operation(
                    operation,
                    setup_with_transport['col'],
                    doc,
                    expected_uris,
                    [],
                    retry_write=True,
                    availability_strategy_config=strategy)

        # Verify error code matches first region's error
        assert exc_info.value.status_code == 400
        await setup_with_transport['client'].close()
        await setup_without_fault['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_transport['db'].id, setup_with_transport['col'].id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    async def test_request_level_disabled_override_client_policy(self, operation, setup):
        """Test that request-level disabled policy overrides client-level enabled policy"""
        # Setup client with enabled hedging policy
        client_strategy = {'type':'CrossRegionHedging', 'threshold_ms':100, 'threshold_steps_ms':50}

        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))

        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
            500,  # Add delay to trigger hedging
            CosmosHttpResponseError(status_code=400, message="Injected Error")
            # using none retryable errors to verify the request will only go to the first region
        )
        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)
        setup_with_transport = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            custom_transport,
            availability_strategy_config=client_strategy)

        setup_without_fault = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            None)

        doc = _create_doc()
        await setup_without_fault['col'].create_item(doc)

        expected_uris = [uri_down]
        excluded_uris = [failed_over_uri]

        # Test should fail with error from the first region
        with pytest.raises(CosmosHttpResponseError) as exc_info:
            if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
                await _perform_read_operation(operation, setup_with_transport['col'], doc, expected_uris, excluded_uris, availability_strategy_config=None)
            else:
                await _perform_write_operation(operation, setup_with_transport['col'], doc, expected_uris, excluded_uris, retry_write=True, availability_strategy_config=None)

        # Verify error code
        assert exc_info.value.status_code == 400
        await setup_with_transport['client'].close()
        await setup_without_fault['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_transport['db'].id, setup_with_transport['col'].id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    async def test_request_level_enabled_override_client_disabled(self, operation, setup):
        """Test that request-level enabled policy overrides client-level disabled policy"""
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))

        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
            1000,  # Add delay to trigger hedging
            CosmosHttpResponseError(status_code=400, message="Injected Error")
        )
        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)
        setup_with_transport = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            custom_transport,
            multiple_write_locations=True)

        setup_without_fault = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            None)

        doc = _create_doc()
        await setup_without_fault['col'].create_item(doc)

        # Create request-level enabled policy
        request_strategy = {'type':'CrossRegionHedging', 'threshold_ms':100, 'threshold_steps_ms':50}

        expected_uris = [uri_down, failed_over_uri]
        # Test operation with fault injection

        if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
            await _perform_read_operation(operation, setup_with_transport['col'], doc, expected_uris, [], availability_strategy_config=request_strategy)
        else:
            await _perform_write_operation(operation, setup_with_transport['col'], doc, expected_uris, [], retry_write=True, availability_strategy_config=request_strategy)

        await setup_with_transport['client'].close()
        await setup_without_fault['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_transport['db'].id, setup_with_transport['col'].id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation", [CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    async def test_no_cross_region_request_with_retry_write_disabled(self, operation, setup):
        """Test that no cross region hedging occurs when retry_write is disabled for write operations"""

        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))

        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
            500,  # Add delay to trigger hedging
            CosmosHttpResponseError(status_code=400, message="Injected Error")
        )
        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)
        setup_with_transport = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            custom_transport,
            multiple_write_locations=True)

        setup_without_fault = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            None)

        doc = _create_doc()
        await setup_without_fault['col'].create_item(doc)

        expected_uris = [uri_down]
        excluded_uris = [failed_over_uri]
        strategy = {'type':'CrossRegionHedging', 'threshold_ms':100, 'threshold_steps_ms':50}

        # Test should fail with error from the first region
        with pytest.raises(CosmosHttpResponseError) as exc_info:
            await _perform_write_operation(
                operation,
                setup_with_transport['col'],
                doc,
                expected_uris,
                excluded_uris,
                retry_write=False,
                availability_strategy_config=strategy)

        # Verify error code
        assert exc_info.value.status_code == 400
        await setup_with_transport['client'].close()
        await setup_without_fault['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_transport['db'].id, setup_with_transport['col'].id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation", [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    async def test_no_cross_region_request_with_exclude_regions(self, operation, setup):
        """Test that even with request-level CrossRegionHedgingStrategy overrides, there will be no cross region hedging due to excluded regions"""

        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))

        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
            500,  # Add delay to trigger hedging
            CosmosHttpResponseError(status_code=400, message="Injected Error")
        )
        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)
        setup_with_transport = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            custom_transport,
            multiple_write_locations=True)

        setup_without_fault = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            None)

        doc = _create_doc()
        await setup_without_fault['col'].create_item(doc)

        expected_uris = [uri_down]
        excluded_uris = [failed_over_uri]

        strategy = {'type':'CrossRegionHedging', 'threshold_ms':100, 'threshold_steps_ms':50}

        # Test should fail with error from the first region
        with pytest.raises(CosmosHttpResponseError) as exc_info:
            if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
                await _perform_read_operation(
                    operation,
                    setup_with_transport['col'],
                    doc,
                    expected_uris,
                    excluded_uris,
                    excluded_locations=[setup['region_2']],
                    availability_strategy_config=strategy)
            else:
                await _perform_write_operation(
                    operation,
                    setup_with_transport['col'],
                    doc,
                    expected_uris,
                    excluded_uris,
                    retry_write=True,
                    excluded_locations=[setup['region_2']],
                    availability_strategy_config=strategy)

        # Verify error code
        assert exc_info.value.status_code == 400
        await setup_with_transport['client'].close()
        await setup_without_fault['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_transport['db'].id, setup_with_transport['col'].id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation", [READ, QUERY_PK, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    async def test_per_partition_circular_breaker_with_cancelled_first_future(self, operation, setup):
        # QUERY, READ_ALL are not included because currently they are not targeting to a specific pkRange
        os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "True"
        os.environ["AZURE_COSMOS_CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE"] = "5"
        os.environ["AZURE_COSMOS_CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ"] = "5"

        try:
            """Test that when per partition circular breaker is enabled and after hitting the threshold, subsequent requests go directly to second region.
            This test verifies the logic of recording failure of cancelled first_future."""

            # Setup fault injection for first region
            uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
            failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

            predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                                   FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(operation)) and
                                   FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))

            error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
                1000,  # Add delay to trigger hedging
                CosmosHttpResponseError(status_code=503, message="Injected Error")
            )

            custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)

            strategy = {'type':'CrossRegionHedging', 'threshold_ms':100, 'threshold_steps_ms':50}

            setup_with_fault_injection = await self._setup_method_with_custom_transport(
                setup['write_locations'],
                setup['read_locations'],
                custom_transport,
                multiple_write_locations=True,
                container_id=self.TEST_SINGLE_PARTITION_CONTAINER_ID
            )
            setup_without_fault = await self._setup_method_with_custom_transport(
                setup['write_locations'],
                setup['read_locations'],
                None,
                container_id=self.TEST_SINGLE_PARTITION_CONTAINER_ID)

            # First operation will attempt first region, fail, and then succeed in second region
            expected_uris = [uri_down, failed_over_uri]

            for _ in range(5):
                doc = _create_doc()
                await setup_without_fault['col'].create_item(body=doc)
                if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
                    await _perform_read_operation(
                        operation,
                        setup_with_fault_injection['col'],
                        doc,
                        expected_uris,
                        [],
                        availability_strategy_config=strategy)
                else:
                    await _perform_write_operation(
                        operation,
                        setup_with_fault_injection['col'],
                        doc,
                        expected_uris,
                        [],
                        retry_write=True,
                        availability_strategy_config=strategy)

            # Subsequent operations should go directly to second region due to per partition circular breaker
            expected_uris = [failed_over_uri]
            excluded_uris = [uri_down]
            doc = _create_doc()
            await setup_without_fault['col'].create_item(body=doc)
            self.MOCK_HANDLER.reset()

            await asyncio.sleep(2)
            if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
                await _perform_read_operation(
                    operation,
                    setup_with_fault_injection['col'],
                    doc,
                    expected_uris,
                    excluded_uris,
                    availability_strategy_config=strategy)
            else:
                await _perform_write_operation(
                    operation,
                    setup_with_fault_injection['col'],
                    doc,
                    expected_uris,
                    excluded_uris,
                    retry_write=True,
                    availability_strategy_config=strategy)

            await setup_with_fault_injection['client'].close()
            await setup_without_fault['client'].close()
        finally:
            del os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"]
            del os.environ["AZURE_COSMOS_CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_WRITE"]
            del os.environ["AZURE_COSMOS_CONSECUTIVE_ERROR_COUNT_TOLERATED_FOR_READ"]
        await self._clean_up_container(setup['client_without_fault'], setup_with_fault_injection['db'].id, setup_with_fault_injection['col'].id)

    @pytest.mark.asyncio
    async def test_max_concurrency(self, setup):
        """Test availability_strategy_max_concurrency will be effective"""

        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

        # fault injection in first preferred region
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_is_operation_type(r, OperationType.Read) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))
        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
            500,
            CosmosHttpResponseError(status_code=400, message="Injected Error")
        )

        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)

        strategy = {'type':'CrossRegionHedging', 'threshold_ms':100, 'threshold_steps_ms':50}
        setup_with_transport = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            custom_transport,
            multiple_write_locations=True,
            availability_strategy_max_concurrency=1)

        doc = _create_doc()
        await setup_with_transport['col'].create_item(doc)

        # Test should fail with error from the first region
        with pytest.raises(CosmosHttpResponseError) as exc_info:
            await _perform_read_operation(
                READ,
                setup_with_transport['col'],
                doc,
                [uri_down],
                [failed_over_uri],
                availability_strategy_config=strategy)

        # Verify error code matches first region's error
        assert exc_info.value.status_code == 400
        await setup_with_transport['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_transport['db'].id, setup_with_transport['col'].id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("operation",[READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED, CREATE, UPSERT, REPLACE, DELETE, PATCH, BATCH])
    async def test_default_availability_strategy_with_ppaf_enabled(
            self,
            operation,
            setup):
        """Test availability strategy is enabled when ppaf is enabled, operations failover to second preferred location on errors"""
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_1'])
        failed_over_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, setup['region_2'])

        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_is_operation_type(r, _get_operation_type(
                                   operation)) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))

        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(
            1000,  # Add delay to trigger hedging
            CosmosHttpResponseError(status_code=400, message="Injected Error")
        )
        custom_transport = self._get_custom_transport_with_fault_injection(predicate, error_lambda)
        #enable ppaf
        is_get_account_predicate = lambda r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
        # Set the database account response to have PPAF enabled
        ppaf_enabled_database_account = \
            lambda r, inner: FaultInjectionTransportAsync.transform_topology_ppaf_enabled(inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            ppaf_enabled_database_account)

        setup_with_transport = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            custom_transport,
            multiple_write_locations=True)
        setup_without_fault = await self._setup_method_with_custom_transport(
            setup['write_locations'],
            setup['read_locations'],
            None)

        doc = _create_doc()
        await setup_without_fault['col'].create_item(doc)

        # Test operation with fault injection
        if operation in [READ, QUERY, QUERY_PK, READ_ALL, CHANGE_FEED]:
            await _perform_read_operation(
                operation,
                setup_with_transport['col'],
                doc,
                [uri_down, failed_over_uri],
                [])
        else:
            await _perform_write_operation(
                operation,
                setup_with_transport['col'],
                doc,
                [uri_down, failed_over_uri],
                [],
                retry_write=True)
        await setup_with_transport['client'].close()
        await setup_without_fault['client'].close()
        await self._clean_up_container(setup['client_without_fault'], setup_with_transport['db'].id,
                                       setup_with_transport['col'].id)

if __name__ == '__main__':
    unittest.main()