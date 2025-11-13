# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import asyncio
import os
import unittest
import uuid
from typing import Any, Union

import pytest
from azure.core.pipeline.transport._aiohttp import AioHttpTransport
from azure.core.exceptions import ServiceResponseError

import test_config
from azure.cosmos import _location_cache, _partition_health_tracker
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from _fault_injection_transport_async import FaultInjectionTransportAsync
from test_per_partition_circuit_breaker_mm import create_doc, read_operations_and_errors, \
    write_operations_and_errors, operations, REGION_1, REGION_2, CHANGE_FEED, CHANGE_FEED_PK, CHANGE_FEED_EPK, READ, \
    CREATE, READ_ALL_ITEMS, DELETE_ALL_ITEMS_BY_PARTITION_KEY, QUERY, QUERY_PK, BATCH, UPSERT, REPLACE, PATCH, DELETE, \
    PK_VALUE, validate_unhealthy_partitions, validate_response_uri, user_agent_hook
from test_per_partition_circuit_breaker_mm import validate_stats

COLLECTION = "created_collection"

async def perform_write_operation(operation, container, fault_injection_container, doc_id, pk, expected_uri=None):
    doc = {'id': doc_id,
           'pk': pk,
           'name': 'sample document',
           'key': 'value'}
    if operation == CREATE:
        resp = await fault_injection_container.create_item(body=doc)
    elif operation == UPSERT:
        resp = await fault_injection_container.upsert_item(body=doc)
    elif operation == REPLACE:
        await container.upsert_item(body=doc)
        new_doc = {'id': doc_id,
                   'pk': pk,
                   'name': 'sample document' + str(uuid),
                   'key': 'value'}
        await asyncio.sleep(1)
        resp = await fault_injection_container.replace_item(item=doc['id'], body=new_doc)
    elif operation == DELETE:
        await container.upsert_item(body=doc)
        await asyncio.sleep(1)
        resp = await fault_injection_container.delete_item(item=doc['id'], partition_key=doc['pk'])
    elif operation == PATCH:
        await container.upsert_item(body=doc)
        await asyncio.sleep(1)
        operations = [{"op": "incr", "path": "/company", "value": 3}]
        resp = await fault_injection_container.patch_item(item=doc['id'], partition_key=doc['pk'], patch_operations=operations)
    elif operation == BATCH:
        batch_operations = [
            ("create", (doc, )),
            ("upsert", (doc,)),
            ("upsert", (doc,)),
            ("upsert", (doc,)),
        ]
        resp = await fault_injection_container.execute_item_batch(batch_operations, partition_key=doc['pk'])
    # this will need to be emulator only
    elif operation == DELETE_ALL_ITEMS_BY_PARTITION_KEY:
        await container.upsert_item(body=doc)
        resp = await fault_injection_container.delete_all_items_by_partition_key(pk)
    if resp and expected_uri:
        validate_response_uri(resp, expected_uri)

async def perform_read_operation(operation, container, doc_id, pk, expected_uri):
    if operation == READ:
        read_resp = await container.read_item(item=doc_id, partition_key=pk)
        request = read_resp.get_response_headers()["_request"]
        # Validate the response comes from "Read Region" (the most preferred read-only region)
        assert request.url.startswith(expected_uri)
    elif operation == QUERY_PK:
        # partition key filtered query
        query = "SELECT * FROM c WHERE c.id = @id AND c.pk = @pk"
        parameters = [{"name": "@id", "value": doc_id}, {"name": "@pk", "value": pk}]
        async for item in container.query_items(query=query, partition_key=pk, parameters=parameters):
            assert item['id'] == doc_id
        # need to do query with no pk and with feed range
    elif operation == QUERY:
        # cross partition query
        query = "SELECT * FROM c WHERE c.id = @id"
        async for item in container.query_items(query=query):
            assert item['id'] == doc_id
    elif operation == CHANGE_FEED:
        async for _ in container.query_items_change_feed():
            pass
    elif operation == CHANGE_FEED_PK:
        # partition key filtered change feed
        async for _ in container.query_items_change_feed(partition_key=pk):
            pass
    elif operation == CHANGE_FEED_EPK:
        # partition key filtered by feed range
        feed_range = await container.feed_range_from_partition_key(partition_key=pk)
        async for _ in container.query_items_change_feed(feed_range=feed_range):
            pass
    elif operation == READ_ALL_ITEMS:
        async for _ in container.read_all_items():
            pass

