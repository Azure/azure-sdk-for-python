# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import asyncio
import os
import unittest
import uuid
from typing import Dict, Any, List

import pytest
import pytest_asyncio
from azure.core.pipeline.transport._aiohttp import AioHttpTransport
from azure.core.exceptions import ServiceResponseError

import test_config
from azure.cosmos import PartitionKey, _location_cache, _partition_health_tracker
from azure.cosmos._partition_health_tracker import HEALTH_STATUS, UNHEALTHY, UNHEALTHY_TENTATIVE
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from _fault_injection_transport_async import FaultInjectionTransportAsync

REGION_1 = "West US 3"
REGION_2 = "Mexico Central" # "West US"


COLLECTION = "created_collection"
@pytest_asyncio.fixture(scope="class", autouse=True)
async def setup_teardown():
    os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "True"
    client = CosmosClient(TestPerPartitionCircuitBreakerMMAsync.host,
                          TestPerPartitionCircuitBreakerMMAsync.master_key)
    created_database = client.get_database_client(TestPerPartitionCircuitBreakerMMAsync.TEST_DATABASE_ID)
    await created_database.create_container(TestPerPartitionCircuitBreakerMMAsync.TEST_CONTAINER_SINGLE_PARTITION_ID,
                                                                 partition_key=PartitionKey("/pk"),
                                                                 offer_throughput=10000)
    # allow some time for the container to be created as this method is in different event loop
    await asyncio.sleep(2)
    yield
    await created_database.delete_container(TestPerPartitionCircuitBreakerMMAsync.TEST_CONTAINER_SINGLE_PARTITION_ID)
    await client.close()
    os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "False"

def write_operations_and_errors():
    write_operations = ["create", "upsert", "replace", "delete", "patch", "batch"] # "delete_all_items_by_partition_key"]
    errors = []
    error_codes = [408, 500, 502, 503]
    for error_code in error_codes:
        errors.append(CosmosHttpResponseError(
            status_code=error_code,
            message="Some injected error."))
    errors.append(ServiceResponseError(message="Injected Service Response Error."))
    params = []
    for write_operation in write_operations:
        for error in errors:
            params.append((write_operation, error))

    return params

def read_operations_and_errors():
    read_operations = ["read", "query", "query_pk", "changefeed", "changefeed_pk", "changefeed_epk", "read_all_items"]
    errors = []
    error_codes = [408, 500, 502, 503]
    for error_code in error_codes:
        errors.append(CosmosHttpResponseError(
            status_code=error_code,
            message="Some injected error."))
    errors.append(ServiceResponseError(message="Injected Service Response Error."))
    params = []
    for read_operation in read_operations:
        for error in errors:
            params.append((read_operation, error))

    return params

def validate_response_uri(response, expected_uri):
    request = response.get_response_headers()["_request"]
    assert request.url.startswith(expected_uri)

async def perform_write_operation(operation, container, fault_injection_container, doc_id, pk, expected_uri):
    doc = {'id': doc_id,
           'pk': pk,
           'name': 'sample document',
           'key': 'value'}
    if operation == "create":
        resp = await fault_injection_container.create_item(body=doc)
    elif operation == "upsert":
        resp = await fault_injection_container.upsert_item(body=doc)
    elif operation == "replace":
        await container.create_item(body=doc)
        new_doc = {'id': doc_id,
                   'pk': pk,
                   'name': 'sample document' + str(uuid),
                   'key': 'value'}
        resp = await fault_injection_container.replace_item(item=doc['id'], body=new_doc)
    elif operation == "delete":
        await container.create_item(body=doc)
        resp = await fault_injection_container.delete_item(item=doc['id'], partition_key=doc['pk'])
    elif operation == "patch":
        await container.create_item(body=doc)
        operations = [{"op": "incr", "path": "/company", "value": 3}]
        resp = await fault_injection_container.patch_item(item=doc['id'], partition_key=doc['pk'], patch_operations=operations)
    elif operation == "batch":
        batch_operations = [
            ("create", (doc, )),
            ("upsert", (doc,)),
            ("upsert", (doc,)),
            ("upsert", (doc,)),
        ]
        resp = await fault_injection_container.execute_item_batch(batch_operations, partition_key=doc['pk'])
    # this will need to be emulator only
    # elif operation == "delete_all_items_by_partition_key":
    #     await container.create_item(body=doc)
    #     await container.create_item(body=doc)
    #     await container.create_item(body=doc)
    #     resp = await fault_injection_container.delete_all_items_by_partition_key(pk)
    if resp:
        validate_response_uri(resp, expected_uri)

