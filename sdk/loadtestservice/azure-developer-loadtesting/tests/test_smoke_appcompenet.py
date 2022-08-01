# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest

from testcase import LoadtestingTest, LoadtestingPowerShellPreparer
from azure.core.exceptions import HttpResponseError
from azure.core.exceptions import ResourceNotFoundError

DISPLAY_NAME = "TestingResource"


class AppComponentTestingSmokeTest(LoadtestingTest):

    @LoadtestingPowerShellPreparer()
    def test_create_or_update_app_components(self, loadtesting_endpoint):

        # positive testing
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.create_or_update_app_components(
            self.app_component,
            {
                "name": "app_component",
                "testId": self.test_id,
                "value": {
                    f"/subscriptions/{self.subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample-Demo": {
                        "resourceId": f"/subscriptions/{self.subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample-Demo",
                        "resourceName": "App-Service-Sample-Demo",
                        "resourceType": "Microsoft.Web/sites",
                        "subscriptionId": self.subscription_id,
                    },
                    f"subscriptions/{self.subscription_id}/resourceGroups/Demo-App-Service-Sample-rg/providers/Microsoft.Web/sites/Demo-App-Service-Sample": {
                        "resourceId": f"/subscriptions/{self.subscription_id}/resourceGroups/Demo-App-Service-Sample-rg/providers/Microsoft.Web/sites/Demo-App-Service-Sample",
                        "resourceName": "Demo-App-Service-Sample",
                        "resourceType": "Microsoft.Web/sites",
                        "subscriptionId": self.subscription_id,
                    },
                    f"/subscriptions/{self.subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample": {
                        "resourceId": f"/subscriptions/{self.subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample",
                        "resourceName": "App-Service-Sample-Demo",
                        "resourceType": "Microsoft.Web/sites",
                        "subscriptionId": self.subscription_id,
                    }
                },
            },
        )
        assert result is not None

        # negative testing
        with pytest.raises(HttpResponseError):
            client.load_test_administration.create_or_update_app_components(
                self.app_component,
                {
                    "name": "app_component",
                    "value": {
                        f"/subscriptions/{self.subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample": {
                            "resourceId": f"/subscriptions/{self.subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample",
                            "resourceName": "App-Service-Sample-Demo",
                            "resourceType": "Microsoft.Web/sites",
                            "subscriptionId": self.subscription_id,
                        }
                    },
                },
            )

    @LoadtestingPowerShellPreparer()
    def test_delete_app_component(self, loadtesting_endpoint):

        #positive testing
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.delete_app_components(
            self.app_component
        )
        assert result is None

        #positive testing
        with pytest.raises(HttpResponseError):
            client = self.create_client(endpoint=loadtesting_endpoint)
            result = client.load_test_administration.delete_app_components(
                self.app_component
            )
        assert result is None


    @LoadtestingPowerShellPreparer()
    def test_get_app_components(self, loadtesting_endpoint):

        # creating an app component array to help in testing
        client = self.create_client(endpoint=loadtesting_endpoint)
        client.load_test_administration.create_or_update_app_components(
            self.app_component,
            {
                "name": "app_component",
                "testId": self.test_id,
                "value": {
                    f"/subscriptions/{self.subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample-Demo": {
                        "resourceId": f"/subscriptions/{self.subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample-Demo",
                        "resourceName": "App-Service-Sample-Demo",
                        "resourceType": "Microsoft.Web/sites",
                        "subscriptionId": self.subscription_id,
                    },
                    f"subscriptions/{self.subscription_id}/resourceGroups/Demo-App-Service-Sample-rg/providers/Microsoft.Web/sites/Demo-App-Service-Sample": {
                        "resourceId": f"/subscriptions/{self.subscription_id}/resourceGroups/Demo-App-Service-Sample-rg/providers/Microsoft.Web/sites/Demo-App-Service-Sample",
                        "resourceName": "Demo-App-Service-Sample",
                        "resourceType": "Microsoft.Web/sites",
                        "subscriptionId": self.subscription_id,
                    },
                    f"/subscriptions/{self.subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample": {
                        "resourceId": f"/subscriptions/{self.subscription_id}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample",
                        "resourceName": "App-Service-Sample-Demo",
                        "resourceType": "Microsoft.Web/sites",
                        "subscriptionId": self.subscription_id,
                    }
                },
            },
        )

        # positive testing
        result = client.load_test_administration.get_app_components(
            test_id=self.test_id
        )
        assert result is not None

        result = client.load_test_administration.get_app_components(
            name=self.app_component
        )
        assert result is not None

        # negative testing
        with pytest.raises(ResourceNotFoundError):
            client.load_test_administration.get_app_components(
                test_id="abcdefghijklmnopqrstuvwxyz"
            )

        with pytest.raises(HttpResponseError):
            client.load_test_administration.get_app_components(
                name="123"
            )