async def cleanup_method(initialized_objects: list[dict[str, Any]]):
    for obj in initialized_objects:
        method_client: CosmosClient = obj["client"]
        await method_client.close()

@pytest.mark.cosmosCircuitBreaker
@pytest.mark.asyncio
class TestPerPartitionCircuitBreakerMMAsync:
    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_MULTI_PARTITION_ID = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID

    async def setup_method_with_custom_transport(self, custom_transport: Union[AioHttpTransport, Any], default_endpoint=host, **kwargs):
        container_id = kwargs.pop("container_id", None)
        if not container_id:
            container_id = self.TEST_CONTAINER_MULTI_PARTITION_ID
        client = CosmosClient(default_endpoint, self.master_key,
                              preferred_locations=[REGION_1, REGION_2],
                              multiple_write_locations=True,
                              transport=custom_transport, **kwargs)
        await client.__aenter__()
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(container_id)
        return {"client": client, "db": db, "col": container}

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors())
    async def test_write_consecutive_failure_threshold_async(self, write_operation, error):
        error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
            0,
            error
        ))
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = await self.setup_info(error_lambda)
        container = setup['col']
        fault_injection_container = custom_setup['col']
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        with pytest.raises((CosmosHttpResponseError, ServiceResponseError)) as exc_info:
            await perform_write_operation(write_operation,
                                          container,
                                          fault_injection_container,
                                          str(uuid.uuid4()),
                                          PK_VALUE,
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
                                              PK_VALUE,
                                              expected_uri)
            assert exc_info.value == error

        # writes should now succeed because going to the other region
        await perform_write_operation(write_operation,
                                      container,
                                      fault_injection_container,
                                      str(uuid.uuid4()),
                                      PK_VALUE,
                                      expected_uri)

        validate_unhealthy_partitions(global_endpoint_manager, 1)
        # remove faults and reduce initial recover time and perform a write
        original_unavailable_time = _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS
        _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS = 1
        custom_transport.faults = []
        try:
            await perform_write_operation(write_operation,
                                          container,
                                          fault_injection_container,
                                          str(uuid.uuid4()),
                                          PK_VALUE,
                                          uri_down)
        finally:
            _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS = original_unavailable_time
        validate_unhealthy_partitions(global_endpoint_manager, 0)
        await cleanup_method([custom_setup, setup])

    async def setup_info(self, error, **kwargs):
        expected_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        custom_transport = FaultInjectionTransportAsync()
        # two documents targeted to same partition, one will always fail and the other will succeed
        doc = create_doc()
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))
        custom_transport.add_fault(predicate,
                                   error)
        custom_setup = await self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host, **kwargs)
        setup = await self.setup_method_with_custom_transport(None, default_endpoint=self.host, **kwargs)
        return setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate


    @pytest.mark.cosmosCircuitBreakerMultiRegion
    @pytest.mark.parametrize("read_operation, error", read_operations_and_errors())
    async def test_read_consecutive_failure_threshold_async(self, read_operation, error):
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
            expected_unhealthy_partitions = 5
        else:
            expected_unhealthy_partitions = 1
        validate_unhealthy_partitions(global_endpoint_manager, expected_unhealthy_partitions)
        # remove faults and reduce initial recover time and perform a read
        original_unavailable_time = _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS
        _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS = 1
        custom_transport.faults = []
        try:
            await perform_read_operation(read_operation,
                                         fault_injection_container,
                                         doc['id'],
                                         doc['pk'],
                                         uri_down)
        finally:
            _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS = original_unavailable_time
        validate_unhealthy_partitions(global_endpoint_manager, 0)
        await cleanup_method([custom_setup, setup])

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors())
    async def test_write_failure_rate_threshold_async(self, write_operation, error):
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

            validate_unhealthy_partitions(global_endpoint_manager, 1)

        finally:
            os.environ["AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"] = "90"
            # restore minimum requests
            _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100
        await cleanup_method([custom_setup, setup])

    @pytest.mark.cosmosCircuitBreakerMultiRegion
    @pytest.mark.parametrize("read_operation, error", read_operations_and_errors())
    async def test_read_failure_rate_threshold_async(self, read_operation, error):
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
                expected_unhealthy_partitions = 5
            else:
                expected_unhealthy_partitions = 1

            validate_unhealthy_partitions(global_endpoint_manager, expected_unhealthy_partitions)
        finally:
            os.environ["AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"] = "90"
            # restore minimum requests
            _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100
        await cleanup_method([custom_setup, setup])

    async def test_stat_reset_async(self):
        status_code = 500
        error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
            0,
            CosmosHttpResponseError(
                status_code=status_code,
                message="Some injected error.")
        ))
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = \
            await self.setup_info(error_lambda, container_id=test_config.TestConfig.TEST_SINGLE_PARTITION_CONTAINER_ID)
        container = setup['col']
        fault_injection_container = custom_setup['col']
        await container.upsert_item(body=doc)
        await asyncio.sleep(1)
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager
        # lower refresh interval for testing
        _partition_health_tracker.REFRESH_INTERVAL_MS = 10 * 1000
        try:
            for i in range(2):
                validate_unhealthy_partitions(global_endpoint_manager, 0)
                # read will fail and retry in other region
                await perform_read_operation(READ,
                                             fault_injection_container,
                                             doc['id'],
                                             PK_VALUE,
                                             expected_uri)
                try:
                    await perform_write_operation(CREATE,
                                                  container,
                                                  fault_injection_container,
                                                  str(uuid.uuid4()),
                                                  PK_VALUE,
                                                  expected_uri)
                except CosmosHttpResponseError as e:
                    assert e.status_code == status_code
            validate_unhealthy_partitions(global_endpoint_manager, 0)
            validate_stats(global_endpoint_manager, 2, 2, 2, 2, 0, 0)
            await asyncio.sleep(25)
            await perform_read_operation(READ,
                                         fault_injection_container,
                                         doc['id'],
                                         PK_VALUE,
                                         expected_uri)

            validate_stats(global_endpoint_manager, 2, 3, 1, 0, 0, 0)
        finally:
            _partition_health_tracker.REFRESH_INTERVAL_MS = 60 * 1000
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

        validate_unhealthy_partitions(global_endpoint_manager, 0)
        assert len(global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint) == 1

        # recover partition
        # remove faults and reduce initial recover time and perform a read
        original_unavailable_time = _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS
        _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS = 1
        custom_transport.faults = []
        try:
            await perform_read_operation(read_operation,
                                         fault_injection_container,
                                         doc['id'],
                                         PK_VALUE,
                                         expected_uri)
        finally:
            _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS = original_unavailable_time
        validate_unhealthy_partitions(global_endpoint_manager, 0)
        # per partition circuit breaker should not regress connection timeouts marking the region as unavailable
        assert len(global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint) == 1

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
        assert len(global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint) == 1


        await cleanup_method([custom_setup, setup])


    # send 15 write concurrent requests when trying to recover
    # verify that only one failed
    async def test_recovering_only_fails_one_requests_async(self):
        error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
            0, CosmosHttpResponseError(
            status_code=502,
            message="Some envoy error.")))
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = await self.setup_info(error_lambda)
        fault_injection_container = custom_setup['col']
        for i in range(5):
            with pytest.raises(CosmosHttpResponseError):
                await fault_injection_container.create_item(body=doc)


        number_of_errors = 0

        async def concurrent_upsert():
            nonlocal number_of_errors
            doc = {'id': str(uuid.uuid4()),
                   'pk': PK_VALUE,
                   'name': 'sample document',
                   'key': 'value'}
            try:
                await fault_injection_container.upsert_item(doc)
            except CosmosHttpResponseError as e:
                number_of_errors += 1

        # attempt to recover partition
        original_unavailable_time = _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS
        _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS = 1
        try:
            tasks = []
            for i in range(15):
                tasks.append(concurrent_upsert())
            await asyncio.gather(*tasks)
            assert number_of_errors == 1
        finally:
            _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS = original_unavailable_time
            await cleanup_method([custom_setup, setup])

    async def test_circuit_breaker_user_agent_feature_flag_mm_async(self):
        # Simple test to verify the user agent suffix is being updated with the relevant feature flags
        custom_setup = await self.setup_method_with_custom_transport(None)
        container = custom_setup['col']
        # Create a document to check the response headers
        await container.upsert_item(body={'id': str(uuid.uuid4()), 'pk': PK_VALUE, 'name': 'sample document', 'key': 'value'},
                                              raw_response_hook=user_agent_hook)

if __name__ == '__main__':
    unittest.main()