async def perform_read_operation(operation, container, doc_id, pk, expected_uri):
    if operation == "read":
        read_resp = await container.read_item(item=doc_id, partition_key=pk)
        request = read_resp.get_response_headers()["_request"]
        # Validate the response comes from "Read Region" (the most preferred read-only region)
        assert request.url.startswith(expected_uri)
    elif operation == "query_pk":
        # partition key filtered query
        query = "SELECT * FROM c WHERE c.id = @id AND c.pk = @pk"
        parameters = [{"name": "@id", "value": doc_id}, {"name": "@pk", "value": pk}]
        async for item in container.query_items(query=query, partition_key=pk, parameters=parameters):
            assert item['id'] == doc_id
        # need to do query with no pk and with feed range
    elif operation == "query":
        # cross partition query
        query = "SELECT * FROM c WHERE c.id = @id"
        async for item in container.query_items(query=query):
            assert item['id'] == doc_id
    elif operation == "changefeed":
        async for _ in container.query_items_change_feed():
            pass
    elif operation == "changefeed_pk":
        # partition key filtered change feed
        async for _ in container.query_items_change_feed(partition_key=pk):
            pass
    elif operation == "changefeed_epk":
        # partition key filtered by feed range
        feed_range = await container.feed_range_from_partition_key(partition_key=pk)
        async for _ in container.query_items_change_feed(feed_range=feed_range):
            pass
    elif operation == "read_all_items":
        async for item in container.read_all_items(partition_key=pk):
            assert item['pk'] == pk

def validate_unhealthy_partitions(global_endpoint_manager,
                                  expected_unhealthy_partitions):
    health_info_map = global_endpoint_manager.global_partition_endpoint_manager_core.partition_health_tracker.pk_range_wrapper_to_health_info
    unhealthy_partitions = 0
    for pk_range_wrapper, location_to_health_info in health_info_map.items():
        for location, health_info in location_to_health_info.items():
            health_status = health_info.unavailability_info.get(HEALTH_STATUS)
            if health_status == UNHEALTHY_TENTATIVE or health_status == UNHEALTHY:
                unhealthy_partitions += 1
            else:
                assert health_info.read_consecutive_failure_count < 10
                assert health_info.write_consecutive_failure_count < 5

    assert unhealthy_partitions == expected_unhealthy_partitions

async def cleanup_method(initialized_objects: List[Dict[str, Any]]):
    for obj in initialized_objects:
        method_client: CosmosClient = obj["client"]
        await method_client.close()

