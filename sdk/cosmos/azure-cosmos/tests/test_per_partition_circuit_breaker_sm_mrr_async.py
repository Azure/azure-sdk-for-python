# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import asyncio
import logging
import os
import unittest
import uuid
from typing import Dict, Any

import pytest
import pytest_asyncio
from azure.core.pipeline.transport._aiohttp import AioHttpTransport
from azure.core.exceptions import ServiceResponseError

import test_config
from azure.cosmos import PartitionKey, _partition_health_tracker, _location_cache
from azure.cosmos._partition_health_tracker import UNHEALTHY_TENTATIVE, UNHEALTHY, HEALTH_STATUS
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from _fault_injection_transport_async import FaultInjectionTransportAsync
from test_per_partition_circuit_breaker_mm_async import perform_write_operation, create_doc, PK_VALUE, \
    write_operations_and_errors, \
    cleanup_method, read_operations_and_errors, perform_read_operation, CHANGE_FEED, QUERY, READ_ALL_ITEMS, operations, \
    REGION_2, REGION_1

COLLECTION = "created_collection"
logger = logging.getLogger('test')
@pytest_asyncio.fixture(scope="class", autouse=True)
async def setup_teardown():
    logger.info(os.getenv("AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"))
    client = CosmosClient(TestPerPartitionCircuitBreakerSmMrrAsync.host, TestPerPartitionCircuitBreakerSmMrrAsync.master_key)
    created_database = client.get_database_client(TestPerPartitionCircuitBreakerSmMrrAsync.TEST_DATABASE_ID)
    await created_database.create_container(TestPerPartitionCircuitBreakerSmMrrAsync.TEST_CONTAINER_SINGLE_PARTITION_ID,
                                                                 partition_key=PartitionKey("/pk"),
                                                                 offer_throughput=10000)
    # allow some time for the container to be created as this method is in different event loop
    await asyncio.sleep(3)
    yield
    await created_database.delete_container(TestPerPartitionCircuitBreakerSmMrrAsync.TEST_CONTAINER_SINGLE_PARTITION_ID)
    await client.close()

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
            # single region write account should never track write failures
            assert health_info.write_failure_count == 0
            assert health_info.write_consecutive_failure_count == 0

    assert unhealthy_partitions == expected_unhealthy_partitions


