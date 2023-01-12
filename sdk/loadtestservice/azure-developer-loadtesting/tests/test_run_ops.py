# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from pathlib import Path

import pytest
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from testcase import LoadtestingPowerShellPreparer, LoadtestingTest
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher, set_custom_default_matcher

DISPLAY_NAME = "TestingResourcePyTest"
NON_EXISTING_RESOURCE = "nonexistingresource"

class TestRunOps(LoadtestingTest):

    def setup_loadtest(self, endpoint, test_id):
        admin_client = self.create_client(endpoint)

        admin_client.administration.create_or_update_test(
            test_id,
            {
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

        validation_poller = admin_client.administration.begin_upload_test_file(
            test_id, "sample.jmx", open(os.path.join(os.path.dirname(__file__), "sample.jmx"), "rb"),
            poll_for_validation_status=True
        )

        validation_poller.result(6000)

    def setup_test_run(self, endpoint, test_id, test_run_id):
        self.setup_loadtest(endpoint, test_id)

        run_client = self.create_client(endpoint)

        run_poller = run_client.test_run.begin_test_run(
            test_run_id,
            {
                "testId": test_id,
                "displayName": "My New Load Test Run from PyTest",
            },
        )
        run_poller.result(10800)

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_test_run_poller(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id):
        set_bodiless_matcher()

        self.setup_loadtest(loadtesting_endpoint, loadtesting_test_id)

        run_client = self.create_client(loadtesting_endpoint)

        run_poller = run_client.test_run.begin_test_run(
            loadtesting_test_run_id,
            {
                "testId": loadtesting_test_id,
                "displayName": "My New Load Test Run from PyTest",
            },
        )

        assert run_poller.get_initial_response() is not None

        result = run_poller.result(10800)
        assert result is not None

        assert run_poller.status() is not None
        assert run_poller.done() is True

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_test_run(self, loadtesting_endpoint, loadtesting_test_run_id):
        set_bodiless_matcher()

        run_client = self.create_client(loadtesting_endpoint)

        result = run_client.test_run.get_test_run(loadtesting_test_run_id)
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            run_client.test_run.get_test_run(NON_EXISTING_RESOURCE)

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_delete_test_run(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id):
        set_bodiless_matcher()

        self.setup_test_run(loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id)

        run_client = self.create_client(loadtesting_endpoint)

        result = run_client.test_run.delete_test_run(loadtesting_test_run_id)
        assert result is None

        with pytest.raises(ResourceNotFoundError):
            run_client.test_run.delete_test_run(NON_EXISTING_RESOURCE)


    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_test_run_file(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id):
        set_bodiless_matcher()

        self.setup_test_run(loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id)

        run_client = self.create_client(loadtesting_endpoint)

        result = run_client.test_run.get_test_run_file(loadtesting_test_run_id, "sample.jmx")
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            run_client.test_run.get_test_run_file(NON_EXISTING_RESOURCE, "sample.jmx")

        with pytest.raises(HttpResponseError):
            run_client.test_run.get_test_run_file(loadtesting_test_run_id, NON_EXISTING_RESOURCE)


    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_list_test_runs(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id):
        set_bodiless_matcher()

        self.setup_test_run(loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id)

        run_client = self.create_client(loadtesting_endpoint)

        result = run_client.test_run.list_test_runs()
        assert result is not None


    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_stop_test_run(self, loadtesting_endpoint):
        set_bodiless_matcher()

        self.setup_loadtest(loadtesting_endpoint, "new-load-test-from-pytest-abc")
        run_client = self.create_client(loadtesting_endpoint)

        try:
            run_client.test_run.delete_test_run("my-new-test-run-from-pytest")
        except ResourceNotFoundError:
            pass

        run_poller = run_client.test_run.begin_test_run(
            "my-new-test-run-from-pytest",
            {
                "testId": "new-load-test-from-pytest-abc",
                "displayName": "My New Load Test Run from PyTest",
            },
            poll_for_test_run_status=False
        )
        assert run_poller.get_initial_response() is not None

        result = run_client.test_run.stop_test_run("my-new-test-run-from-pytest")
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            run_client.test_run.stop_test_run(NON_EXISTING_RESOURCE)


    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_metrics(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id):
        set_bodiless_matcher()

        self.setup_test_run(loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id)
        run_client = self.create_client(loadtesting_endpoint)

        test_run_response = run_client.test_run.get_test_run(loadtesting_test_run_id)
        assert test_run_response is not None

        metric_namespaces = run_client.test_run.list_metric_namespaces(loadtesting_test_run_id)
        assert metric_namespaces is not None

        metric_definitions = run_client.test_run.list_metric_definitions(loadtesting_test_run_id,
                            metric_namespace=metric_namespaces["value"][0]["name"])
        assert metric_definitions is not None

        metrics = run_client.test_run.list_metrics(
            test_run_id=loadtesting_test_run_id,
            metricname=metric_definitions["value"][0]["name"],
            metric_namespace=metric_namespaces["value"][0]["name"],
            timespan=test_run_response["startDateTime"] + "/" + test_run_response["endDateTime"]
        )
        assert metrics is not None

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_create_or_update_app_component(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id, loadtesting_resource_id):
        set_bodiless_matcher()

        self.setup_test_run(loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id)

        run_client = self.create_client(loadtesting_endpoint)

        result = run_client.test_run.create_or_update_app_components(
            loadtesting_test_run_id,
            {
                "components":
                    {
                        loadtesting_resource_id:
                            {
                                "resourceId": loadtesting_resource_id,
                                "resourceName": "App-Service-Sample-Demo",
                                "resourceType": "Microsoft.Web/sites",
                                "kind": "web"
                            }
                    }
            }
        )
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            run_client.test_run.create_or_update_app_components(
                NON_EXISTING_RESOURCE,
                {
                    "components":
                        {
                            loadtesting_resource_id:
                                {
                                    "resourceId": loadtesting_resource_id,
                                    "resourceName": "App-Service-Sample-Demo",
                                    "resourceType": "Microsoft.Web/sites",
                                    "kind": "web"
                                }
                        }
                }
            )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_app_component(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id, loadtesting_resource_id):
        set_bodiless_matcher()
        self.setup_test_run(loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id)

        run_client = self.create_client(loadtesting_endpoint)

        result = run_client.test_run.get_app_components(loadtesting_test_run_id)
        assert result is not None

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_create_or_update_server_metrics_config(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id, loadtesting_resource_id):
        set_bodiless_matcher()
        self.setup_test_run(loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id)

        run_client = self.create_client(loadtesting_endpoint)

        result = run_client.test_run.create_or_update_server_metrics_config(
            loadtesting_test_run_id,
            {
                "metrics": {
                    loadtesting_resource_id: {
                        "resourceId": loadtesting_resource_id,
                        "metricNamespace": "microsoft.insights/components",
                        "displayDescription": "sample description",
                        "name": "requests/duration",
                        "aggregation": "Average",
                        "unit": None,
                        "resourceType": "microsoft.insights/components"
                    }
                }
            }
        )
        assert result is not None

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_server_metrics_config(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id, loadtesting_resource_id):
        set_bodiless_matcher()
        self.setup_test_run(loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id)

        run_client = self.create_client(loadtesting_endpoint)

        result = run_client.test_run.get_server_metrics_config(loadtesting_test_run_id)
        assert result is not None