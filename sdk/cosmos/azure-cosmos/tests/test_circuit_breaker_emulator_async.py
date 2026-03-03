# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import asyncio
import os
import unittest
import uuid

import pytest
import pytest_asyncio
from azure.core.exceptions import ServiceResponseError
from azure.cosmos._request_object import RequestObject

import test_config
from azure.cosmos import _partition_health_tracker, documents
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.http_constants import ResourceType, HttpHeaders
from test_per_partition_circuit_breaker_mm_async import (perform_write_operation, cleanup_method)
from test_per_partition_circuit_breaker_mm import create_doc, DELETE_ALL_ITEMS_BY_PARTITION_KEY, PK_VALUE, \
    create_errors, validate_unhealthy_partitions as validate_unhealthy_partitions_mm
from test_per_partition_circuit_breaker_sm_mrr import \
    validate_unhealthy_partitions as validate_unhealthy_partitions_sm_mrr
from _fault_injection_transport_async import FaultInjectionTransportAsync

COLLECTION = "created_collection"
@pytest_asyncio.fixture(scope="class", autouse=True)
async def setup_teardown():
    os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "True"
    yield
    os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "False"

async def create_custom_transport_mm():
    custom_transport = FaultInjectionTransportAsync()
    is_get_account_predicate = lambda r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
    emulator_as_multi_write_region_account_transformation = \
        lambda r, inner: FaultInjectionTransportAsync.transform_topology_mwr(
            first_region_name="Write Region",
            second_region_name="Read Region",
            inner=inner)
    custom_transport.add_response_transformation(
        is_get_account_predicate,
        emulator_as_multi_write_region_account_transformation)
    return custom_transport