@pytest.mark.cosmosCircuitBreakerMultiRegion
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_teardown")
class TestPerPartitionCircuitBreakerSmMrrAsync:
    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = os.path.basename(__file__) + str(uuid.uuid4())

    async def setup_method_with_custom_transport(self, custom_transport: AioHttpTransport, default_endpoint=host, **kwargs):
        client = CosmosClient(default_endpoint, self.master_key, consistency_level="Session",
                              preferred_locations=[REGION_1, REGION_2],
                              transport=custom_transport, **kwargs)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_SINGLE_PARTITION_ID)
        return {"client": client, "db": db, "col": container}

    @staticmethod
    async def cleanup_method(initialized_objects: Dict[str, Any]):
        method_client: CosmosClient = initialized_objects["client"]
        await method_client.close()

    async def setup_info(self, error):
        expected_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        custom_transport = FaultInjectionTransportAsync()
        # two documents targeted to same partition, one will always fail and the other will succeed
        doc = create_doc()
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))
        custom_transport.add_fault(predicate,
                                   error)
        custom_setup = await self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host)
        setup = await self.setup_method_with_custom_transport(None, default_endpoint=self.host)
        return setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors())
    async def test_write_consecutive_failure_threshold_async(self, setup_teardown, write_operation, error):
        error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
            0,
            error
        ))
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = await self.setup_info(error_lambda)
        container = setup['col']
        fault_injection_container = custom_setup['col']
        global_endpoint_manager = container.client_connection._global_endpoint_manager

        # writes should fail in sm mrr with circuit breaker and should not mark unavailable a partition
        for i in range(6):
            validate_unhealthy_partitions(global_endpoint_manager, 0)
            with pytest.raises((CosmosHttpResponseError, ServiceResponseError)):
                await perform_write_operation(
                    write_operation,
                    container,
                    fault_injection_container,
                    str(uuid.uuid4()),
                    PK_VALUE,
                    expected_uri,
                )

        validate_unhealthy_partitions(global_endpoint_manager, 0)
        await cleanup_method([custom_setup, setup])


    @pytest.mark.parametrize("read_operation, error", read_operations_and_errors())
    async def test_read_consecutive_failure_threshold_async(self, setup_teardown, read_operation, error):
        error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
            0,
            error
        ))
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = await self.setup_info(error_lambda)
        container = setup['col']
        fault_injection_container = custom_setup['col']

        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        # create a document to read
        await container.create_item(body=doc)

        # reads should fail over and only the relevant partition should be marked as unavailable
        await perform_read_operation(read_operation,
                                     fault_injection_container,
                                     doc['id'],
                                     doc['pk'],
                                     expected_uri)
        # partition should not have been marked unavailable after one error
        validate_unhealthy_partitions(global_endpoint_manager, 0)

        for i in range(10):
            await perform_read_operation(read_operation,
                                         fault_injection_container,
                                         doc['id'],
                                         doc['pk'],
                                         expected_uri)

        # the partition should have been marked as unavailable after breaking read threshold
        if read_operation in (CHANGE_FEED, QUERY, READ_ALL_ITEMS):
            # these operations are cross partition so they would mark both partitions as unavailable
            expected_unhealthy_partitions = 2
        else:
            expected_unhealthy_partitions = 1
        validate_unhealthy_partitions(global_endpoint_manager, expected_unhealthy_partitions)
        # remove faults and reduce initial recover time and perform a read
        original_unavailable_time = _partition_health_tracker.INITIAL_UNAVAILABLE_TIME
        _partition_health_tracker.INITIAL_UNAVAILABLE_TIME = 1
        custom_transport.faults = []
        try:
            await perform_read_operation(read_operation,
                                         fault_injection_container,
                                         doc['id'],
                                         doc['pk'],
                                         uri_down)
        finally:
            _partition_health_tracker.INITIAL_UNAVAILABLE_TIME = original_unavailable_time
        validate_unhealthy_partitions(global_endpoint_manager, 0)
        await cleanup_method([custom_setup, setup])

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors())
    async def test_write_failure_rate_threshold_async(self, setup_teardown, write_operation, error):
        error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
            0,
            error
        ))
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = await self.setup_info(error_lambda)
        container = setup['col']
        fault_injection_container = custom_setup['col']
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
                                                      PK_VALUE,
                                                      expected_uri)
                    assert exc_info.value == error

            validate_unhealthy_partitions(global_endpoint_manager, 0)

        finally:
            os.environ["AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"] = "90"
            # restore minimum requests
            _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100
        await cleanup_method([custom_setup, setup])

    @pytest.mark.parametrize("read_operation, error", read_operations_and_errors())
    async def test_read_failure_rate_threshold_async(self, setup_teardown, read_operation, error):
        error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
            0,
            error
        ))
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = await self.setup_info(error_lambda)
        container = setup['col']
        fault_injection_container = custom_setup['col']
        await container.upsert_item(body=doc)
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager
        # lower minimum requests for testing
        _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 8
        os.environ["AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"] = "80"
        try:
            if isinstance(error, ServiceResponseError):
                # service response error retries in region 3 additional times before failing over
                num_operations = 2
            else:
                num_operations = 8
            for i in range(num_operations):
                validate_unhealthy_partitions(global_endpoint_manager, 0)
                # read will fail and retry in other region
                await perform_read_operation(read_operation,
                                             fault_injection_container,
                                             doc['id'],
                                             PK_VALUE,
                                             expected_uri)
            if read_operation in (CHANGE_FEED, QUERY, READ_ALL_ITEMS):
                # these operations are cross partition so they would mark both partitions as unavailable
                expected_unhealthy_partitions = 2
            else:
                expected_unhealthy_partitions = 1

            validate_unhealthy_partitions(global_endpoint_manager, expected_unhealthy_partitions)
        finally:
            os.environ["AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"] = "90"
            # restore minimum requests
            _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100
        await cleanup_method([custom_setup, setup])


    @pytest.mark.parametrize("read_operation, write_operation", operations())
    async def test_service_request_error_async(self, read_operation, write_operation):
        # the region should be tried 4 times before failing over and mark the partition as unavailable
        # the region should not be marked as unavailable
        error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_region_down())
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = await self.setup_info(error_lambda)
        container = setup['col']
        fault_injection_container = custom_setup['col']
        await container.upsert_item(body=doc)
        await perform_read_operation(read_operation,
                                     fault_injection_container,
                                     doc['id'],
                                     PK_VALUE,
                                     expected_uri)
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        validate_unhealthy_partitions(global_endpoint_manager, 1)
        # there shouldn't be region marked as unavailable
        assert len(global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint) == 0

        # recover partition
        # remove faults and reduce initial recover time and perform a write
        original_unavailable_time = _partition_health_tracker.INITIAL_UNAVAILABLE_TIME
        _partition_health_tracker.INITIAL_UNAVAILABLE_TIME = 1
        custom_transport.faults = []
        try:
            await perform_read_operation(read_operation,
                                         fault_injection_container,
                                         doc['id'],
                                         PK_VALUE,
                                         uri_down)
        finally:
            _partition_health_tracker.INITIAL_UNAVAILABLE_TIME = original_unavailable_time
        validate_unhealthy_partitions(global_endpoint_manager, 0)

        custom_transport.add_fault(predicate,
                                   lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_region_down()))

        await perform_write_operation(write_operation,
                                      container,
                                      fault_injection_container,
                                      str(uuid.uuid4()),
                                      PK_VALUE,
                                      expected_uri)
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        validate_unhealthy_partitions(global_endpoint_manager, 0)
        # there shouldn't be region marked as unavailable
        assert len(global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint) == 1
        await cleanup_method([custom_setup, setup])

    # test cosmos client timeout

if __name__ == '__main__':
    unittest.main()
