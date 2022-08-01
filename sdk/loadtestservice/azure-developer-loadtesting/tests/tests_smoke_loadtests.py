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


class TestOperationsSmokeTest(LoadtestingTest):

    @LoadtestingPowerShellPreparer()
    def test_create_or_update_loadtest(self, loadtesting_endpoint):
        # positive testing
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.create_or_update_test(
            "some-unique-test-id",
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

        # negative testing
        with pytest.raises(HttpResponseError):
            client.load_test_administration.create_or_update_test(
                "some-test-id",
                {
                    "resourceId": f"/subscriptions/{self.subscription_id}/resourceGroups/yashika-rg/providers/Microsoft.LoadTestService/loadtests/loadtestsdk",
                    "description": "",
                    "displayName": DISPLAY_NAME + "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz",
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

    @LoadtestingPowerShellPreparer()
    def test_delete_loadtest(self, loadtesting_endpoint):
        # creating a mock test to delete
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.create_or_update_test(
            "to-be-deleted-test-id",
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

        # positive testing
        result = client.load_test_administration.delete_load_test(
            test_id="to-be-deleted-test-id"
        )
        assert result is None

        # negative testing
        with pytest.raises(ResourceNotFoundError):
            client.load_test_administration.delete_load_test(
                test_id="non-existing-test-id"
            )
