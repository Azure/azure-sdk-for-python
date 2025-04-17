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
from azure.cosmos import PartitionKey, _location_cache
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
    read_operations = ["read", "query", "changefeed", "read_all_items"]
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
    validate_response_uri(resp, expected_uri)


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

    @staticmethod
    async def cleanup_method(initialized_objects: List[Dict[str, Any]]):
        for obj in initialized_objects:
            method_client: CosmosClient = obj["client"]
            await method_client.close()

    @staticmethod
    async def perform_read_operation(operation, container, doc_id, pk, expected_uri):
        if operation == "read":
            read_resp = await container.read_item(item=doc_id, partition_key=pk)
            request = read_resp.get_response_headers()["_request"]
            # Validate the response comes from "Read Region" (the most preferred read-only region)
            assert request.url.startswith(expected_uri)
        elif operation == "query":
            query = "SELECT * FROM c WHERE c.id = @id AND c.pk = @pk"
            parameters = [{"name": "@id", "value": doc_id}, {"name": "@pk", "value": pk}]
            async for item in container.query_items(query=query, partition_key=pk, parameters=parameters):
                assert item['id'] == doc_id
            # need to do query with no pk and with feed range
        elif operation == "changefeed":
            async for _ in container.query_items_change_feed():
                pass
        elif operation == "read_all_items":
            async for item in container.read_all_items(partition_key=pk):
                assert item['pk'] == pk


    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors())
    async def test_write_consecutive_failure_threshold_async(self, setup_teardown, write_operation, error):
        expected_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        custom_transport =  FaultInjectionTransportAsync()
        id_value = 'failoverDoc-' + str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': 'pk1'}
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
                                          document_definition['id'],
                                          document_definition['pk'],
                                          expected_uri)
        assert exc_info.value == error

        TestPerPartitionCircuitBreakerMMAsync.validate_unhealthy_partitions(global_endpoint_manager, 0)

        # writes should fail but still be tracked
        for i in range(4):
            with pytest.raises((CosmosHttpResponseError, ServiceResponseError)):
                await perform_write_operation(write_operation,
                                              container,
                                              fault_injection_container,
                                              document_definition['id'],
                                              document_definition['pk'],
                                              expected_uri)

        await perform_write_operation(write_operation,
                                      container,
                                      fault_injection_container,
                                      document_definition['id'],
                                      document_definition['pk'],
                                      expected_uri)
        TestPerPartitionCircuitBreakerMMAsync.validate_unhealthy_partitions(global_endpoint_manager, 1)
        await TestPerPartitionCircuitBreakerMMAsync.cleanup_method([custom_setup, setup])

    @pytest.mark.parametrize("read_operation, error", read_operations_and_errors())
    async def test_read_consecutive_failure_threshold_async(self, setup_teardown, read_operation, error):
        expected_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        custom_transport =  FaultInjectionTransportAsync()
        id_value = 'failoverDoc-' + str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': 'pk1',
                               'name': 'sample document',
                               'key': 'value'}
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, expected_uri))
        custom_transport.add_fault(predicate, lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
            0,
            error
        )))

        custom_setup = await self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host)
        container = custom_setup['col']
        global_endpoint_manager = container.client_connection._global_endpoint_manager


        await TestPerPartitionCircuitBreakerMMAsync.perform_write_operation(write_operation,
                                                                            setup_teardown[COLLECTION],
                                                                            container,
                                                                            document_definition['id'],
                                                                            document_definition['pk'],
                                                                            expected_uri)

        # writes should fail in sm mrr with circuit breaker and should not mark unavailable a partition
        for i in range(6):
            with pytest.raises((CosmosHttpResponseError, ServiceResponseError)):
                await TestPerPartitionCircuitBreakerMMAsync.perform_write_operation(write_operation,
                                                                                    setup_teardown[COLLECTION],
                                                                                    container,
                                                                                    document_definition['id'],
                                                                                    document_definition['pk'],
                                                                                    expected_uri)

        TestPerPartitionCircuitBreakerMMAsync.validate_unhealthy_partitions(global_endpoint_manager, 1)

        # create item with client without fault injection
        await setup_teardown[COLLECTION].create_item(body=document_definition)

        # reads should fail over and only the relevant partition should be marked as unavailable
        await TestPerPartitionCircuitBreakerMMAsync.perform_read_operation(read_operation,
                                                                           container,
                                                                           document_definition['id'],
                                                                           document_definition['pk'],
                                                                           expected_uri)
        # partition should not have been marked unavailable after one error
        TestPerPartitionCircuitBreakerMMAsync.validate_unhealthy_partitions(global_endpoint_manager, 1)

        for i in range(10):
            await TestPerPartitionCircuitBreakerMMAsync.perform_read_operation(read_operation,
                                                                               container,
                                                                               document_definition['id'],
                                                                               document_definition['pk'],
                                                                               expected_uri)

        # the partition should have been marked as unavailable after breaking read threshold
        TestPerPartitionCircuitBreakerMMAsync.validate_unhealthy_partitions(global_endpoint_manager, 1)
        # test recovering the partition again

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors())
    async def test_failure_rate_threshold_async(self, setup_teardown, write_operation, error):
        expected_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        custom_transport = await self.create_custom_transport_sm_mrr()
        id_value = 'failoverDoc-' + str(uuid.uuid4())
        # two documents targeted to same partition, one will always fail and the other will succeed
        document_definition = {'id': id_value,
                               'pk': 'pk1',
                               'name': 'sample document',
                               'key': 'value'}
        doc_2 = {'id': str(uuid.uuid4()),
                 'pk': 'pk1',
                 'name': 'sample document',
                 'key': 'value'}
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_req_for_document_with_id(r, id_value) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, expected_write_region_uri))
        custom_transport.add_fault(predicate,
                                   lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
                                       0,
                                       error
                                   )))

        custom_setup = await self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host)
        container = custom_setup['col']
        global_endpoint_manager = container.client_connection._global_endpoint_manager
        # lower minimum requests for testing
        global_endpoint_manager.global_partition_endpoint_manager_core.partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 10
        try:
            # writes should fail in sm mrr with circuit breaker and should not mark unavailable a partition
            for i in range(14):
                if i == 9:
                    await container.upsert_item(body=doc_2)
                with pytest.raises((CosmosHttpResponseError, ServiceResponseError)):
                    await TestPerPartitionCircuitBreakerMMAsync.perform_write_operation(write_operation,
                                                                                        setup_teardown[COLLECTION],
                                                                                        container,
                                                                                        document_definition['id'],
                                                                                        document_definition['pk'],
                                                                                        expected_uri)

            TestPerPartitionCircuitBreakerMMAsync.validate_unhealthy_partitions(global_endpoint_manager, 0)

            # create item with client without fault injection
            await setup_teardown[COLLECTION].create_item(body=document_definition)
        finally:
            # restore minimum requests
            global_endpoint_manager.global_partition_endpoint_manager_core.partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100



    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors())
    async def test_read_failure_rate_threshold_async(self, setup_teardown, write_operation, error):
        expected_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        custom_transport = await self.create_custom_transport_sm_mrr()
        id_value = 'failoverDoc-' + str(uuid.uuid4())
        # two documents targeted to same partition, one will always fail and the other will succeed
        document_definition = {'id': id_value,
                               'pk': 'pk1',
                               'name': 'sample document',
                               'key': 'value'}
        doc_2 = {'id': str(uuid.uuid4()),
                 'pk': 'pk1',
                 'name': 'sample document',
                 'key': 'value'}
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_req_for_document_with_id(r, id_value) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, expected_write_region_uri))
        custom_transport.add_fault(predicate,
                                   lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
                                       0,
                                       error
                                   )))

        custom_setup = await self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host)
        container = custom_setup['col']
        global_endpoint_manager = container.client_connection._global_endpoint_manager
        # lower minimum requests for testing
        global_endpoint_manager.global_partition_endpoint_manager_core.partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 10
        try:
            # writes should fail in sm mrr with circuit breaker and should not mark unavailable a partition
            for i in range(14):
                if i == 9:
                    await container.upsert_item(body=doc_2)
                with pytest.raises((CosmosHttpResponseError, ServiceResponseError)):
                    await TestPerPartitionCircuitBreakerMMAsync.perform_write_operation(write_operation,
                                                                                        setup_teardown[COLLECTION],
                                                                                        container,
                                                                                        document_definition['id'],
                                                                                        document_definition['pk'],
                                                                                        expected_uri)

            TestPerPartitionCircuitBreakerMMAsync.validate_unhealthy_partitions(global_endpoint_manager, 0)

            # create item with client without fault injection
            await setup_teardown[COLLECTION].create_item(body=document_definition)

            # reads should fail over and only the relevant partition should be marked as unavailable
            await container.read_item(item=document_definition['id'], partition_key=document_definition['pk'])
            # partition should not have been marked unavailable after one error
            TestPerPartitionCircuitBreakerMMAsync.validate_unhealthy_partitions(global_endpoint_manager, 0)
            for i in range(20):
                if i == 8:
                    read_resp = await container.read_item(item=doc_2['id'],
                                                          partition_key=doc_2['pk'])
                    request = read_resp.get_response_headers()["_request"]
                    # Validate the response comes from "Read Region" (the most preferred read-only region)
                    assert request.url.startswith(expected_uri)
                else:
                    await TestPerPartitionCircuitBreakerMMAsync.perform_read_operation(read_operation,
                                                                                       container,
                                                                                       document_definition['id'],
                                                                                       document_definition['pk'],
                                                                                       expected_uri)
            # the partition should have been marked as unavailable after breaking read threshold
            TestPerPartitionCircuitBreakerMMAsync.validate_unhealthy_partitions(global_endpoint_manager, 1)
        finally:
            # restore minimum requests
            global_endpoint_manager.global_partition_endpoint_manager_core.partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100

        # look at the urls for verifying fall back and use another id for same partition

    @staticmethod
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

    # test_failure_rate_threshold - add service response error - across operation types - test recovering the partition again
    # test service request marks only a partition unavailable not an entire region - across operation types
    # test cosmos client timeout

if __name__ == '__main__':
    unittest.main()
