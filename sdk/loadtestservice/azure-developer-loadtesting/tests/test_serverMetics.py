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


class ServerMetricsSmokeTest(LoadtestingTest):

    def prepare(self, endpoint):
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
            }
        )

        client.load_test_administration.upload_test_file(
            "some-unique-test-id",
            "some-unique-file-id",
            open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb")
        )

        client.load_test_runs.create_or_update_test(
            "some-unique-test-run-id",
            {
                "testId": "some-unique-test-id",
                "displayName": DISPLAY_NAME
            }
        )

    @LoadtestingPowerShellPreparer()
    def test_create_or_update_server_metrics_config(self, loadtesting_endpoint):
        self.prepare(endpoint=loadtesting_endpoint)

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.create_or_update_server_metrics_config(
            "some-unique-server-metrics-config-id",
            {
                "testRunId": "some-unique-test-run-id",
            }
        )
        print(result)
        assert result is not None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            client.load_test_administration.create_or_update_server_metrics_config(
                "some-unique-server-metrics-config-id",
                {
                    "testRunId": "some-non-existing-test-run-id",
                }
            )

    @LoadtestingPowerShellPreparer()
    def test_delete_server_metrics_config(self, loadtesting_endpoint):
        self.prepare(endpoint=loadtesting_endpoint)

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.delete_server_metrics_config(
            "some-unique-server-metrics-config-id"
        )
        assert result is None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            client.load_test_administration.delete_server_metrics_config(
                "some-unique-server-metrics-config-id"
            )

    @LoadtestingPowerShellPreparer()
    def test_get_server_metrics_config(self, loadtesting_endpoint):
        self.prepare(endpoint=loadtesting_endpoint)

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)

        result = client.load_test_administration.get_server_metrics_config(
            test_id="some-unique-test-id",
        )
        assert result is not None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            client.load_test_administration.get_server_metrics_config(
                test_id="some-non-existing-test-id",
            )

    @LoadtestingPowerShellPreparer()
    def test_get_server_default_metrics_config(self, loadtesting_endpoint):
        self.prepare(endpoint=loadtesting_endpoint)

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)

        result = client.load_test_administration.get_server_default_metrics_config()
        assert result is not None

    @LoadtestingPowerShellPreparer()
    def test_list_supported_resource_types(self, loadtesting_endpoint):
        self.prepare(endpoint=loadtesting_endpoint)

        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.list_supported_resource_types()
        print(result)
        assert result is not None
