# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from pathlib import Path

from testcase import LoadtestingTest, LoadtestingPowerShellPreparer

DISPLAY_NAME = "TestingResource"


class LoadtestingSmokeTest(LoadtestingTest):
    @LoadtestingPowerShellPreparer()
    def test_smoke_create_or_update_test(self, loadtesting_endpoint):
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.create_or_update_test(
            self.test_id,
            {
                "resourceId": f"/subscriptions/{self.subscription_id}/resourceGroups/yashika-rg/providers/Microsoft.LoadTestService/loadtests/loadtestsdk",
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
    def test_upload_test_file(self, loadtesting_endpoint):
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.upload_test_file(
            self.test_id, self.file_id, open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb")
        )
        assert result is not None

    @LoadtestingPowerShellPreparer()
    def test_create_or_update_app_components(self, loadtesting_endpoint):
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
                    }
                },
            },
        )
        assert result is not None

    @LoadtestingPowerShellPreparer()
    def test_create_or_update_test_run(self, loadtesting_endpoint):
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_runs.create_or_update_test(
            self.test_run_id,
            {
                "testId": self.test_id,
                "displayName": DISPLAY_NAME,
                "requestSamplers": [],
                "errors": [],
                "percentiles": ["90"],
                "groupByInterval": "5s",
            },
        )
        assert result is not None

    @LoadtestingPowerShellPreparer()
    def test_get_app_components(self, loadtesting_endpoint):
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.get_app_components(test_id=self.test_id)
        assert result is not None

        result = client.load_test_administration.get_app_components(name=self.app_component)
        assert result is not None
