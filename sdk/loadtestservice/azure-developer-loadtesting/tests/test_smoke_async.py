# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import LoadtestingPowerShellPreparer
from testcase_async import LoadtestingAsyncTest
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_bodiless_matcher
import os

DISPLAY_NAME = "TestingResource"  # display name


class TestLoadtestingSmokeAsync(LoadtestingAsyncTest):
    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_smoke_create_or_update_test(
            self,
            loadtesting_endpoint,
            loadtesting_test_id,
            loadtesting_subscription_id
    ):
        set_bodiless_matcher()
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = await client.load_test_administration.create_or_update_test(
            loadtesting_test_id,
            {
                "resourceId": f"/subscriptions/{loadtesting_subscription_id}/resourceGroups/yashika-rg/providers/Microsoft.LoadTestService/loadtests/loadtestsdk",
                "description": "",
                "displayName": DISPLAY_NAME,
                "loadTestConfig": {
                    "engineSize": "m",
                    "engineInstances": 1,
                    "splitAllCSVs": False,
                },
                "secrets": {},
                "environmentVariables": {},
                "passFailCriteria": {"passFailMetrics": {}},
                "keyvaultReferenceIdentityType": "SystemAssigned",
                "keyvaultReferenceIdentityId": None,
            },
        )
        assert result is not None

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_create_or_update_app_components(
            self,
            loadtesting_endpoint,
            loadtesting_test_id,
            loadtesting_app_component,
            loadtesting_subscription_id
    ):
        set_bodiless_matcher()
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = await client.load_test_administration.create_or_update_app_components(
            loadtesting_app_component,
            {
                "name": "app_component",
                "testId": loadtesting_test_id,
                "value": {
                    f"/subscriptions/{loadtesting_subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample-Demo": {
                        "resourceId": f"/subscriptions/{loadtesting_subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample-Demo",
                        "resourceName": "App-Service-Sample-Demo",
                        "resourceType": "Microsoft.Web/sites",
                        "subscriptionId": loadtesting_subscription_id,
                    }
                },
            },
        )
        assert result is not None

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_app_components(
            self,
            loadtesting_endpoint,
            loadtesting_test_id,
            loadtesting_app_component
    ):
        set_bodiless_matcher()
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = await client.load_test_administration.get_app_components(test_id=loadtesting_test_id)
        assert result is not None

        result = client.load_test_administration.get_app_components(name=loadtesting_app_component)
        assert result is not None
