# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


from json import load
import unittest

from azure.mgmt.loadtestservice import LoadTestMgmtClient
from azure.mgmt.loadtestservice.models import LoadTestResource, LoadTestResourcePatchRequestBody, QuotaBucketRequest
from devtools_testutils import AzureMgmtTestCase, recorded_by_proxy, ResourceGroupPreparer

AZURE_LOCATION = 'westus2'
LOAD_TEST_RESOURCE_NAME = 'py-sdk-testing-resource-cp'

class LoadTestResourceOperations(AzureMgmtTestCase):
    
    def setUp(self):
        super(LoadTestResourceOperations, self).setUp()

        self.loadtestservice_client = self.create_mgmt_client(
            LoadTestMgmtClient
        )
    
    @ResourceGroupPreparer()
    def test_load_test_resource_operations(self, resource_group):

        # Create a load test resource
        loadtestresource_create_payload = LoadTestResource(location=AZURE_LOCATION)
        
        # Create a load test resource create begin - returns a poller
        loadtest_resource_poller = self.loadtestservice_client.load_tests.begin_create_or_update(resource_group.name, LOAD_TEST_RESOURCE_NAME, loadtestresource_create_payload)
        
        # Wait for the poller to complete
        while loadtest_resource_poller.done()==False:
            loadtest_resource_poller.wait(2)
        
        # Get the result of the poller
        loadtest_resource = loadtest_resource_poller.result()
        
        # Assert the result of the poller
        assert loadtest_resource != None
        assert loadtest_resource.name == LOAD_TEST_RESOURCE_NAME
        assert loadtest_resource.location == AZURE_LOCATION
        assert loadtest_resource.id != None
        
        # Get the load test resource
        loadtest_resource_get = self.loadtestservice_client.load_tests.get(resource_group.name, LOAD_TEST_RESOURCE_NAME)
        
        # Assert the result of the get operation
        assert loadtest_resource.name == loadtest_resource_get.name
        assert loadtest_resource.location == loadtest_resource_get.location
        assert loadtest_resource.id == loadtest_resource_get.id


        # Update the load test resource
        loadtestresourcePatchdata = LoadTestResourcePatchRequestBody(
            identity={
                'type': 'SystemAssigned'
            }
        )

        # load test resource update begin - returns a poller
        loadtest_resource_patch_poller = self.loadtestservice_client.load_tests.begin_update(resource_group.name, LOAD_TEST_RESOURCE_NAME, loadtestresourcePatchdata)
        
        # Wait for the poller to complete
        while loadtest_resource_poller.done()==False:
            loadtest_resource_poller.wait(2)
        
        # Get the result of the poller
        loadtest_resource_patch_response = loadtest_resource_patch_poller.result()

        # Assert the result of the poller
        assert loadtest_resource_patch_response.name == loadtest_resource_get.name
        assert loadtest_resource_patch_response.location == loadtest_resource_get.location
        assert loadtest_resource_patch_response.id == loadtest_resource_get.id
        assert loadtest_resource_patch_response.identity.type == "SystemAssigned"

        # Delete the load test resource
        self.loadtestservice_client.load_tests._delete_initial(resource_group.name, LOAD_TEST_RESOURCE_NAME)

    def test_load_test_quota_operations(self):

        quotaBucket = "maxEngineInstancesPerTestRun"

        # List the load test quota
        loadtest_quota_list = self.loadtestservice_client.quotas.list(AZURE_LOCATION)

        # Assert the result of the list operation
        for loadtestQuota in loadtest_quota_list:
            assert loadtestQuota != None
            assert loadtestQuota.name != None
            assert loadtestQuota.id != None
            assert loadtestQuota.type != None
            assert loadtestQuota.limit != None
            assert loadtestQuota.usage != None

        # Get the load test quota bucket
        loadtest_quota_bucket = self.loadtestservice_client.quotas.get(AZURE_LOCATION, quotaBucket)
        
        # Assert the result of the get operation
        assert loadtest_quota_bucket != None
        assert loadtest_quota_bucket.name == quotaBucket
        assert loadtest_quota_bucket.id != None
        assert loadtest_quota_bucket.type != None
        assert loadtest_quota_bucket.limit != None
        assert loadtest_quota_bucket.usage != None

        # Check availability for quota bucket
        check_availability_payload = QuotaBucketRequest(
            new_quota = loadtest_quota_bucket.limit
        )
        loadtest_quota_check_availability = self.loadtestservice_client.quotas.check_availability(AZURE_LOCATION, quotaBucket, check_availability_payload)

        # Assert the result of the check availability operation
        assert loadtest_quota_check_availability != None
        assert loadtest_quota_check_availability.name == quotaBucket
        assert loadtest_quota_check_availability.id != None
        assert loadtest_quota_check_availability.type != None
        assert loadtest_quota_check_availability.is_available != None
        assert loadtest_quota_check_availability.availability_status != None



#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()     