# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import os
from pathlib import Path

from testcase import LoadtestingTest, LoadtestingPowerShellPreparer
from azure.core.exceptions import HttpResponseError
from azure.core.exceptions import ResourceNotFoundError

DISPLAY_NAME = "TestingResource"


class TestRunSmokeTest(LoadtestingTest):

    def create_run_prerequisite(self, endpoint):
        client = self.create_client(endpoint=endpoint)

        client.load_test_administration.create_or_update_test(
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

        client.load_test_administration.upload_test_file(
            "some-unique-test-id",
            "unique-image-file-id",
            open(os.path.join(Path(__file__).resolve().parent, "sample-image.jpg"), "rb")
        )

    def create_test_run(self, endpoint, test_run_name):

        self.create_run_prerequisite(endpoint=endpoint)

        client = self.create_client(endpoint=endpoint)
        client.load_test_runs.create_or_update_test(
            test_run_name,
            {
                "testId": "some-unique-test-id",
                "displayName": DISPLAY_NAME
            }
        )


    @LoadtestingPowerShellPreparer()
    def test_create_or_update_loadtest(self, loadtesting_endpoint):
        # create prerequisites
        self.create_run_prerequisite(endpoint=loadtesting_endpoint)

        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_runs.create_or_update_test(
            "some-unique-test-run-id",
            {
                "testId": "some-unique-test-id",
                "displayName": DISPLAY_NAME
            }
        )
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            client.load_test_runs.create_or_update_test(
                "another-unique-test-run-id",
                {
                    "testId": "some-non-existing-test-id",
                    "displayName": DISPLAY_NAME
                }
            )

    @LoadtestingPowerShellPreparer()
    def test_delete_test_run(self, loadtesting_endpoint):

        # creating test run
        self.create_test_run(endpoint=loadtesting_endpoint, test_run_name="some-unique-test-run-id")

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_runs.delete_test_run("some-unique-test-run-id")
        assert result is None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            client.load_test_runs.delete_test_run("some-non-existing-test-run-id")

    @LoadtestingPowerShellPreparer()
    def test_get_test_run(self, loadtesting_endpoint):

        # creating test run
        self.create_test_run(endpoint=loadtesting_endpoint, test_run_name="some-unique-test-run-id")

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_runs.get_test_run("some-unique-test-run-id")
        assert result is not None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            client.load_test_runs.get_test_run("some-non-existing-test-run-id")

    