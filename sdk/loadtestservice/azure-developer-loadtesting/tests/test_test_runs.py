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
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher

test_id = os.environ.get("TEST_ID", "000")
file_id = os.environ.get("FILE_ID", "000")
test_run_id = os.environ.get("TEST_RUN_ID", "000")
non_existing_test_run_id = "0000-0000"
subscription_id = os.environ.get("LOADTESTING_SUBSCRIPTION_ID", "000")
DISPLAY_NAME = "TestingResource"


class TestRunSmokeTest(LoadtestingTest):

    def create_run_prerequisite(self, endpoint):
        client = self.create_client(endpoint=endpoint)

        client.load_test_administration.create_or_update_test(
            test_id,
            {
                "resourceId": f"/subscriptions/{subscription_id}/resourceGroups/yashika-rg/providers/Microsoft.LoadTestService/loadtests/loadtestsdk",
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
            test_id,
            file_id,
            open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb")
        )

    def create_test_run(self, endpoint, test_run_name):
        self.create_run_prerequisite(endpoint=endpoint)

        client = self.create_client(endpoint=endpoint)
        client.load_test_runs.create_or_update_test(
            test_run_name,
            {
                "testId": test_id,
                "displayName": DISPLAY_NAME
            }
        )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_create_or_update_loadtest(self, loadtesting_endpoint):
        set_bodiless_matcher()
        # create prerequisites
        self.create_run_prerequisite(endpoint=loadtesting_endpoint)

        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_runs.create_or_update_test(
            test_run_id,
            {
                "testId": test_id,
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
    @recorded_by_proxy
    def test_delete_test_run(self, loadtesting_endpoint):
        set_bodiless_matcher()
        # creating test run
        self.create_test_run(endpoint=loadtesting_endpoint, test_run_name=test_run_id)

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_runs.delete_test_run(test_run_id)
        assert result is None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            client.load_test_runs.delete_test_run(non_existing_test_run_id)

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_test_run(self, loadtesting_endpoint):
        set_bodiless_matcher()
        # creating test run
        self.create_test_run(endpoint=loadtesting_endpoint, test_run_name=test_run_id)

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_runs.get_test_run(test_run_id)
        assert result is not None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            client.load_test_runs.get_test_run(non_existing_test_run_id)

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_test_run_file(self, loadtesting_endpoint):
        set_bodiless_matcher()
        # creating test run
        self.create_test_run(endpoint=loadtesting_endpoint, test_run_name=test_run_id)

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_runs.get_test_run_file(test_run_id, file_id)
        assert result is not None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            client.load_test_runs.get_test_run_file(non_existing_test_run_id, file_id)

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_stop_test_run(self, loadtesting_endpoint):
        set_bodiless_matcher()
        # creating test run
        self.create_test_run(endpoint=loadtesting_endpoint, test_run_name=test_run_id)

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_runs.stop_test_run(test_run_id)
        assert result is not None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            client.load_test_runs.stop_test_run(non_existing_test_run_id)

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_test_run_client_metrics(self, loadtesting_endpoint):
        set_bodiless_matcher()
        # creating test run
        self.create_test_run(endpoint=loadtesting_endpoint, test_run_name=test_run_id)

        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_runs.get_test_run_client_metrics_filters(
            test_run_id
        )
        assert result is not None

        result_metrics = client.load_test_runs.get_test_run_client_metrics(
            test_run_id,
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
                non_existing_test_run_id
            )

        # negative test
        with pytest.raises(ResourceNotFoundError):
            client.load_test_runs.get_test_run_client_metrics(
                non_existing_test_run_id,
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
