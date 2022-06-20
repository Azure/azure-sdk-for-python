# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from json import load
from testcase import LoadtestserviceTest, LoadtestservicePowerShellPreparer

class LoadtestserviceSmokeTest(LoadtestserviceTest):

    @LoadtestservicePowerShellPreparer()
    def test_smoke_create_or_update_test(self, loadtestservice_endpoint):
        client = self.create_client(loadtestservice_endpoint)
        test_id="d7c9990e"
        body_test={"resourceId":"/subs","testId":"d7c9990e","description":"","displayName":"newtest","loadTestConfig":{"engineSize":"m","engineInstances":1,"splitAllCSVs":False},"secrets":{},"environmentVariables":{},"passFailCriteria":{"passFailMetrics":{}},"keyvaultReferenceIdentityType":"SystemAssigned","keyvaultReferenceIdentityId":None}
        result = client.test.create_or_update_test(test_id, body_test)
        assert result is not None

    @LoadtestservicePowerShellPreparer()
    def test_smoke_list_search(self, loadtestservice_endpoint):
        client = self.create_client(loadtestservice_endpoint)
        result = client.test.list_load_test_search()
        assert result is not None

    @LoadtestservicePowerShellPreparer()
    def test_smoke_delete(self, loadtestservice_endpoint):
        client = self.create_client(loadtestservice_endpoint)
        test_id="d7c9990e"
        result = client.test.delete_load_test(test_id)
        assert result is None