# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import LoadtestingPowerShellPreparer
from testcase_async import LoadtestingAsyncTest

TEST_ID = "a011890b-0201-004d-010d"  # ID to be assigned to a test
FILE_ID = "a012b234-1230-ab00-0040"  # ID to be assigned to file uploaded
TEST_RUN_ID = "08673e89-3285-46a1-9c6b"  # ID to be assigned to a test run
APP_COMPONENT = "01730263-6671-4216-b283"  # ID of the APP Component
DISPLAY_NAME = "new_namespace-new-namespace"  # display name
SUBSCRIPTION_ID = "fake-subs-id"


class LoadtestingSmokeAsyncTest(LoadtestingAsyncTest):

    # @pytest.mark.asyncio
    @LoadtestingPowerShellPreparer()
    async def test_smoke_async(self, loadtesting_endpoint):
        client = self.create_client(endpoint=loadtesting_endpoint)
        # result = await client.load_test_administration.create_or_update_test( TEST_ID, { "resourceId":
        # f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/yashika-rg/providers/Microsoft.LoadTestService/loadtests
        # /loadtestsdk", "description": "", "displayName": DISPLAY_NAME, "loadTestConfig": { "engineSize": "m",
        # "engineInstances": 1, "splitAllCSVs": False, }, "secrets": {}, "environmentVariables": {},
        # "passFailCriteria": {"passFailMetrics": {}}, "keyvaultReferenceIdentityType": "SystemAssigned",
        # "keyvaultReferenceIdentityId": None, } ) test your code here, for example: result = await client.xxx.xx(
        # ...) assert result is not None