@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
@pytest.mark.usefixtures("setup_teardown")
class TestCircuitBreakerEmulatorAsync:
    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID

    async def setup_method_with_custom_transport(self, custom_transport, default_endpoint=host, **kwargs):
        client = CosmosClient(default_endpoint, self.master_key, consistency_level="Session",
                              preferred_locations=["Write Region", "Read Region"],
                              transport=custom_transport, **kwargs)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_SINGLE_PARTITION_ID)
        return {"client": client, "db": db, "col": container}


    async def create_custom_transport_sm_mrr(self):
        custom_transport =  FaultInjectionTransportAsync()
        # Inject rule to disallow writes in the read-only region
        is_write_operation_in_read_region_predicate = lambda \
                r: FaultInjectionTransportAsync.predicate_is_write_operation(r, self.host)

        custom_transport.add_fault(
            is_write_operation_in_read_region_predicate,
            lambda r: FaultInjectionTransportAsync.error_write_forbidden())

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

    async def setup_info(self, error=None, mm=False):
        expected_uri = self.host
        uri_down = self.host.replace("localhost", "127.0.0.1")
        custom_transport = await create_custom_transport_mm() if mm else await self.create_custom_transport_sm_mrr()
        # two documents targeted to same partition, one will always fail and the other will succeed
        doc = create_doc()
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_resource_type(r, ResourceType.Collection) and
                               FaultInjectionTransportAsync.predicate_is_operation_type(r, documents._OperationType.Delete) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))
        if error is not None:
            custom_transport.add_fault(predicate, error)
        custom_setup = await self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host, multiple_write_locations=mm)
        setup = await self.setup_method_with_custom_transport(None, default_endpoint=self.host, multiple_write_locations=mm)
        return setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate

    async def test_pk_range_wrapper_async(self):
        _, _, _, _, custom_setup, _, _ = await self.setup_info()
        container = custom_setup['col']
        prop = await container.read()
        headers = {HttpHeaders.IntendedCollectionRID: prop['_rid']}
        # check request with partition key flow
        request = RequestObject(
            ResourceType.Document,
            documents._OperationType.Create,
            headers,
            "pk-8584",
        )
        pk_range_wrapper = await container.client_connection._global_endpoint_manager.create_pk_range_wrapper(request)
        assert pk_range_wrapper.partition_key_range.max == "33333333333333333333333333333330"
        assert pk_range_wrapper.partition_key_range.min == "26666666666666666666666666666664"

        # check request with partition key range id flow
        headers[HttpHeaders.PartitionKeyRangeID] = '0'
        request = RequestObject(
            ResourceType.Document,
            documents._OperationType.Create,
            headers,
            None,
        )
        pk_range_wrapper = await container.client_connection._global_endpoint_manager.create_pk_range_wrapper(request)
        assert pk_range_wrapper.partition_key_range.max == "0CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC"
        assert pk_range_wrapper.partition_key_range.min == ""
        await cleanup_method([custom_setup])

    @pytest.mark.parametrize("error", create_errors())
    async def test_write_consecutive_failure_threshold_delete_all_items_by_pk_sm_async(self, setup_teardown, error):
        error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(0, error))
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = await self.setup_info(error_lambda)
        fault_injection_container = custom_setup['col']
        container = setup['col']
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        # writes should fail in sm mrr with circuit breaker and should not mark unavailable a partition
        for i in range(6):
            validate_unhealthy_partitions_sm_mrr(global_endpoint_manager, 0)
            with pytest.raises((CosmosHttpResponseError, ServiceResponseError)):
                await perform_write_operation(
                    DELETE_ALL_ITEMS_BY_PARTITION_KEY,
                    container,
                    fault_injection_container,
                    str(uuid.uuid4()),
                    PK_VALUE,
                    expected_uri,
                )

        validate_unhealthy_partitions_sm_mrr(global_endpoint_manager, 0)
        await cleanup_method([custom_setup, setup])


    @pytest.mark.parametrize("error", create_errors())
    async def test_write_consecutive_failure_threshold_delete_all_items_by_pk_mm_async(self, setup_teardown, error):
        if hasattr(error, "status_code") and error.status_code == 503:
            pytest.skip("ServiceUnavailableError will do a cross-region retry, so it has to be special cased.")
        error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(0, error))
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = await self.setup_info(error_lambda, mm=True)
        fault_injection_container = custom_setup['col']
        container = setup['col']
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        with pytest.raises((CosmosHttpResponseError, ServiceResponseError)) as exc_info:
            await perform_write_operation(DELETE_ALL_ITEMS_BY_PARTITION_KEY,
                                    container,
                                    fault_injection_container,
                                    str(uuid.uuid4()),
                                    PK_VALUE,
                                    expected_uri)
        assert exc_info.value == error

        validate_unhealthy_partitions_mm(global_endpoint_manager, 0)

        # writes should fail but still be tracked
        for i in range(4):
            with pytest.raises((CosmosHttpResponseError, ServiceResponseError)) as exc_info:
                await perform_write_operation(DELETE_ALL_ITEMS_BY_PARTITION_KEY,
                                        container,
                                        fault_injection_container,
                                        str(uuid.uuid4()),
                                        PK_VALUE,
                                        expected_uri)
            assert exc_info.value == error

        # writes should now succeed because going to the other region
        await perform_write_operation(DELETE_ALL_ITEMS_BY_PARTITION_KEY,
                                container,
                                fault_injection_container,
                                str(uuid.uuid4()),
                                PK_VALUE,
                                expected_uri)

        validate_unhealthy_partitions_mm(global_endpoint_manager, 1)
        # remove faults and reduce initial recover time and perform a write
        original_unavailable_time = _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS
        _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS = 1
        custom_transport.faults = []
        try:
            await perform_write_operation(DELETE_ALL_ITEMS_BY_PARTITION_KEY,
                                    container,
                                    fault_injection_container,
                                    str(uuid.uuid4()),
                                    PK_VALUE,
                                    uri_down)
        finally:
            _partition_health_tracker.INITIAL_UNAVAILABLE_TIME_MS = original_unavailable_time
        validate_unhealthy_partitions_mm(global_endpoint_manager, 0)
        await cleanup_method([custom_setup, setup])


    @pytest.mark.parametrize("error", create_errors())
    async def test_write_failure_rate_threshold_delete_all_items_by_pk_mm_async(self, setup_teardown, error):
        if hasattr(error, "status_code") and error.status_code == 503:
            pytest.skip("ServiceUnavailableError will do a cross-region retry, so it has to be special cased.")
        error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(0, error))
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = await self.setup_info(error_lambda, mm=True)
        fault_injection_container = custom_setup['col']
        container = setup['col']
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager
        # lower minimum requests for testing
        _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 10
        os.environ["AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"] = "80"
        try:
            # writes should fail but still be tracked and mark unavailable a partition after crossing threshold
            for i in range(10):
                validate_unhealthy_partitions_mm(global_endpoint_manager, 0)
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
                        await perform_write_operation(DELETE_ALL_ITEMS_BY_PARTITION_KEY,
                                                container,
                                                fault_injection_container,
                                                str(uuid.uuid4()),
                                                PK_VALUE,
                                                expected_uri)
                    assert exc_info.value == error

            validate_unhealthy_partitions_mm(global_endpoint_manager, 1)

        finally:
            os.environ["AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"] = "90"
            # restore minimum requests
            _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100
        await cleanup_method([custom_setup, setup])

    @pytest.mark.parametrize("error", create_errors())
    async def test_write_failure_rate_threshold_delete_all_items_by_pk_sm_async(self, setup_teardown, error):
        error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(0, error))
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = await self.setup_info(error_lambda)
        fault_injection_container = custom_setup['col']
        container = setup['col']
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager
        # lower minimum requests for testing
        _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 10
        os.environ["AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"] = "80"
        try:
            # writes should fail but still be tracked and mark unavailable a partition after crossing threshold
            for i in range(10):
                validate_unhealthy_partitions_sm_mrr(global_endpoint_manager, 0)
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
                        await perform_write_operation(DELETE_ALL_ITEMS_BY_PARTITION_KEY,
                                                container,
                                                fault_injection_container,
                                                str(uuid.uuid4()),
                                                PK_VALUE,
                                                expected_uri)
                    assert exc_info.value == error

            validate_unhealthy_partitions_sm_mrr(global_endpoint_manager, 0)

        finally:
            os.environ["AZURE_COSMOS_FAILURE_PERCENTAGE_TOLERATED"] = "90"
            # restore minimum requests
            _partition_health_tracker.MINIMUM_REQUESTS_FOR_FAILURE_RATE = 100
        await cleanup_method([custom_setup, setup])

    # test cosmos client timeout

if __name__ == '__main__':
    unittest.main()
