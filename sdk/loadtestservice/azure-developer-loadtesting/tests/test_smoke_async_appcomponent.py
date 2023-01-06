# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from testcase import LoadtestingPowerShellPreparer
from testcase_async import LoadtestingAsyncTest
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_bodiless_matcher
import pytest
import os

DISPLAY_NAME = "TestingResource"  # display name


class TestAppComponentAsync(LoadtestingAsyncTest):

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
        # positive testing
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = await client.load_test_administration.create_or_update_app_components(
            loadtesting_app_component,
            {
                "name": "app_componentx",
                "testId": loadtesting_test_id,
                "value": {
                    f"/subscriptions/{loadtesting_subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample-Demo": {
                        "resourceId": f"/subscriptions/{loadtesting_subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample-Demo",
                        "resourceName": "App-Service-Sample-Demo",
                        "resourceType": "Microsoft.Web/sites",
                        "subscriptionId": loadtesting_subscription_id,
                    },
                    f"subscriptions/{loadtesting_subscription_id}/resourceGroups/Demo-App-Service-Sample-rg/providers/Microsoft.Web/sites/Demo-App-Service-Sample": {
                        "resourceId": f"/subscriptions/{loadtesting_subscription_id}/resourceGroups/Demo-App-Service-Sample-rg/providers/Microsoft.Web/sites/Demo-App-Service-Sample",
                        "resourceName": "Demo-App-Service-Sample",
                        "resourceType": "Microsoft.Web/sites",
                        "subscriptionId": loadtesting_subscription_id,
                    },
                    f"/subscriptions/{loadtesting_subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample": {
                        "resourceId": f"/subscriptions/{loadtesting_subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample",
                        "resourceName": "App-Service-Sample-Demo",
                        "resourceType": "Microsoft.Web/sites",
                        "subscriptionId": loadtesting_subscription_id,
                    }
                },
            },
        )
        assert result is not None

        # negative testing
        with pytest.raises(HttpResponseError):
            await client.load_test_administration.create_or_update_app_components(
                loadtesting_app_component,
                {
                    "name": "app_componentx",
                    "value": {
                        f"/subscriptions/{loadtesting_subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample": {
                            "resourceId": f"/subscriptions/{loadtesting_subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample",
                            "resourceName": "App-Service-Sample-Demo",
                            "resourceType": "Microsoft.Web/sites",
                            "subscriptionId": loadtesting_subscription_id,
                        }
                    },
                },
            )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_delete_app_component(self, loadtesting_endpoint, loadtesting_app_component):
        set_bodiless_matcher()

        #positive testing
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = await client.load_test_administration.delete_app_components(
            loadtesting_app_component
        )
        assert result is None

        #positive testing
        with pytest.raises(HttpResponseError):
            client = self.create_client(endpoint=loadtesting_endpoint)
            result = await client.load_test_administration.delete_app_components(
                loadtesting_app_component
            )
        assert result is None


    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_app_components(
            self,
            loadtesting_endpoint,
            loadtesting_test_id,
            loadtesting_app_component,
            loadtesting_subscription_id
    ):
        set_bodiless_matcher()
        # creating an app component array to help in testing
        client = self.create_client(endpoint=loadtesting_endpoint)
        await client.load_test_administration.create_or_update_app_components(
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
                    },
                    f"subscriptions/{loadtesting_subscription_id}/resourceGroups/Demo-App-Service-Sample-rg/providers/Microsoft.Web/sites/Demo-App-Service-Sample": {
                        "resourceId": f"/subscriptions/{loadtesting_subscription_id}/resourceGroups/Demo-App-Service-Sample-rg/providers/Microsoft.Web/sites/Demo-App-Service-Sample",
                        "resourceName": "Demo-App-Service-Sample",
                        "resourceType": "Microsoft.Web/sites",
                        "subscriptionId": loadtesting_subscription_id,
                    },
                    f"/subscriptions/{loadtesting_subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample": {
                        "resourceId": f"/subscriptions/{loadtesting_subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample",
                        "resourceName": "App-Service-Sample-Demo",
                        "resourceType": "Microsoft.Web/sites",
                        "subscriptionId": loadtesting_subscription_id,
                    }
                },
            },
        )

        # positive testing
        result = await client.load_test_administration.get_app_components(
            test_id=loadtesting_test_id
        )
        assert result is not None

        result = await client.load_test_administration.get_app_components(
            name=loadtesting_app_component
        )
        assert result is not None

        # negative testing
        with pytest.raises(ResourceNotFoundError):
            await client.load_test_administration.get_app_components(
                test_id="abcdefghijklmnopqrstuvwxyz"
            )

        with pytest.raises(HttpResponseError):
            await client.load_test_administration.get_app_components(
                name="123"
            )
