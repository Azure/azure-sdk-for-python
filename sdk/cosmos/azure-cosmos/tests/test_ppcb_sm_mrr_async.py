# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import asyncio
import os
import unittest
import uuid
from typing import Dict, Any

import pytest
import pytest_asyncio
from azure.core.pipeline.transport._aiohttp import AioHttpTransport
from azure.core.exceptions import ServiceResponseError

import test_config
from azure.cosmos import PartitionKey
from azure.cosmos._partition_health_tracker import HEALTH_STATUS, UNHEALTHY, UNHEALTHY_TENTATIVE
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from _fault_injection_transport_async import FaultInjectionTransportAsync

COLLECTION = "created_collection"
@pytest_asyncio.fixture()
async def setup():
    os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "True"
    client = CosmosClient(TestPerPartitionCircuitBreakerSmMrrAsync.host, TestPerPartitionCircuitBreakerSmMrrAsync.master_key, consistency_level="Session")
    created_database = client.get_database_client(TestPerPartitionCircuitBreakerSmMrrAsync.TEST_DATABASE_ID)
    await client.create_database_if_not_exists(TestPerPartitionCircuitBreakerSmMrrAsync.TEST_DATABASE_ID)
    created_collection = await created_database.create_container(TestPerPartitionCircuitBreakerSmMrrAsync.TEST_CONTAINER_SINGLE_PARTITION_ID,
                                                                 partition_key=PartitionKey("/pk"),
                                                                 offer_throughput=10000)
    yield {
        COLLECTION: created_collection
    }

    await created_database.delete_container(TestPerPartitionCircuitBreakerSmMrrAsync.TEST_CONTAINER_SINGLE_PARTITION_ID)
    await client.close()
    os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "False"

def operations_and_errors():
    write_operations = ["create", "upsert", "replace", "delete", "patch", "batch"]
    read_operations = ["read", "query", "changefeed"]
    errors = []
    error_codes = [408, 500, 502, 503]
    for error_code in error_codes:
        errors.append(CosmosHttpResponseError(
            status_code=error_code,
            message="Some injected error."))
    errors.append(ServiceResponseError(message="Injected Service Response Error."))
    params = []
    for write_operation in write_operations:
        for read_operation in read_operations:
            for error in errors:
                params.append((write_operation, read_operation, error))

    return params


