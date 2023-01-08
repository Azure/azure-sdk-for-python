# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------


import unittest
from azure.mgmt.loadtesting import LoadTestMgmtClient
from azure.mgmt.loadtesting.models import QuotaBucketRequest
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

AZURE_LOCATION = 'westus2'

class TestQuotaOperations(AzureMgmtRecordedTestCase):
    
    def setup_method(self, method):
        self.loadtestservice_client = self.create_mgmt_client(
            LoadTestMgmtClient
        )
    
    @recorded_by_proxy
    def test_list_quota(self):

        loadtest_quota_list = self.loadtestservice_client.quotas.list(AZURE_LOCATION)
        for loadtestQuota in loadtest_quota_list:
            assert loadtestQuota != None
            assert loadtestQuota.name != None
            assert loadtestQuota.id != None
            assert loadtestQuota.type != None
            assert loadtestQuota.limit != None
            assert loadtestQuota.usage != None

    @recorded_by_proxy
    def test_get_quota(self):

        quotaBucket = "maxEngineInstancesPerTestRun"
        loadtest_quota_bucket = self.loadtestservice_client.quotas.get(AZURE_LOCATION, quotaBucket)
        assert loadtest_quota_bucket != None
        assert loadtest_quota_bucket.name == quotaBucket
        assert loadtest_quota_bucket.id != None
        assert loadtest_quota_bucket.type != None
        assert loadtest_quota_bucket.limit != None
        assert loadtest_quota_bucket.usage != None
    
    @recorded_by_proxy
    def test_check_quota_availability(self):

        quotaBucket = "maxEngineInstancesPerTestRun"
        loadtest_quota_bucket = self.loadtestservice_client.quotas.get(AZURE_LOCATION, quotaBucket)
        assert loadtest_quota_bucket != None
        assert loadtest_quota_bucket.name == quotaBucket
        assert loadtest_quota_bucket.id != None
        assert loadtest_quota_bucket.type != None
        assert loadtest_quota_bucket.limit != None
        assert loadtest_quota_bucket.usage != None

        check_availability_payload = QuotaBucketRequest(
            new_quota = loadtest_quota_bucket.limit
        )
        loadtest_quota_check_availability = self.loadtestservice_client.quotas.check_availability(AZURE_LOCATION, quotaBucket, check_availability_payload)
        assert loadtest_quota_check_availability != None
        assert loadtest_quota_check_availability.name == quotaBucket
        assert loadtest_quota_check_availability.id != None
        assert loadtest_quota_check_availability.type != None
        assert loadtest_quota_check_availability.is_available != None
        assert loadtest_quota_check_availability.availability_status != None

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()     