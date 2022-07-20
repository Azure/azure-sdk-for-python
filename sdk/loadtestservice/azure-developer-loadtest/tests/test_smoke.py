# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from json import load
from testcase import LoadtestingTest, LoadtestingPowerShellPreparer


class LoadtestingSmokeTest(LoadtestingTest):
    @LoadtestingPowerShellPreparer()
    def test_smoke_create_or_update_test(self, loadtestservice_endpoint):
        client = self.create_client(loadtestservice_endpoint)
        test_id = "000001"
        body_test = {
            "resourceId": "/subscriptions/123456/resourceGroups/fake/providers/Microsoft.LoadTestService/loadtests/fake",
            "testId": "000001",
            "description": "",
            "displayName": "test",
            "loadTestConfig": {"engineSize": "m", "engineInstances": 1, "splitAllCSVs": False},
            "secrets": {},
            "environmentVariables": {},
            "passFailCriteria": {"passFailMetrics": {}},
            "keyvaultReferenceIdentityType": "SystemAssigned",
            "keyvaultReferenceIdentityId": None,
        }
        result = client.administration.test.create_or_update_test(test_id, body_test)
        assert result is not None

    @LoadtestingPowerShellPreparer()
    def test_smoke_list_search(self, loadtestservice_endpoint):
        client = self.create_client(loadtestservice_endpoint)
        result = client.administration.test.list_load_test_search()
        assert result is not None

    @LoadtestingPowerShellPreparer()
    def test_smoke_delete_test(self, loadtestservice_endpoint):
        client = self.create_client(loadtestservice_endpoint)
        test_id = "000001"
        result = client.administration.test.delete_load_test(test_id)
        assert result is None
