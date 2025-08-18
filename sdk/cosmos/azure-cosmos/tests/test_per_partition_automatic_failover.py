# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import unittest
import uuid

import pytest
import test_config
from azure.core.exceptions import ServiceResponseError
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from _fault_injection_transport import FaultInjectionTransport
from test_per_partition_circuit_breaker_mm import (REGION_1, REGION_2, PK_VALUE, BATCH,
                                                   write_operations_and_errors, perform_write_operation)

# cspell:disable

def create_failover_errors():
    errors = []
    error_codes = [403]
    for error_code in error_codes:
        errors.append(CosmosHttpResponseError(
            status_code=error_code,
            message="Some injected error.",
            sub_status=3))
    return errors

def create_threshold_errors():
    errors = []
    error_codes = [408, 500, 502, 503, 504]
    for error_code in error_codes:
        errors.append(CosmosHttpResponseError(
            status_code=error_code,
            message="Some injected error."))
    errors.append(ServiceResponseError(message="Injected Service Response Error."))
    return errors

# These tests assume that the configured live account has one main write region and one secondary read region.

@pytest.mark.cosmosPerPartitionAutomaticFailover
class TestPerPartitionAutomaticFailover:
    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_MULTI_PARTITION_ID = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID

    def setup_method_with_custom_transport(self, custom_transport, default_endpoint=host, **kwargs):
        container_id = kwargs.pop("container_id", None)
        if not container_id:
            container_id = self.TEST_CONTAINER_MULTI_PARTITION_ID
        client = CosmosClient(default_endpoint, self.master_key, consistency_level="Session",
                              preferred_locations=[REGION_1, REGION_2],
                              transport=custom_transport, **kwargs)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(container_id)
        return {"client": client, "db": db, "col": container}

    def setup_info(self, error, max_count=None, is_batch=False, **kwargs):
        custom_transport = FaultInjectionTransport()
        # two documents targeted to same partition, one will always fail and the other will succeed
        doc_fail_id = str(uuid.uuid4())
        doc_success_id = str(uuid.uuid4())
        predicate = lambda r: FaultInjectionTransport.predicate_req_for_document_with_id(r, doc_fail_id)
        # The MockRequest only gets used to create the MockHttpResponse
        mock_request = FaultInjectionTransport.MockHttpRequest(url=self.host)
        if is_batch:
            success_response = FaultInjectionTransport.MockHttpResponse(mock_request, 200, [{"statusCode": 200}],)
        else:
            success_response = FaultInjectionTransport.MockHttpResponse(mock_request, 200)
        custom_transport.add_fault(predicate=predicate, fault_factory=error, max_inner_count=max_count,
                                   after_max_count=success_response)
        is_get_account_predicate = lambda r: FaultInjectionTransport.predicate_is_database_account_call(r)
        # Set the database account response to have PPAF enabled
        ppaf_enabled_database_account = \
            lambda r, inner: FaultInjectionTransport.transform_topology_ppaf_enabled(inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            ppaf_enabled_database_account)
        setup = self.setup_method_with_custom_transport(None, default_endpoint=self.host, **kwargs)
        custom_setup = self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host, **kwargs)
        return setup, doc_fail_id, doc_success_id, custom_setup, custom_transport, predicate

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors(create_failover_errors()))
    def test_ppaf_partition_info_cache_and_routing(self, write_operation, error):
        # This test validates that the partition info cache is updated correctly upon failures, and that the
        # per-partition automatic failover logic routes requests to the next available regional endpoint on 403.3 errors.
        error_lambda = lambda r: FaultInjectionTransport.error_after_delay(0, error)
        setup, doc_fail_id, doc_success_id, custom_setup, custom_transport, predicate = self.setup_info(error_lambda, 1, write_operation == BATCH)
        container = setup['col']
        fault_injection_container = custom_setup['col']
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        # Create a document to populate the per-partition GEM partition range info cache
        fault_injection_container.create_item(body={'id': doc_success_id, 'pk': PK_VALUE,
                                                    'name': 'sample document', 'key': 'value'})
        pk_range_wrapper = list(global_endpoint_manager.partition_range_to_failover_info.keys())[0]
        initial_endpoint = global_endpoint_manager.partition_range_to_failover_info[pk_range_wrapper].current_regional_endpoint

        # Based on our configuration, we should have had one error followed by a success - marking only the previous endpoint as unavailable
        perform_write_operation(
            write_operation,
            container,
            fault_injection_container,
            doc_fail_id,
            PK_VALUE)
        partition_info = global_endpoint_manager.partition_range_to_failover_info[pk_range_wrapper]
        # Verify that the partition is marked as unavailable, and that the current regional endpoint is not the same
        assert len(partition_info.unavailable_regional_endpoints) == 1
        assert initial_endpoint in partition_info.unavailable_regional_endpoints
        assert initial_endpoint != partition_info.current_regional_endpoint # west us 3 != west us

        # Now we run another request to see how the cache gets updated
        perform_write_operation(
            write_operation,
            container,
            fault_injection_container,
            str(uuid.uuid4()),
            PK_VALUE)
        partition_info = global_endpoint_manager.partition_range_to_failover_info[pk_range_wrapper]
        # Verify that the cache is empty, since the request going to the second regional endpoint failed
        # Once we reach the point of all available regions being marked as unavailable, the cache is cleared
        assert len(partition_info.unavailable_regional_endpoints) == 0
        assert initial_endpoint not in partition_info.unavailable_regional_endpoints
        assert partition_info.current_regional_endpoint is None


    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors(create_threshold_errors()))
    def test_ppaf_partition_thresholds_and_routing(self, write_operation, error):
        # This test validates the consecutive failures logic is properly handled for per-partition automatic failover,
        # and that the per-partition automatic failover logic routes requests to the next available regional endpoint
        # after enough consecutive failures have occurred.
        error_lambda = lambda r: FaultInjectionTransport.error_after_delay(0, error)
        setup, doc_fail_id, doc_success_id, custom_setup, custom_transport, predicate = self.setup_info(error_lambda)
        container = setup['col']
        fault_injection_container = custom_setup['col']
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        # Create a document to populate the per-partition GEM partition range info cache
        fault_injection_container.create_item(body={'id': doc_success_id, 'pk': PK_VALUE,
                                                    'name': 'sample document', 'key': 'value'})
        pk_range_wrapper = list(global_endpoint_manager.partition_range_to_failover_info.keys())[0]
        initial_endpoint = global_endpoint_manager.partition_range_to_failover_info[pk_range_wrapper].current_regional_endpoint


        is_503 = hasattr(error, 'status_code') and error.status_code == 503
        # Since 503 errors are retried by default, we each request counts as two failures
        consecutive_failures = 3 if is_503 else 6

        for i in range(consecutive_failures):
            # We perform the write operation multiple times to check the consecutive failures logic
            with pytest.raises((CosmosHttpResponseError, ServiceResponseError)) as exc_info:
                perform_write_operation(write_operation,
                                        container,
                                        fault_injection_container,
                                        doc_fail_id,
                                        PK_VALUE)
            assert exc_info.value == error
        # Verify that the threshold for consecutive failures is updated
        pk_range_wrappers = list(global_endpoint_manager.ppaf_thresholds_tracker.pk_range_wrapper_to_failure_count.keys())
        assert len(pk_range_wrappers) == 1
        failure_count = global_endpoint_manager.ppaf_thresholds_tracker.pk_range_wrapper_to_failure_count[pk_range_wrappers[0]]
        assert failure_count == 6
        # Run some more requests to the same partition to trigger the failover logic
        for i in range(consecutive_failures):
            with pytest.raises((CosmosHttpResponseError, ServiceResponseError)) as exc_info:
                perform_write_operation(write_operation,
                                        container,
                                        fault_injection_container,
                                        doc_fail_id,
                                        PK_VALUE)
            assert exc_info.value == error
        # We should have marked the previous endpoint as unavailable after 10 successive failures
        partition_info = global_endpoint_manager.partition_range_to_failover_info[pk_range_wrapper]
        # Verify that the partition is marked as unavailable, and that the current regional endpoint is not the same
        assert len(partition_info.unavailable_regional_endpoints) == 1
        assert initial_endpoint in partition_info.unavailable_regional_endpoints
        assert initial_endpoint != partition_info.current_regional_endpoint # west us 3 != west us

        # Since we are failing every request, even though we retried to the next region, that retry should have failed as well
        # This means we should have one extra failure - verify that the value makes sense
        failure_count = global_endpoint_manager.ppaf_thresholds_tracker.pk_range_wrapper_to_failure_count[pk_range_wrappers[0]]
        assert failure_count == 1 if is_503 else 3

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors(create_failover_errors()))
    def test_ppaf_exclude_regions(self, write_operation, error):
        # TODO: finish this test
        return

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors(create_failover_errors()))
    def test_ppaf_invalid_configs(self, write_operation, error):
        # TODO: finish this test
        return



if __name__ == '__main__':
    unittest.main()