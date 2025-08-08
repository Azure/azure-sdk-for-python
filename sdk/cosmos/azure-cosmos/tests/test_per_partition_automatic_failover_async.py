# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
import unittest
import uuid

import asyncio

import pytest
from typing import Dict, Any, Optional

import test_config
from azure.core.pipeline.transport._aiohttp import AioHttpTransport
from azure.cosmos.aio import CosmosClient
from _fault_injection_transport import FaultInjectionTransport
from _fault_injection_transport_async import FaultInjectionTransportAsync
from test_per_partition_automatic_failover import create_errors
from test_per_partition_circuit_breaker_mm import REGION_1, REGION_2, PK_VALUE, BATCH, write_operations_and_errors
from test_per_partition_circuit_breaker_mm_async import perform_write_operation

# cspell:disable

# These tests assume that the configured live account has one main write region and one secondary read region.

@pytest.mark.cosmosPerPartitionAutomaticFailover
@pytest.mark.asyncio
class TestPerPartitionAutomaticFailoverAsync:
    host = test_config.TestConfig.host
    master_key = test_config.TestConfig.masterKey
    TEST_DATABASE_ID = test_config.TestConfig.TEST_DATABASE_ID
    TEST_CONTAINER_MULTI_PARTITION_ID = test_config.TestConfig.TEST_MULTI_PARTITION_CONTAINER_ID

    async def setup_method_with_custom_transport(self, custom_transport: Optional[AioHttpTransport], default_endpoint=host, **kwargs):
        container_id = kwargs.pop("container_id", None)
        if not container_id:
            container_id = self.TEST_CONTAINER_MULTI_PARTITION_ID
        client = CosmosClient(default_endpoint, self.master_key, consistency_level="Session",
                              preferred_locations=[REGION_1, REGION_2],
                              transport=custom_transport, **kwargs)
        db = client.get_database_client(self.TEST_DATABASE_ID)
        container = db.get_container_client(container_id)
        return {"client": client, "db": db, "col": container}
    
    @staticmethod
    async def cleanup_method(initialized_objects: Dict[str, Any]):
        method_client: CosmosClient = initialized_objects["client"]
        await method_client.close()

    async def setup_info(self, error, max_count=None, is_batch=False, **kwargs):
        custom_transport = FaultInjectionTransportAsync()
        # two documents targeted to same partition, one will always fail and the other will succeed
        doc_fail_id = str(uuid.uuid4())
        doc_success_id = str(uuid.uuid4())
        predicate = lambda r: FaultInjectionTransportAsync.predicate_req_for_document_with_id(r, doc_fail_id)
        # The MockRequest only gets used to create the MockHttpResponse
        mock_request = FaultInjectionTransport.MockHttpRequest(url=self.host)
        if is_batch:
            success_response = FaultInjectionTransportAsync.MockHttpResponse(mock_request, 200, [{"statusCode": 200}],)
        else:
            success_response = FaultInjectionTransportAsync.MockHttpResponse(mock_request, 200)
        custom_transport.add_fault(predicate=predicate, fault_factory=error, max_inner_count=max_count,
                                   after_max_count=success_response)
        is_get_account_predicate = lambda r: FaultInjectionTransportAsync.predicate_is_database_account_call(r)
        # Set the database account response to have PPAF enabled
        ppaf_enabled_database_account = \
            lambda r, inner: FaultInjectionTransportAsync.transform_topology_ppaf_enabled(inner=inner)
        custom_transport.add_response_transformation(
            is_get_account_predicate,
            ppaf_enabled_database_account)
        setup = await self.setup_method_with_custom_transport(None, default_endpoint=self.host, **kwargs)
        custom_setup = await self.setup_method_with_custom_transport(custom_transport, default_endpoint=self.host, **kwargs)
        return setup, doc_fail_id, doc_success_id, custom_setup, custom_transport, predicate

    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors(create_errors()))
    async def test_ppaf_partition_info_cache_and_routing_async(self, write_operation, error):
        # This test validates that the partition info cache is updated correctly upon failures, and that the
        # per-partition automatic failover logic routes requests to the next available regional endpoint
        error_lambda = lambda r: asyncio.create_task(FaultInjectionTransportAsync.error_after_delay(
            0,
            error
        ))
        setup, doc_fail_id, doc_success_id, custom_setup, custom_transport, predicate = await self.setup_info(error_lambda, 1, write_operation == BATCH)
        container = setup['col']
        fault_injection_container = custom_setup['col']
        global_endpoint_manager = fault_injection_container.client_connection._global_endpoint_manager

        # Create a document to populate the per-partition GEM partition range info cache
        await fault_injection_container.create_item(body={'id': doc_success_id, 'pk': PK_VALUE,
                                                    'name': 'sample document', 'key': 'value'})
        pk_range_wrapper = list(global_endpoint_manager.partition_range_to_failover_info.keys())[0]
        initial_endpoint = global_endpoint_manager.partition_range_to_failover_info[pk_range_wrapper].current_regional_endpoint

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
        assert initial_endpoint in partition_info.unavailable_regional_endpoints
        assert initial_endpoint != partition_info.current_regional_endpoint # west us 3 != west us

        # Now we run another request to see how the cache gets updated
        await perform_write_operation(
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


    @pytest.mark.parametrize("write_operation, error", write_operations_and_errors(create_errors()))
    async def test_ppaf_exclude_regions_async(self, write_operation, error):
        # TODO: finish this test
        return



if __name__ == '__main__':
    unittest.main()
