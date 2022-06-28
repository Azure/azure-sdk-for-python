# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import LoadtestservicePowerShellPreparer
from testcase_async import LoadtestserviceAsyncTest


class LoadtestserviceSmokeAsyncTest(LoadtestserviceAsyncTest):

    @LoadtestservicePowerShellPreparer()
    async def test_smoke_create_or_update_test(self, loadtestservice_endpoint):
        client = self.create_client(loadtestservice_endpoint)
        test_id="000002" 
        body_test={"resourceId":"/subscriptions/123456/resourceGroups/fake/providers/Microsoft.LoadTestService/loadtests/fake",
                "testId":"000002","description":"","displayName":"test",
                "loadTestConfig":{"engineSize":"m","engineInstances":1,"splitAllCSVs":False},"secrets":{},"environmentVariables":{},
                "passFailCriteria":{"passFailMetrics":{}},"keyvaultReferenceIdentityType":"SystemAssigned","keyvaultReferenceIdentityId":None}
        result = await client.test.create_or_update_test(test_id, body_test)
        assert result is not None


    @LoadtestservicePowerShellPreparer()
    async def test_smoke_list_search(self, loadtestservice_endpoint):
        client = self.create_client(loadtestservice_endpoint)
        result = await client.test.list_load_test_search()
        assert result is not None