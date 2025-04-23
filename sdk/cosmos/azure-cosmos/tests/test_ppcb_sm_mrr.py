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
from azure.cosmos import PartitionKey, _partition_health_tracker
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from _fault_injection_transport_async import FaultInjectionTransportAsync
from test_ppcb_mm_async import perform_write_operation, create_doc, PK_VALUE, write_operations_and_errors, \
    cleanup_method, read_operations_and_errors, perform_read_operation, CHANGE_FEED, QUERY, READ_ALL_ITEMS, operations
from test_ppcb_sm_mrr_async import validate_unhealthy_partitions

COLLECTION = "created_collection"
@pytest_asyncio.fixture()
def setup_teardown():
    os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "True"
    client = CosmosClient(TestPerPartitionCircuitBreakerSmMrr.host, TestPerPartitionCircuitBreakerSmMrr.master_key)
    created_database = client.get_database_client(TestPerPartitionCircuitBreakerSmMrr.TEST_DATABASE_ID)
    created_database.create_container(TestPerPartitionCircuitBreakerSmMrr.TEST_CONTAINER_SINGLE_PARTITION_ID,
                                            partition_key=PartitionKey("/pk"),
                                            offer_throughput=10000)
    # allow some time for the container to be created as this method is in different event loop
    asyncio.sleep(3)
    yield
    created_database.delete_container(TestPerPartitionCircuitBreakerSmMrr.TEST_CONTAINER_SINGLE_PARTITION_ID)
    client.close()
    os.environ["AZURE_COSMOS_ENABLE_CIRCUIT_BREAKER"] = "False"

@pytest.mark.cosmosEmulator
@pytest.mark.usefixtures("setup")
class TestPerPartitionCircuitBreakerSmMrr:
    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = os.path.basename(__file__) + str(uuid.uuid4())

    def setup_method_with_custom_transport(self, custom_transport: AioHttpTransport, default_endpoint=host, **kwargs):
        client = CosmosClient(default_endpoint, self.master_key, consistency_level="Session",
                              preferred_locations=["Write Region", "Read Region"],
                              transport=custom_transport, **kwargs)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_SINGLE_PARTITION_ID)
        return {"client": client, "db": db, "col": container}

    @staticmethod
    def cleanup_method(initialized_objects: Dict[str, Any]):
        method_client: CosmosClient = initialized_objects["client"]
        method_client.close()


    def create_custom_transport_sm_mrr(self):
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

    def setup_info(self, error):
        expected_uri = self.host
        uri_down = expected_uri.replace("localhost", "127.0.0.1")
        custom_transport = self.create_custom_transport_sm_mrr()
        # two documents targeted to same partition, one will always fail and the other will succeed
        doc = create_doc()
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_document_operation(r) and
                               FaultInjectionTransportAsync.predicate_targets_region(r, uri_down))
        custom_transport.add_fault(predicate,
                                   error)
        custom_setup = self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host)
        setup = self.setup_method_with_custom_transport(None, default_endpoint=self.host)
        return setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors())
    def test_write_consecutive_failure_threshold(self, setup_teardown, write_operation, error):
        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(0, error)
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = self.setup_info(error_lambda)
        container = setup['col']
        fault_injection_container = custom_setup['col']
        global_endpoint_manager = container.client_connection._global_endpoint_manager

        # writes should fail in sm mrr with circuit breaker and should not mark unavailable a partition
        for i in range(6):
            validate_unhealthy_partitions(global_endpoint_manager, 0)
            with pytest.raises((CosmosHttpResponseError, ServiceResponseError)):
                perform_write_operation(
                    write_operation,
                    container,
                    fault_injection_container,
                    str(uuid.uuid4()),
                    PK_VALUE,
                    expected_uri,
                )

        validate_unhealthy_partitions(global_endpoint_manager, 0)
        cleanup_method([custom_setup, setup])


    @pytest.mark.parametrize("read_operation, error", read_operations_and_errors())
    def test_read_consecutive_failure_threshold(self, setup_teardown, read_operation, error):
        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(0, error)
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = self.setup_info(error_lambda)
        container = setup['col']
        fault_injection_container = custom_setup['col']

        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        # create a document to read
        container.create_item(body=doc)

        # reads should fail over and only the relevant partition should be marked as unavailable
        perform_read_operation(read_operation,
                                     fault_injection_container,
                                     doc['id'],
                                     doc['pk'],
                                     expected_uri)
        # partition should not have been marked unavailable after one error
        validate_unhealthy_partitions(global_endpoint_manager, 0)

        for i in range(10):
            perform_read_operation(read_operation,
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
            perform_read_operation(read_operation,
                                         fault_injection_container,
                                         doc['id'],
                                         doc['pk'],
                                         uri_down)
        finally:
            _partition_health_tracker.INITIAL_UNAVAILABLE_TIME = original_unavailable_time
        validate_unhealthy_partitions(global_endpoint_manager, 0)
        cleanup_method([custom_setup, setup])

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors())
    def test_write_failure_rate_threshold(self, setup_teardown, write_operation, error):
        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(0, error)
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = self.setup_info(error_lambda)
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
                    fault_injection_container.upsert_item(body=doc)
                    custom_transport.add_fault(predicate,
                                               lambda r: FaultInjectionTransportAsync.error_after_delay(
                                                   0,
                                                   error
                                               ))
                else:
                    with pytest.raises((CosmosHttpResponseError, ServiceResponseError)) as exc_info:
                        perform_write_operation(write_operation,
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
        cleanup_method([custom_setup, setup])

    @pytest.mark.parametrize("read_operation, error", read_operations_and_errors())
    def test_read_failure_rate_threshold(self, setup_teardown, read_operation, error):
        error_lambda = lambda r: FaultInjectionTransportAsync.error_after_delay(0, error)
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = self.setup_info(error_lambda)
        container = setup['col']
        fault_injection_container = custom_setup['col']
        container.upsert_item(body=doc)
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
                perform_read_operation(read_operation,
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
        cleanup_method([custom_setup, setup])


    @pytest.mark.parametrize("read_operation, write_operation", operations())
    def test_service_request_error(self, read_operation, write_operation):
        # the region should be tried 4 times before failing over and mark the partition as unavailable
        # the region should not be marked as unavailable
        error_lambda = lambda r: FaultInjectionTransportAsync.error_region_down()
        setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate = self.setup_info(error_lambda)
        container = setup['col']
        fault_injection_container = custom_setup['col']
        container.upsert_item(body=doc)
        perform_read_operation(read_operation,
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
            perform_read_operation(read_operation,
                                         fault_injection_container,
                                         doc['id'],
                                         PK_VALUE,
                                         uri_down)
        finally:
            _partition_health_tracker.INITIAL_UNAVAILABLE_TIME = original_unavailable_time
        validate_unhealthy_partitions(global_endpoint_manager, 0)

        custom_transport.add_fault(predicate,
                                   lambda r: FaultInjectionTransportAsync.error_region_down())

        perform_write_operation(write_operation,
                                      container,
                                      fault_injection_container,
                                      str(uuid.uuid4()),
                                      PK_VALUE,
                                      expected_uri)
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        validate_unhealthy_partitions(global_endpoint_manager, 0)
        # there shouldn't be region marked as unavailable
        assert len(global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint) == 1
        cleanup_method([custom_setup, setup])

    # test cosmos client timeout

if __name__ == '__main__':
    unittest.main()