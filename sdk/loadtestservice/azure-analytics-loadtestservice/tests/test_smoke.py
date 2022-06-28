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
        test_id="a000090b-12cd-004d-015d-1200d8880000" 
        body_test={"resourceId":"/subscriptions/7c71b563-0dc0-4bc0-bcf6-06f8f0516c7a/resourceGroups/yashika-rg/providers/Microsoft.LoadTestService/loadtests/loadtestsdk","testId":"a000090b-12cd-004d-015d-1200d8880000","description":"","displayName":"testsmoke","loadTestConfig":{"engineSize":"m","engineInstances":1,"splitAllCSVs":False},"secrets":{},"environmentVariables":{},"passFailCriteria":{"passFailMetrics":{}},"keyvaultReferenceIdentityType":"SystemAssigned","keyvaultReferenceIdentityId":None}
        result = client.test.create_or_update_test(test_id, body_test)
        assert result is not None

    @LoadtestservicePowerShellPreparer()
    def test_smoke_list_search(self, loadtestservice_endpoint):
        client = self.create_client(loadtestservice_endpoint)
        result = client.test.list_load_test_search()
        assert result is not None

    # @LoadtestservicePowerShellPreparer()
    # def test_smoke_delete_test(self, loadtestservice_endpoint):
    #     client = self.create_client(loadtestservice_endpoint)
    #     test_id="a000090b-12cd-004d-015d-1200d8880000"
    #     result = client.test.delete_load_test(test_id)
    #     assert result is None