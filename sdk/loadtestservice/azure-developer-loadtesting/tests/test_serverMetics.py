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
from devtools_testutils import recorded_by_proxy, set_custom_default_matcher

test_id = os.environ.get("TEST_ID", "000")
file_id = os.environ.get("FILE_ID", "000")
test_run_id = os.environ.get("TEST_RUN_ID", "000")
non_existing_test_id = "0000-0000"
non_existing_test_run_id = "0000-0000"
non_existing_file_id = "000-000"
subscription_id = os.environ.get("LOADTESTING_SUBSCRIPTION_ID", "000")
DISPLAY_NAME = "TestingResource"


class TestServerMetricsSmoke(LoadtestingTest):

    def prepare(self, endpoint):
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
            }
        )

        client.load_test_administration.upload_test_file(
            test_id,
            file_id,
            open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb")
        )

        client.load_test_runs.create_or_update_test(
            test_run_id,
            {
                "testId": test_id,
                "displayName": DISPLAY_NAME
            }
        )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_create_or_update_server_metrics_config(self, loadtesting_endpoint):
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Type,x-ms-client-request-id,x-ms-request-id"
        )
        self.prepare(endpoint=loadtesting_endpoint)

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.create_or_update_server_metrics_config(
            "some-unique-server-metrics-config-id",
            {
                "testRunId": test_run_id,
            }
        )
        assert result is not None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            client.load_test_administration.create_or_update_server_metrics_config(
                "some-unique-server-metrics-config-id",
                {
                    "testRunId": non_existing_test_run_id,
                }
            )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_delete_server_metrics_config(self, loadtesting_endpoint):
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Type,x-ms-client-request-id,x-ms-request-id"
        )
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
    @recorded_by_proxy
    def test_get_server_metrics_config(self, loadtesting_endpoint):
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Type,x-ms-client-request-id,x-ms-request-id"
        )
        self.prepare(endpoint=loadtesting_endpoint)

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)

        result = client.load_test_administration.get_server_metrics_config(
            test_id=test_id,
        )
        assert result is not None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            client.load_test_administration.get_server_metrics_config(
                test_id=non_existing_test_id,
            )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_server_default_metrics_config(self, loadtesting_endpoint):
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Type,x-ms-client-request-id,x-ms-request-id"
        )
        self.prepare(endpoint=loadtesting_endpoint)

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)

        result = client.load_test_administration.get_server_default_metrics_config()
        assert result is not None

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_list_supported_resource_types(self, loadtesting_endpoint):
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Type,x-ms-client-request-id,x-ms-request-id"
        )
        self.prepare(endpoint=loadtesting_endpoint)

        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.list_supported_resource_types()
        assert result is not None
