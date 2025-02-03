# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import unittest
from azure.mgmt.loadtesting import LoadTestMgmtClient
from azure.mgmt.loadtesting.models import QuotaBucketRequest
from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

AZURE_LOCATION = "westus2"


@pytest.mark.live_test_only
class TestQuotaOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.loadtestservice_client = self.create_mgmt_client(LoadTestMgmtClient)

    @recorded_by_proxy
    def test_list_quota(self):

        loadtest_quota_list = self.loadtestservice_client.quotas.list(AZURE_LOCATION)
        for loadtestQuota in loadtest_quota_list:
            assert loadtestQuota
            assert loadtestQuota.name
            assert loadtestQuota.id
            assert loadtestQuota.type
            assert loadtestQuota.limit != None
            assert loadtestQuota.usage != None

    @recorded_by_proxy
    def test_get_quota(self):

        quotaBucket = "maxEngineInstancesPerTestRun"
        loadtest_quota_bucket = self.loadtestservice_client.quotas.get(
            AZURE_LOCATION, quotaBucket
        )
        assert loadtest_quota_bucket
        assert loadtest_quota_bucket.name == quotaBucket
        assert loadtest_quota_bucket.id
        assert loadtest_quota_bucket.type
        assert loadtest_quota_bucket.limit != None
        assert loadtest_quota_bucket.usage != None

    @recorded_by_proxy
    def test_check_quota_availability(self):

        quotaBucket = "maxEngineInstancesPerTestRun"
        loadtest_quota_bucket = self.loadtestservice_client.quotas.get(
            AZURE_LOCATION, quotaBucket
        )
        assert loadtest_quota_bucket
        assert loadtest_quota_bucket.name == quotaBucket
        assert loadtest_quota_bucket.id
        assert loadtest_quota_bucket.type
        assert loadtest_quota_bucket.limit != None
        assert loadtest_quota_bucket.usage != None

        check_availability_payload = QuotaBucketRequest(
            new_quota=loadtest_quota_bucket.limit
        )
        loadtest_quota_check_availability = (
            self.loadtestservice_client.quotas.check_availability(
                AZURE_LOCATION, quotaBucket, check_availability_payload
            )
        )
        assert loadtest_quota_check_availability
        assert loadtest_quota_check_availability.name == quotaBucket
        assert loadtest_quota_check_availability.id
        assert loadtest_quota_check_availability.type
        assert loadtest_quota_check_availability.is_available != None
        assert loadtest_quota_check_availability.availability_status


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()