@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup")
class TestPerPartitionCircuitBreakerSmMrrAsync:
    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = os.path.basename(__file__) + str(uuid.uuid4())

    async def setup_method_with_custom_transport(self, custom_transport: AioHttpTransport, default_endpoint=host, **kwargs):
        client = CosmosClient(default_endpoint, self.master_key, consistency_level="Session",
                              preferred_locations=["Write Region", "Read Region"],
                              transport=custom_transport, **kwargs)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_SINGLE_PARTITION_ID)
        return {"client": client, "db": db, "col": container}

    @staticmethod
    async def cleanup_method(initialized_objects: Dict[str, Any]):
        method_client: CosmosClient = initialized_objects["client"]
        await method_client.close()

    @staticmethod
    async def perform_write_operation(operation, container, doc_id, pk):
        doc = {'id': doc_id,
               'pk': pk,
               'name': 'sample document',
               'key': 'value'}
        if operation == "create":
            await container.create_item(body=doc)
        elif operation == "upsert":
            await container.upsert_item(body=doc)
        elif operation == "replace":
            new_doc = {'id': doc_id,
                       'pk': pk,
                       'name': 'sample document' + str(uuid),
                       'key': 'value'}
            await container.replace_item(item=doc['id'], body=new_doc)
        elif operation == "delete":
            await container.create_item(body=doc)
            await container.delete_item(item=doc['id'], partition_key=doc['pk'])
        elif operation == "patch":
            operations = [{"op": "incr", "path": "/company", "value": 3}]
            await container.patch_item(item=doc['id'], partition_key=doc['pk'], operations=operations)
        elif operation == "batch":
            batch_operations = [
                ("create", (doc, )),
                ("upsert", (doc,)),
                ("upsert", (doc,)),
                ("upsert", (doc,)),
            ]
            await container.execute_item_batch(batch_operations, partition_key=doc['pk'])

    @staticmethod
    async def perform_read_operation(operation, container, doc_id, pk, expected_read_region_uri):
        if operation == "read":
            read_resp = await container.read_item(item=doc_id, partition_key=pk)
            request = read_resp.get_response_headers()["_request"]
            # Validate the response comes from "Read Region" (the most preferred read-only region)
            assert request.url.startswith(expected_read_region_uri)
        elif operation == "query":
            query = "SELECT * FROM c WHERE c.id = @id AND c.pk = @pk"
            parameters = [{"name": "@id", "value": doc_id}, {"name": "@pk", "value": pk}]
            async for _ in container.query_items(query=query, parameters=parameters):
                pass
        elif operation == "changefeed":
            async for _ in container.query_items_change_feed():
                pass


    async def create_custom_transport_sm_mrr(self):
        custom_transport =  FaultInjectionTransportAsync()
        # Inject rule to disallow writes in the read-only region
        is_write_operation_in_read_region_predicate = lambda \
                r: FaultInjectionTransportAsync.predicate_is_write_operation(r, self.host)

        custom_transport.add_fault(
            is_write_operation_in_read_region_predicate,
            lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_write_forbidden()))

        # Inject topology transformation that would make Emulator look like a single write region
        # account with two read regions
        is_get_account_predicate = lambda r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
        emulator_as_multi_region_sm_account_transformation = \
            lambda r, inner: FaultInjectionTransportAsync.transform_topology_swr_mrr(
                write_region_name="Write Region",
                read_region_name="Read Region",
                inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            emulator_as_multi_region_sm_account_transformation)
        return custom_transport

    @pytest.mark.parametrize("write_operation, read_operation, error", operations_and_errors())
    async def test_consecutive_failure_threshold_async(self, setup, write_operation, read_operation, error):
        expected_read_region_uri = self.host
        expected_write_region_uri = expected_read_region_uri.replace("localhost", "127.0.0.1")
        custom_transport = await self.create_custom_transport_sm_mrr()
        id_value = 'failoverDoc-' + str(uuid.uuid4())
        document_definition = {'id': id_value,
                               'pk': 'pk1',
                               'name': 'sample document',
                               'key': 'value'}
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_req_for_document_with_id(r, id_value) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, expected_write_region_uri))
        custom_transport.add_fault(predicate, lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
            0,
            error
        )))

        custom_setup = await self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host)
        container = custom_setup['col']

        # writes should fail in sm mrr with circuit breaker and should not mark unavailable a partition
        for i in range(6):
            with pytest.raises((CosmosHttpResponseError, ServiceResponseError)):
                await TestPerPartitionCircuitBreakerSmMrrAsync.perform_write_operation(write_operation,
                                                                                       container,
                                                                                       document_definition['id'],
                                                                                       document_definition['pk'])
        global_endpoint_manager = container.client_connection._global_endpoint_manager

        TestPerPartitionCircuitBreakerSmMrrAsync.validate_unhealthy_partitions(global_endpoint_manager, 0)

        # create item with client without fault injection
        await setup[COLLECTION].create_item(body=document_definition)

        # reads should fail over and only the relevant partition should be marked as unavailable
        await TestPerPartitionCircuitBreakerSmMrrAsync.perform_read_operation(read_operation,
                                                                              container,
                                                                              document_definition['id'],
                                                                              document_definition['pk'],
                                                                              expected_read_region_uri)
        # partition should not have been marked unavailable after one error
        TestPerPartitionCircuitBreakerSmMrrAsync.validate_unhealthy_partitions(global_endpoint_manager, 0)

        for i in range(10):
            await TestPerPartitionCircuitBreakerSmMrrAsync.perform_read_operation(read_operation,
                                                                                  container,
                                                                                  document_definition['id'],
                                                                                  document_definition['pk'],
                                                                                  expected_read_region_uri)

       # the partition should have been marked as unavailable after breaking read threshold
        TestPerPartitionCircuitBreakerSmMrrAsync.validate_unhealthy_partitions(global_endpoint_manager, 1)

    @pytest.mark.parametrize("write_operation, read_operation, error", operations_and_errors())
    async def test_failure_rate_threshold_async(self, setup, write_operation, read_operation, error):
        expected_read_region_uri = self.host
        expected_write_region_uri = expected_read_region_uri.replace("localhost", "127.0.0.1")
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
                    await TestPerPartitionCircuitBreakerSmMrrAsync.perform_write_operation(write_operation,
                                                                                           container,
                                                                                           document_definition['id'],
                                                                                           document_definition['pk'])

            TestPerPartitionCircuitBreakerSmMrrAsync.validate_unhealthy_partitions(global_endpoint_manager, 0)

            # create item with client without fault injection
            await setup[COLLECTION].create_item(body=document_definition)

            # reads should fail over and only the relevant partition should be marked as unavailable
            await container.read_item(item=document_definition['id'], partition_key=document_definition['pk'])
            # partition should not have been marked unavailable after one error
            TestPerPartitionCircuitBreakerSmMrrAsync.validate_unhealthy_partitions(global_endpoint_manager, 0)
            for i in range(20):
                if i == 8:
                    read_resp = await container.read_item(item=doc_2['id'],
                                                          partition_key=doc_2['pk'])
                    request = read_resp.get_response_headers()["_request"]
                    # Validate the response comes from "Read Region" (the most preferred read-only region)
                    assert request.url.startswith(expected_read_region_uri)
                else:
                    await TestPerPartitionCircuitBreakerSmMrrAsync.perform_read_operation(read_operation,
                                                                                          container,
                                                                                          document_definition['id'],
                                                                                          document_definition['pk'],
                                                                                          expected_read_region_uri)
            # the partition should have been marked as unavailable after breaking read threshold
            TestPerPartitionCircuitBreakerSmMrrAsync.validate_unhealthy_partitions(global_endpoint_manager, 1)
        finally:
            # restore minimum requests
            global_endpoint_manager.global_partition_endpoint_manager_core.partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100

        # look at the urls for verifying fall back

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
                    assert health_info.write_failure_count == 0
                    assert health_info.write_consecutive_failure_count == 0

        assert unhealthy_partitions == expected_unhealthy_partitions

    # test_failure_rate_threshold - add service response error - across operation types - test recovering the partition again
    # test service request marks only a partition unavailable not an entire region - across operation types
    # test cosmos client timeout

if __name__ == '__main__':
    unittest.main()
