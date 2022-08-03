# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from pathlib import Path

import pytest
from azure.core.exceptions import ResourceNotFoundError

from testcase import LoadtestingTest, LoadtestingPowerShellPreparer

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
            "some-unique-file-id",
            open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb")
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

    @LoadtestingPowerShellPreparer()
    def test_get_test_run_file(self, loadtesting_endpoint):
        # creating test run
        self.create_test_run(endpoint=loadtesting_endpoint, test_run_name="some-unique-test-run-id")

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_runs.get_test_run_file("some-unique-test-run-id", "some-unique-file-id")
        assert result is not None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            client.load_test_runs.get_test_run_file("some-non-existing-test-run-id", "some-unique-file-id")

    @LoadtestingPowerShellPreparer()
    def test_stop_test_run(self, loadtesting_endpoint):
        # creating test run
        self.create_test_run(endpoint=loadtesting_endpoint, test_run_name="some-unique-test-run-id")

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_runs.stop_test_run("some-unique-test-run-id")
        assert result is not None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            client.load_test_runs.stop_test_run("some-non-existing-test-run-id")

    @LoadtestingPowerShellPreparer()
    def test_get_test_run_client_metrics(self, loadtesting_endpoint):
        # creating test run
        self.create_test_run(endpoint=loadtesting_endpoint, test_run_name="some-unique-test-run-id")

        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_runs.get_test_run_client_metrics_filters(
            "some-unique-test-run-id"
        )
        assert result is not None

        result_metrics = client.load_test_runs.get_test_run_client_metrics(
            "some-unique-test-run-id",
            {
                "requestSamplers": ["GET"],
                "startTime": result['timeRange']['startTime'],
                "endTime": result['timeRange']['endTime']

            }
        )
        assert result_metrics is not None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            client.load_test_runs.get_test_run_client_metrics_filters(
                "some-non-existing-test-run-id"
            )

        # negative test
        with pytest.raises(ResourceNotFoundError):
            client.load_test_runs.get_test_run_client_metrics(
                "some-non-existing-test-run-id",
                {
                    "requestSamplers": ["GET"],
                    "startTime": result['timeRange']['startTime'],
                    "endTime": result['timeRange']['endTime']
                }
            )

    # @LoadtestingPowerShellPreparer()
    # def test_list_test_runs(self, loadtesting_endpoint):

    #     client = self.create_client(endpoint=loadtesting_endpoint)
    #     result = client.load_test_runs.list_test_runs(
    #         order_by="displayName asc",
    #     )

    #     print(result)