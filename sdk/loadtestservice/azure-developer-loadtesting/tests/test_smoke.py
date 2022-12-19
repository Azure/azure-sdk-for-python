# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from pathlib import Path

from testcase import LoadtestingTest, LoadtestingPowerShellPreparer
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher, set_custom_default_matcher

DISPLAY_NAME = "TestingResource"


class TestLoadtestingSmoke(LoadtestingTest):
    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_smoke_create_or_update_test(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_subscription_id):
        set_bodiless_matcher()
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.create_or_update_test(
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
    @recorded_by_proxy
    def test_upload_test_file(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_file_id):
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Type,x-ms-client-request-id,x-ms-request-id"
        )
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.upload_test_file(
            loadtesting_test_id, loadtesting_file_id,
            open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb")
        )
        assert result is not None

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_create_or_update_loadtesting_app_components(
            self,
            loadtesting_endpoint,
            loadtesting_test_id,
            loadtesting_app_component,
            loadtesting_subscription_id
    ):
        set_bodiless_matcher()
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.create_or_update_app_components(
            loadtesting_app_component,
            {
                "name": "loadtesting_app_component",
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
    @recorded_by_proxy
    def test_create_or_update_test_run(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id):
        set_bodiless_matcher()
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_runs.create_or_update_test(
            loadtesting_test_run_id,
            {
                "testId": loadtesting_test_id,
                "displayName": DISPLAY_NAME,
                "requestSamplers": [],
                "errors": [],
                "percentiles": ["90"],
                "groupByInterval": "5s",
            },
        )
        assert result is not None

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_loadtesting_app_components(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_app_component):
        set_bodiless_matcher()
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.get_app_components(test_id=loadtesting_test_id)
        assert result is not None

        result = client.load_test_administration.get_app_components(name=loadtesting_app_component)
        assert result is not None
