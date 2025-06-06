# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import os
import unittest
import uuid

import pytest
from azure.core.exceptions import ServiceResponseError

import test_config
from azure.cosmos import _partition_health_tracker, _location_cache
from azure.cosmos import CosmosClient
from azure.cosmos._partition_health_tracker import HEALTH_STATUS, UNHEALTHY_TENTATIVE, UNHEALTHY
from azure.cosmos.exceptions import CosmosHttpResponseError
from _fault_injection_transport import FaultInjectionTransport
from test_per_partition_circuit_breaker_mm import create_doc, write_operations_and_errors, operations, REGION_1, \
    REGION_2, PK_VALUE, perform_write_operation, perform_read_operation

COLLECTION = "created_collection"

@pytest.mark.cosmosCircuitBreakerMultiRegion
class TestPerPartitionCircuitBreakerSmMrr:
    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    connectionPolicy = test_config.TestConfig.connectionPolicy
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_SINGLE_PARTITION_ID = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID

    def setup_method_with_custom_transport(self, custom_transport, default_endpoint=host, **kwargs):
        client = CosmosClient(default_endpoint, self.master_key, consistency_level="Session",
                              preferred_locations=[REGION_1, REGION_2],
                              transport=custom_transport, **kwargs)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(self.TEST_CONTAINER_SINGLE_PARTITION_ID)
        return {"client": client, "db": db, "col": container}

    def setup_info(self, error):
        expected_uri = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_2)
        uri_down = _location_cache.LocationCache.GetLocationalEndpoint(self.host, REGION_1)
        custom_transport = FaultInjectionTransport()
        # two documents targeted to same partition, one will always fail and the other will succeed
        doc = create_doc()
        predicate = lambda r: (FaultInjectionTransport.predicate_is_document_operation(r) and
                               FaultInjectionTransport.predicate_targets_region(r, uri_down))
        custom_transport.add_fault(predicate,
                                   error)
        custom_setup = self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host)
        setup = self.setup_method_with_custom_transport(None, default_endpoint=self.host)
        return setup, doc, expected_uri, uri_down, custom_setup, custom_transport, predicate

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors())
    def test_write_consecutive_failure_threshold(self, write_operation, error):
        error_lambda = lambda r: FaultInjectionTransport.error_after_delay(0, error)
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

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors())
    def test_write_failure_rate_threshold(self, write_operation, error):
        error_lambda = lambda r: FaultInjectionTransport.error_after_delay(0, error)
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
                                               lambda r: FaultInjectionTransport.error_after_delay(
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

    @pytest.mark.parametrize("read_operation, write_operation", operations())
    def test_service_request_error(self, read_operation, write_operation):
        # the region should be tried 4 times before failing over and mark the partition as unavailable
        # the region should not be marked as unavailable
        error_lambda = lambda r: FaultInjectionTransport.error_region_down()
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

        # there shouldn't be partition marked as unavailable
        validate_unhealthy_partitions(global_endpoint_manager, 0)
        assert len(global_endpoint_manager.location_cache.location_unavailability_info_by_endpoint) == 1

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
                                         expected_uri)
        finally:
            _partition_health_tracker.INITIAL_UNAVAILABLE_TIME = original_unavailable_time
        validate_unhealthy_partitions(global_endpoint_manager, 0)

        custom_transport.add_fault(predicate,
                                   lambda r: FaultInjectionTransport.error_region_down())

        # The global endpoint would be used for the write operation
        expected_uri = self.host
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

    # test cosmos client timeout

if __name__ == '__main__':
    unittest.main()


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
