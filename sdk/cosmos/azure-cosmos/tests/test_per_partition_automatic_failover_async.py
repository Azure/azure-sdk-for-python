# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import unittest
import uuid

import asyncio

import pytest
from typing import Dict, Any, Optional

import test_config
from azure.core.pipeline.transport._aiohttp import AioHttpTransport
from azure.core.exceptions import ServiceResponseError
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.aio import CosmosClient
from _fault_injection_transport import FaultInjectionTransport
from _fault_injection_transport_async import FaultInjectionTransportAsync
from test_per_partition_automatic_failover import create_failover_errors, create_threshold_errors, session_retry_hook, ppaf_user_agent_hook
from test_per_partition_circuit_breaker_mm import REGION_1, REGION_2, PK_VALUE, BATCH, write_operations_errors_and_boolean
from test_per_partition_circuit_breaker_mm_async import perform_write_operation

#cspell:ignore PPAF, ppaf

# These tests assume that the configured live account has one main write region and one secondary read region.

@pytest.mark.cosmosPerPartitionAutomaticFailover
@pytest.mark.asyncio
class TestPerPartitionAutomaticFailoverAsync:
    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_MULTI_PARTITION_ID = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID

    async def setup_method_with_custom_transport(self, custom_transport: Optional[AioHttpTransport],
                                                 default_endpoint=host, read_first=False, **kwargs):
        regions = [REGION_2, REGION_1] if read_first else [REGION_1, REGION_2]
        container_id = kwargs.pop("container_id", None)
        exclude_client_regions = kwargs.pop("exclude_client_regions", False)
        excluded_regions = []
        if exclude_client_regions:
            excluded_regions = [REGION_2]
        if not container_id:
            container_id = self.TEST_CONTAINER_MULTI_PARTITION_ID
        client = CosmosClient(default_endpoint, self.master_key, consistency_level="Session",
                              preferred_locations=regions,
                              excluded_locations=excluded_regions,
                              transport=custom_transport, **kwargs)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(container_id)
        await client.__aenter__()
        return {"client": client, "db": db, "col": container}
    
    @staticmethod
    async def cleanup_method(initialized_objects: Dict[str, Any]):
        method_client: CosmosClient = initialized_objects["client"]
        await method_client.close()

    async def setup_info(self, error=None, max_count=None, is_batch=False, exclude_client_regions=False, session_error=False, **kwargs):
        custom_transport = FaultInjectionTransportAsync()
        # two documents targeted to same partition, one will always fail and the other will succeed
        doc_fail_id = str(uuid.uuid4())
        doc_success_id = str(uuid.uuid4())
        predicate = lambda r: (FaultInjectionTransportAsync.predicate_req_for_document_with_id(r, doc_fail_id) and
                               FaultInjectionTransportAsync.predicate_is_write_operation(r, "com"))
        # The MockRequest only gets used to create the MockHttpResponse
        mock_request = FaultInjectionTransport.MockHttpRequest(url=self.host)
        if is_batch:
            success_response = FaultInjectionTransportAsync.MockHttpResponse(mock_request, 200, [{"statusCode": 200}],)
        else:
            success_response = FaultInjectionTransportAsync.MockHttpResponse(mock_request, 200)
        if error:
            custom_transport.add_fault(predicate=predicate, fault_factory=error, max_inner_count=max_count,
                                       after_max_count=success_response)
        if session_error:
            read_predicate = lambda r: (FaultInjectionTransportAsync.predicate_is_operation_type(r, "Read")
                                        and FaultInjectionTransportAsync.predicate_req_for_document_with_id(r, doc_fail_id))
            read_error = CosmosHttpResponseError(
                            status_code=404,
                            message="Some injected error.",
                            sub_status=1002)
            error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(0, read_error))
            success_response = FaultInjectionTransportAsync.MockHttpResponse(mock_request, 200)
            custom_transport.add_fault(predicate=read_predicate, fault_factory=error_lambda, max_inner_count=max_count,
                                       after_max_count=success_response)
        is_get_account_predicate = lambda r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
        # Set the database account response to have PPAF enabled
        ppaf_enabled_database_account = \
            lambda r, inner: FaultInjectionTransportAsync.transform_topology_ppaf_enabled(inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            ppaf_enabled_database_account)
        setup = await self.setup_method_with_custom_transport(None, default_endpoint=self.host,
                                                        exclude_client_regions=exclude_client_regions, **kwargs)
        custom_setup = await self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host,
                                                        exclude_client_regions=exclude_client_regions, **kwargs)
        return setup, doc_fail_id, doc_success_id, custom_setup, custom_transport, predicate

    @pytest.mark.parametrize("write_operation, error, exclude_regions", write_operations_errors_and_boolean(create_failover_errors()))
    async def test_ppaf_partition_info_cache_and_routing_async(self, write_operation, error, exclude_regions):
        # This test validates that the partition info cache is updated correctly upon failures, and that the
        # per-partition automatic failover logic routes requests to the next available regional endpoint.
        # We also verify that this logic is unaffected by user excluded regions, since write-region routing is
        # entirely taken care of on the service.
        error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(0, error))
        setup, doc_fail_id, doc_success_id, custom_setup, custom_transport, predicate = await self.setup_info(error_lambda, 1,
                                                                                                              write_operation == BATCH, exclude_regions=exclude_regions)
        container = setup['col']
        fault_injection_container = custom_setup['col']
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        # Create a document to populate the per-partition GEM partition range info cache
        await fault_injection_container.create_item(body={'id': doc_success_id, 'pk': PK_VALUE,
                                                    'name': 'sample document', 'key': 'value'})
        pk_range_wrapper = list(global_endpoint_manager.partition_range_to_failover_info.keys())[0]
        initial_region = global_endpoint_manager.partition_range_to_failover_info[pk_range_wrapper].current_region

        # Based on our configuration, we should have had one error followed by a success - marking only the previous endpoint as unavailable
        await perform_write_operation(
            write_operation,
            container,
            fault_injection_container,
            doc_fail_id,
            PK_VALUE)
        partition_info = global_endpoint_manager.partition_range_to_failover_info[pk_range_wrapper]
        # Verify that the partition is marked as unavailable, and that the current regional endpoint is not the same
        assert len(partition_info.unavailable_regional_endpoints) == 1
        assert initial_region in partition_info.unavailable_regional_endpoints
        assert initial_region != partition_info.current_region # west us 3 != west us

        # Now we run another request to see how the cache gets updated
        await perform_write_operation(
            write_operation,
            container,
            fault_injection_container,
            doc_fail_id,
            PK_VALUE)
        partition_info = global_endpoint_manager.partition_range_to_failover_info[pk_range_wrapper]
        # Verify that the cache is empty, since the request going to the second regional endpoint failed
        # Once we reach the point of all available regions being marked as unavailable, the cache is cleared
        assert len(partition_info.unavailable_regional_endpoints) == 0
        assert initial_region not in partition_info.unavailable_regional_endpoints
        assert partition_info.current_region is None

    @pytest.mark.parametrize("write_operation, error, exclude_regions", write_operations_errors_and_boolean(create_threshold_errors()))
    async def test_ppaf_partition_thresholds_and_routing_async(self, write_operation, error, exclude_regions):
        # This test validates that the partition info cache is updated correctly upon failures, and that the
        # per-partition automatic failover logic routes requests to the next available regional endpoint.
        # We also verify that this logic is unaffected by user excluded regions, since write-region routing is
        # entirely taken care of on the service.
        error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(0, error))
        setup, doc_fail_id, doc_success_id, custom_setup, custom_transport, predicate = await self.setup_info(error_lambda,
                                                                                                              exclude_regions=exclude_regions,)
        container = setup['col']
        fault_injection_container = custom_setup['col']
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        # Create a document to populate the per-partition GEM partition range info cache
        await fault_injection_container.create_item(body={'id': doc_success_id, 'pk': PK_VALUE,
                                                    'name': 'sample document', 'key': 'value'})
        pk_range_wrapper = list(global_endpoint_manager.partition_range_to_failover_info.keys())[0]
        initial_region = global_endpoint_manager.partition_range_to_failover_info[pk_range_wrapper].current_region

        consecutive_failures = 6
        for i in range(consecutive_failures):
            # We perform the write operation multiple times to check the consecutive failures logic
            with pytest.raises((CosmosHttpResponseError, ServiceResponseError)) as exc_info:
                await perform_write_operation(write_operation,
                                              container,
                                              fault_injection_container,
                                              doc_fail_id,
                                              PK_VALUE)
            assert exc_info.value == error

        # Verify that the threshold for consecutive failures is updated
        pk_range_wrappers = list(global_endpoint_manager.ppaf_thresholds_tracker.pk_range_wrapper_to_failure_count.keys())
        assert len(pk_range_wrappers) == 1
        failure_count = global_endpoint_manager.ppaf_thresholds_tracker.pk_range_wrapper_to_failure_count[pk_range_wrappers[0]]
        assert failure_count == consecutive_failures

        # Verify that a single success to the same partition resets the consecutive failures count
        await perform_write_operation(write_operation,
                                container,
                                fault_injection_container,
                                str(uuid.uuid4()),
                                PK_VALUE)

        failure_count = global_endpoint_manager.ppaf_thresholds_tracker.pk_range_wrapper_to_failure_count.get(pk_range_wrappers[0], 0)
        assert failure_count == 0

        # Run enough failed requests to the partition to trigger the failover logic
        for i in range(12):
            with pytest.raises((CosmosHttpResponseError, ServiceResponseError)) as exc_info:
                await perform_write_operation(write_operation,
                                              container,
                                              fault_injection_container,
                                              doc_fail_id,
                                              PK_VALUE)
            assert exc_info.value == error
        # We should have marked the previous endpoint as unavailable after 10 successive failures
        partition_info = global_endpoint_manager.partition_range_to_failover_info[pk_range_wrapper]
        # Verify that the partition is marked as unavailable, and that the current regional endpoint is not the same
        assert len(partition_info.unavailable_regional_endpoints) == 1
        assert initial_region in partition_info.unavailable_regional_endpoints
        assert initial_region != partition_info.current_region # west us 3 != west us

        # 12 failures - 10 to trigger failover, 2 more to start counting again
        failure_count = global_endpoint_manager.ppaf_thresholds_tracker.pk_range_wrapper_to_failure_count[pk_range_wrappers[0]]
        assert failure_count == 2

    @pytest.mark.parametrize("write_operation, error, exclude_regions", write_operations_errors_and_boolean(create_failover_errors()))
    async def test_ppaf_session_unavailable_retry_async(self, write_operation, error, exclude_regions):
        # Account config has 2 regions: West US 3 (A) and West US (B). This test validates that after marking the write
        # region (A) as unavailable, the next request is retried to the read region (B) and succeeds. The next read request
        # should see that the write region (A) is unavailable for the partition, and should retry to the read region (B) as well.
        # We also verify that this logic is unaffected by user excluded regions, since write-region routing is
        # entirely taken care of on the service.
        error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(0, error))
        setup, doc_fail_id, doc_success_id, custom_setup, custom_transport, predicate = await self.setup_info(error_lambda, max_count=1,
                                                                                                        is_batch=write_operation==BATCH,
                                                                                                        session_error=True, exclude_regions=exclude_regions)
        container = setup['col']
        fault_injection_container = custom_setup['col']
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        # Create a document to populate the per-partition GEM partition range info cache
        await fault_injection_container.create_item(body={'id': doc_success_id, 'pk': PK_VALUE,
                                                    'name': 'sample document', 'key': 'value'})
        pk_range_wrapper = list(global_endpoint_manager.partition_range_to_failover_info.keys())[0]
        initial_region = global_endpoint_manager.partition_range_to_failover_info[pk_range_wrapper].current_region

        # Verify the region that is being used for the read requests
        read_response = await fault_injection_container.read_item(doc_success_id, PK_VALUE)
        uri = read_response.get_response_headers().get('Content-Location')
        region = fault_injection_container.client_connection._global_endpoint_manager.location_cache.get_location_from_endpoint(uri)
        assert region == REGION_1 # first preferred region

        # Based on our configuration, we should have had one error followed by a success - marking only the previous endpoint as unavailable
        await perform_write_operation(
                write_operation,
                container,
                fault_injection_container,
                doc_fail_id,
                PK_VALUE)
        partition_info = global_endpoint_manager.partition_range_to_failover_info[pk_range_wrapper]
        # Verify that the partition is marked as unavailable, and that the current regional endpoint is not the same
        assert len(partition_info.unavailable_regional_endpoints) == 1
        assert initial_region in partition_info.unavailable_regional_endpoints
        assert initial_region != partition_info.current_region # west us 3 != west us

        # Now we run a read request that runs into a 404.1002 error, which should retry to the read region
        # We verify that the read request was going to the correct region by using the raw_response_hook
        fault_injection_container.read_item(doc_fail_id, PK_VALUE, raw_response_hook=session_retry_hook)

    async def test_ppaf_user_agent_feature_flag_async(self):
        # Simple test to verify the user agent suffix is being updated with the relevant feature flags
        setup, doc_fail_id, doc_success_id, custom_setup, custom_transport, predicate = await self.setup_info()
        fault_injection_container = custom_setup['col']
        # Create a document to check the response headers
        await fault_injection_container.upsert_item(body={'id': doc_success_id, 'pk': PK_VALUE, 'name': 'sample document', 'key': 'value'},
                                                    raw_response_hook=ppaf_user_agent_hook)

if __name__ == '__main__':
    unittest.main()
