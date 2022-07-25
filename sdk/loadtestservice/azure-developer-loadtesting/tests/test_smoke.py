# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from testcase import LoadtestingTest, LoadtestingPowerShellPreparer
from pathlib import Path
import os

TEST_ID = "a011890b-0201-004d-010d"  # ID to be assigned to a test
FILE_ID = "a012b234-1230-ab00-0040"  # ID to be assigned to file uploaded
TEST_RUN_ID = "08673e89-3285-46a1-9c6b"  # ID to be assigned to a test run
APP_COMPONENT = "01730263-6671-4216-b283"  # ID of the APP Component
DISPLAY_NAME = "new_namespace-new-namespace"  # display name
SUBSCRIPTION_ID = "fake-subs-id"


class LoadtestingSmokeTest(LoadtestingTest):

    @LoadtestingPowerShellPreparer()
    def test_smoke_create_or_update_test(self, loadtesting_endpoint):
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.create_or_update_test(
            TEST_ID,
            {
                "resourceId": f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/yashika-rg/providers/Microsoft.LoadTestService/loadtests/loadtestsdk",
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
            }
        )
        assert result is not None

    @LoadtestingPowerShellPreparer()
    def test_upload_test_file(self, loadtesting_endpoint):
        client = self.create_client(endpoint=loadtesting_endpoint)
        body = {"file": open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb")}
        result = client.load_test_administration.upload_test_file(TEST_ID, FILE_ID, body)
        assert result is not None

    @LoadtestingPowerShellPreparer()
    def test_create_or_update_app_components(self, loadtesting_endpoint):
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.create_or_update_app_components(
            APP_COMPONENT,
            {
                "name": "app_component",
                "testId": TEST_ID,
                "value": {
                    f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample-Demo": {
                        "resourceId": f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample-Demo",
                        "resourceName": "App-Service-Sample-Demo",
                        "resourceType": "Microsoft.Web/sites",
                        "subscriptionId": SUBSCRIPTION_ID,
                    }
                },
            },
        )
        assert result is not None

    @LoadtestingPowerShellPreparer()
    def test_create_or_update_test_run(self, loadtesting_endpoint):
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_runs.create_or_update_test(
            TEST_RUN_ID,
            {
                "testId": TEST_ID,
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
        result = client.load_test_administration.get_app_components(
            test_id=TEST_ID
        )
        assert result is not None

        result = client.load_test_administration.get_app_components(
            name=APP_COMPONENT
        )
        assert result is not None