@pytest.mark.cosmosMultiRegion
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_teardown")
class TestPerPartitionCircuitBreakerMMAsync:
    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = os.path.basename(__file__) + str(uuid.uuid4())

    async def setup_method_with_custom_transport(self, custom_transport: AioHttpTransport, default_endpoint=host, **kwargs):
        client = CosmosClient(default_endpoint, self.master_key,
                              preferred_locations=[REGION_1, REGION_2],
                              multiple_write_locations=True,
                              transport=custom_transport, **kwargs)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_SINGLE_PARTITION_ID)
        return {"client": client, "db": db, "col": container}

    async def setup_method(self, default_endpoint=host, **kwargs):
        client = CosmosClient(default_endpoint, self.master_key,
                              preferred_locations=[REGION_1, REGION_2],
                              multiple_write_locations=True,
                              **kwargs)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_SINGLE_PARTITION_ID)
        return {"client": client, "db": db, "col": container}

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors())
    async def test_write_consecutive_failure_threshold_async(self, setup_teardown, write_operation, error):
        expected_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        custom_transport =  FaultInjectionTransportAsync()
        pk_value = "pk1"
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))
        custom_transport.add_fault(predicate, lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
            0,
            error
        )))

        custom_setup = await self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host)
        setup = await self.setup_method(default_endpoint=self.host)
        container = setup['col']
        fault_injection_container = custom_setup['col']
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        with pytest.raises((CosmosHttpResponseError, ServiceResponseError)) as exc_info:
            await perform_write_operation(write_operation,
                                          container,
                                          fault_injection_container,
                                          str(uuid.uuid4()),
                                          pk_value,
                                          expected_uri)
        assert exc_info.value == error

        validate_unhealthy_partitions(global_endpoint_manager, 0)

        # writes should fail but still be tracked
        for i in range(4):
            with pytest.raises((CosmosHttpResponseError, ServiceResponseError)) as exc_info:
                await perform_write_operation(write_operation,
                                              container,
                                              fault_injection_container,
                                              str(uuid.uuid4()),
                                              pk_value,
                                              expected_uri)
            assert exc_info.value == error

        # writes should now succeed because going to the other region
        await perform_write_operation(write_operation,
                                      container,
                                      fault_injection_container,
                                      str(uuid.uuid4()),
                                      pk_value,
                                      expected_uri)

        validate_unhealthy_partitions(global_endpoint_manager, 1)
        # remove faults and reduce initial recover time and perform a write
        original_val = _partition_health_tracker.INITIAL_UNAVAILABLE_TIME
        _partition_health_tracker.INITIAL_UNAVAILABLE_TIME = 1
        custom_transport.faults = []
        try:
            await perform_write_operation(write_operation,
                                          container,
                                          fault_injection_container,
                                          str(uuid.uuid4()),
                                          pk_value,
                                          uri_down)
        finally:
            _partition_health_tracker.INITIAL_UNAVAILABLE_TIME = original_val
        await cleanup_method([custom_setup, setup])



    @pytest.mark.parametrize("read_operation, error", read_operations_and_errors())
    async def test_read_consecutive_failure_threshold_async(self, setup_teardown, read_operation, error):
        expected_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        custom_transport =  FaultInjectionTransportAsync()
        id_value = str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': 'pk1',
                               'name': 'sample document',
                               'key': 'value'}
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))
        custom_transport.add_fault(predicate, lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
            0,
            error
        )))

        custom_setup = await self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host)
        fault_injection_container = custom_setup['col']
        setup = await self.setup_method(default_endpoint=self.host)
        container = setup['col']
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager
        
        # create a document to read
        await container.create_item(body=document_definition)

        # reads should fail over and only the relevant partition should be marked as unavailable
        await perform_read_operation(read_operation,
                                     fault_injection_container,
                                     document_definition['id'],
                                     document_definition['pk'],
                                     expected_uri)
        # partition should not have been marked unavailable after one error
        validate_unhealthy_partitions(global_endpoint_manager, 0)

        for i in range(10):
            await perform_read_operation(read_operation,
                                         fault_injection_container,
                                         document_definition['id'],
                                         document_definition['pk'],
                                         expected_uri)

        # the partition should have been marked as unavailable after breaking read threshold
        validate_unhealthy_partitions(global_endpoint_manager, 1)
        await cleanup_method([custom_setup, setup])

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors())
    async def test_write_failure_rate_threshold_async(self, setup_teardown, write_operation, error):
        expected_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        custom_transport = FaultInjectionTransportAsync()
        # two documents targeted to same partition, one will always fail and the other will succeed
        pk_value = "pk1"
        doc = {'id': str(uuid.uuid4()),
                 'pk': pk_value,
                 'name': 'sample document',
                 'key': 'value'}
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))
        custom_transport.add_fault(predicate,
                                   lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
                                       0,
                                       error
                                   )))

        custom_setup = await self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host)
        fault_injection_container = custom_setup['col']
        setup = await self.setup_method(default_endpoint=self.host)
        container = setup['col']
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager
        # lower minimum requests for testing
        _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 10
        os.environ["AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"] = "80"
        try:
            # writes should fail but still be tracked and mark unavailable a partition after crossing threshold
            for i in range(10):
                validate_unhealthy_partitions(global_endpoint_manager, 0)
                if i == 4 or i == 8:
                    # perform some successful creates to reset consecutive counter
                    # remove faults and perform a write
                    custom_transport.faults = []
                    await fault_injection_container.upsert_item(body=doc)
                    custom_transport.add_fault(predicate,
                                               lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
                                                   0,
                                                   error
                                               )))
                else:
                    with pytest.raises((CosmosHttpResponseError, ServiceResponseError)) as exc_info:
                        await perform_write_operation(write_operation,
                                                      container,
                                                      fault_injection_container,
                                                      str(uuid.uuid4()),
                                                      pk_value,
                                                      expected_uri)
                    assert exc_info.value == error

            validate_unhealthy_partitions(global_endpoint_manager, 1)

        finally:
            os.environ["AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"] = "90"
            # restore minimum requests
            _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100
        await cleanup_method([custom_setup, setup])

    @pytest.mark.parametrize("read_operation, error", read_operations_and_errors())
    async def test_read_failure_rate_threshold_async(self, setup_teardown, read_operation, error):
        expected_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        custom_transport = FaultInjectionTransportAsync()
        # two documents targeted to same partition, one will always fail and the other will succeed
        pk_value = "pk1"
        doc = {'id': str(uuid.uuid4()),
               'pk': pk_value,
               'name': 'sample document',
               'key': 'value'}
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))
        custom_transport.add_fault(predicate,
                                   lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
                                       0,
                                       error
                                   )))

        custom_setup = await self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host)
        fault_injection_container = custom_setup['col']
        setup = await self.setup_method(default_endpoint=self.host)
        container = setup['col']
        await container.upsert_item(body=doc)
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager
        # lower minimum requests for testing
        _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 8
        os.environ["AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"] = "80"
        try:
            if isinstance(error, ServiceResponseError):
                num_operations = 4
            else:
                num_operations = 8
            for i in range(num_operations):
                validate_unhealthy_partitions(global_endpoint_manager, 0)
                if i == 2:
                    # perform some successful read to reset consecutive counter
                    # remove faults and perform a read
                    custom_transport.faults = []
                    await fault_injection_container.read_item(item=doc["id"], partition_key=pk_value)
                    custom_transport.add_fault(predicate,
                                               lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
                                                   0,
                                                   error
                                               )))
                else:
                    # read will fail and retry in other region
                    await perform_read_operation(read_operation,
                                                  fault_injection_container,
                                                  doc['id'],
                                                  pk_value,
                                                  expected_uri)

            validate_unhealthy_partitions(global_endpoint_manager, 1)
        finally:
            os.environ["AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"] = "90"
            # restore minimum requests
            _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100
        await cleanup_method([custom_setup, setup])

        # look at the urls for verifying fall back and use another id for same partition

    # test_failure_rate_threshold - add service response error - across operation types - test recovering the partition again
    # test service request marks only a partition unavailable not an entire region - across operation types
    # test cosmos client timeout

if __name__ == '__main__':
    unittest.main()
