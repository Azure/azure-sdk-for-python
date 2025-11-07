# -*- coding: utf-8 -*-
# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
from azure.cosmos import DatabaseProxy
import unittest
import uuid
import pytest
from azure.core.exceptions import ServiceRequestError
import azure.cosmos.cosmos_client as cosmos_client
import test_config
from azure.cosmos import PartitionKey
from _fault_injection_transport import FaultInjectionTransport
from azure.cosmos.documents import _OperationType, ConnectionPolicy


@pytest.mark.cosmosMultiRegion
class TestServiceRequestRetryPolicies(unittest.TestCase):
    """Test cases for the read_items API."""

    created_db: DatabaseProxy = None
    client: cosmos_client.CosmosClient = None
    host = test_config.TestConfig.host
    masterKey = test_config.TestConfig.masterKey
    configs = test_config.TestConfig
    TEST_DATABASE_ID = configs.TEST_DATABASE_ID

    @classmethod
    def setUpClass(cls):
        cls.client = cosmos_client.CosmosClient(cls.host, cls.masterKey)
        cls.database = cls.client.get_database_client(cls.TEST_DATABASE_ID)


    def test_write_failover_to_global_with_service_request_error(self):
        container = self.database.create_container("service_request_mrr_test_" + str(uuid.uuid4()),
                                                   PartitionKey(path="/id"))

        # 1. Get write regions and ensure there are at least 2 for this test.
        endpoint_manager = self.client.client_connection._global_endpoint_manager
        db_account = self.client.get_database_account()
        endpoint_manager.refresh_endpoint_list(db_account)

        write_locations_map = endpoint_manager.location_cache.account_locations_by_write_endpoints

        if len(write_locations_map) < 2:
            pytest.skip("This test requires an account with 2 or more write regions.")

        write_endpoints = list(write_locations_map.keys())
        write_locations = list(write_locations_map.values())

        account_name = self.host.split(".")[0].split("//")[1]
        region_to_fail_slug = write_endpoints[1].split('/')[2].replace(f"{account_name}-", "").split('.')[0]

        region_to_exclude = write_locations[0]  # Use the display name for ExcludedLocations

        # 2. Set up a client with one region excluded and a fault injection transport.
        policy = ConnectionPolicy()  # Create a new policy object for this test
        policy.EnableEndpointDiscovery = True
        policy.UseMultipleWriteLocations = True
        policy.ExcludedLocations = [region_to_exclude]
        fault_injection_transport = FaultInjectionTransport()

        client_with_faults = cosmos_client.CosmosClient(
            self.host,
            self.masterKey,
            connection_policy=policy,
            transport=fault_injection_transport,

        )
        container_with_faults = client_with_faults.get_database_client(self.database.id).get_container_client(
            container.id)

        # 3. Configure fault injection to fail requests to the second write region with a ServiceRequestError.
        error_to_inject = ServiceRequestError(message="Simulated Service Request Error")

        def predicate(request):
            # Fail if it's a create item operation and the host matches the region we want to fail.
            is_create = FaultInjectionTransport.predicate_is_operation_type(request, _OperationType.Create)
            is_target_region = region_to_fail_slug in request.url
            return is_create and is_target_region

        def fault_action(_):
            raise error_to_inject

        fault_injection_transport.add_fault(predicate, fault_action)

        # 4. Execute a write operation. It should fail with ServiceRequestError as no regions are available.
        with self.assertRaises(ServiceRequestError) as context:
            container_with_faults.create_item(body={'id': 'failover_test_id', 'pk': 'pk_value'})

        self.assertIn("Simulated Service Request Error", str(context.exception))


if __name__ == "__main__":
    unittest.main()

