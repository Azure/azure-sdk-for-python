# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from pathlib import Path

import pytest

from testcase import LoadTestingPreparer
from testcase_async import LoadTestingAsyncTest
from devtools_testutils import set_bodiless_matcher, set_custom_default_matcher
from devtools_testutils.aio import recorded_by_proxy_async

DISPLAY_NAME = "TestingResourcePyTest"
NON_EXISTING_RESOURCE = "nonexistingresource"

class TestLoadTestRunOperations(LoadTestingAsyncTest):

    # Pre-requisite: Test creation is needed for test run related tests
    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_create_or_update_load_test(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.create_or_update_test(
            loadtesting_test_id,
            {
                "description": "",
                "displayName": DISPLAY_NAME,
                "loadTestConfiguration": {
                    "engineInstances": 1,
                    "splitAllCSVs": False,
                },
                "passFailCriteria": {
                    "passFailMetrics": {
                        "condition1": {"clientmetric": "response_time_ms", "aggregate": "avg", "condition": ">", "value": 300},
                        "condition2": {"clientmetric": "error", "aggregate": "percentage", "condition": ">", "value": 50},
                        "condition3": {
                            "clientmetric": "latency",
                            "aggregate": "avg",
                            "condition": ">",
                            "value": 200,
                            "requestName": "GetCustomerDetails",
                        },
                    }
                },
                "secrets": {},
                "environmentVariables": {"my-variable": "value"},
        })

        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_get_load_test(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.get_test(loadtesting_test_id)
        assert result is not None

        await self.close_admin_client()
    
    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_upload_test_file(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        poller = await client.begin_upload_test_file(
            loadtesting_test_id,
            "sample.jmx",
            open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb"),
        )

        result = await poller.result()
        assert poller.status() is not None
        assert result is not None
        assert poller.done() is True

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_get_test_file(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.get_test_file(loadtesting_test_id, "sample.jmx")
        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_begin_test_run(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_test_run_id):
        set_bodiless_matcher()

        run_client = self.create_run_client(loadtesting_endpoint)

        run_poller = await run_client.begin_test_run(
            loadtesting_test_run_id,
            {
                "testId": loadtesting_test_id,
                "displayName": "My New Load Test Run from PyTest",
            },
        )

        result = await run_poller.result()
        assert result is not None

        assert run_poller.status() is not None
        assert run_poller.done() is True

        await self.close_run_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_get_test_run(self, loadtesting_endpoint, loadtesting_test_run_id):
        set_bodiless_matcher()

        run_client = self.create_run_client(loadtesting_endpoint)

        result = await run_client.get_test_run(loadtesting_test_run_id)
        assert result is not None

        await self.close_run_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_get_test_run_file(self, loadtesting_endpoint, loadtesting_test_run_id):
        set_bodiless_matcher()

        run_client = self.create_run_client(loadtesting_endpoint)

        result = run_client.get_test_run_file(loadtesting_test_run_id, "sample.jmx")
        assert result is not None

        await self.close_run_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_list_test_runs(self, loadtesting_endpoint):
        set_bodiless_matcher()

        run_client = self.create_run_client(loadtesting_endpoint)

        result = run_client.list_test_runs()
        assert result is not None
        items = [item async for item in result]
        assert len(items) > 0 # Atleast one item in the page

        await self.close_run_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_get_metrics(self, loadtesting_endpoint, loadtesting_test_run_id):
        # NOTE: During recording the query parameters are not sanitized
        # but they are sanitized during playback causing failures. Hence
        # they are ignored right now.
        set_custom_default_matcher(ignored_query_parameters="metricNamespace")

        run_client = self.create_run_client(loadtesting_endpoint)

        test_run_response = await run_client.get_test_run(loadtesting_test_run_id)
        assert test_run_response is not None

        metric_namespaces = await run_client.get_metric_namespaces(loadtesting_test_run_id)
        assert metric_namespaces is not None

        metric_definitions = await run_client.get_metric_definitions(
            loadtesting_test_run_id, metric_namespace=metric_namespaces["value"][0]["name"]
        )
        assert metric_definitions is not None

        metrics = run_client.list_metrics(
            test_run_id=loadtesting_test_run_id,
            metric_name=metric_definitions["value"][0]["name"],
            metric_namespace=metric_namespaces["value"][0]["name"],
            time_interval=test_run_response["startDateTime"] + "/" + test_run_response["endDateTime"],
        )
        assert metrics is not None

        await self.close_run_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_create_or_update_app_component(
        self, loadtesting_endpoint, loadtesting_test_run_id, loadtesting_app_component_id
    ):
        set_bodiless_matcher()

        run_client = self.create_run_client(loadtesting_endpoint)

        result = await run_client.create_or_update_app_components(
            loadtesting_test_run_id,
            {
                "components": {
                    loadtesting_app_component_id: {
                        "resourceId": loadtesting_app_component_id,
                        "resourceName": "contoso-sampleapp",
                        "resourceType": "Microsoft.Web/sites",
                        "kind": "web",
                    }
                }
            },
        )
        assert result is not None

        await self.close_run_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_get_app_component(
        self, loadtesting_endpoint, loadtesting_test_run_id
    ):
        set_bodiless_matcher()

        run_client = self.create_run_client(loadtesting_endpoint)

        result = await run_client.get_app_components(loadtesting_test_run_id)
        assert result is not None

        await self.close_run_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_create_or_update_server_metrics_config(
        self, loadtesting_endpoint, loadtesting_test_run_id, loadtesting_app_component_id
    ):
        set_bodiless_matcher()

        run_client = self.create_run_client(loadtesting_endpoint)

        result = await run_client.create_or_update_server_metrics_config(
            loadtesting_test_run_id,
            {
                "metrics": {
                    loadtesting_app_component_id: {
                        "resourceId": loadtesting_app_component_id,
                        "metricNamespace": "microsoft.insights/components",
                        "displayDescription": "sample description",
                        "name": "requests/duration",
                        "aggregation": "Average",
                        "unit": None,
                        "resourceType": "microsoft.insights/components",
                    }
                }
            },
        )
        assert result is not None

        await self.close_run_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_get_server_metrics_config(
        self, loadtesting_endpoint, loadtesting_test_run_id
    ):
        set_bodiless_matcher()

        run_client = self.create_run_client(loadtesting_endpoint)

        result = await run_client.get_server_metrics_config(loadtesting_test_run_id)
        assert result is not None

        await self.close_run_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_stop_test_run(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        test_run_id = "sample-test-run-2"
        run_client = self.create_run_client(loadtesting_endpoint)

        run_poller = await run_client.begin_test_run(
            test_run_id,
            {
                "testId": loadtesting_test_id,
                "displayName": "My New Load Test Run from PyTest",
            },
        )

        result = await run_client.stop_test_run(test_run_id)
        assert result is not None

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_delete_test_run(self, loadtesting_endpoint, loadtesting_test_run_id):
        set_bodiless_matcher()

        run_client = self.create_run_client(loadtesting_endpoint)

        result = await run_client.delete_test_run(loadtesting_test_run_id)
        assert result is None

        await self.close_run_client()
    
    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_delete_test(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)

        result = await client.delete_test(loadtesting_test_id)
        assert result is None

        await self.close_admin_client()

class TestTestProfileRunOperations(LoadTestingAsyncTest):

    # Pre-requisite: Test & Test Profile creation is needed for test profile run related tests
    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_create_or_update_load_test(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.create_or_update_test(
            loadtesting_test_id,
            {
                "description": "",
                "displayName": DISPLAY_NAME,
                "loadTestConfiguration": {
                    "engineInstances": 1,
                    "splitAllCSVs": False,
                },
                "passFailCriteria": {
                    "passFailMetrics": {
                        "condition1": {"clientmetric": "response_time_ms", "aggregate": "avg", "condition": ">", "value": 300},
                        "condition2": {"clientmetric": "error", "aggregate": "percentage", "condition": ">", "value": 50},
                        "condition3": {
                            "clientmetric": "latency",
                            "aggregate": "avg",
                            "condition": ">",
                            "value": 200,
                            "requestName": "GetCustomerDetails",
                        },
                    }
                },
                "secrets": {},
                "environmentVariables": {"my-variable": "value"},
            },
        )

        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_get_load_test(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.get_test(loadtesting_test_id)
        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_upload_test_file(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        poller = await client.begin_upload_test_file(
            loadtesting_test_id,
            "sample.jmx",
            open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb"),
        )

        result = await poller.result()
        assert poller.status() is not None
        assert result is not None
        assert poller.done() is True

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_get_test_file(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.get_test_file(loadtesting_test_id, "sample.jmx")
        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_create_or_update_test_profile(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_test_profile_id, loadtesting_target_resource_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.create_or_update_test_profile(
            loadtesting_test_profile_id,
            {
                "description": "Sample Test Profile Description",
                "displayName": "My New Test Profile",
                "testId": loadtesting_test_id,
                "targetResourceId": loadtesting_target_resource_id,
                "targetResourceConfigurations": {
                    "kind": "FunctionsFlexConsumption",
                    "configurations": {
                        "config1": {
                            "instanceMemoryMB": 2048,
                            "httpConcurrency": 20
                        },
                        "config2": {
                            "instanceMemoryMB": 4096,
                            "httpConcurrency": 100
                        },
                    }
                }
            },
        )
        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_get_test_profile(self, loadtesting_endpoint, loadtesting_test_profile_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.get_test_profile(loadtesting_test_profile_id)
        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_begin_test_profile_run(self, loadtesting_endpoint, loadtesting_test_profile_id, loadtesting_test_profile_run_id):
        set_bodiless_matcher()

        run_client = self.create_run_client(loadtesting_endpoint)

        run_poller = await run_client.begin_test_profile_run(
            loadtesting_test_profile_run_id,
            {
                "testProfileId": loadtesting_test_profile_id,
                "displayName": "My New Test Profile Run from PyTest",
            },
        )

        result = await run_poller.result()
        assert result is not None

        assert run_poller.status() is not None
        assert run_poller.done() is True

        await self.close_run_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_get_test_profile_run(self, loadtesting_endpoint, loadtesting_test_profile_run_id):
        set_bodiless_matcher()

        run_client = self.create_run_client(loadtesting_endpoint)

        result = await run_client.get_test_profile_run(loadtesting_test_profile_run_id)
        assert result is not None
        assert len(result["recommendations"]) > 0

        await self.close_run_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_stop_test_profile_run(self, loadtesting_endpoint, loadtesting_test_profile_id):
        set_bodiless_matcher()

        test_profile_run_id = "sample-test-profile-run-2"
        run_client = self.create_run_client(loadtesting_endpoint)

        run_poller = await run_client.begin_test_profile_run(
            test_profile_run_id,
            {
                "testProfileId": loadtesting_test_profile_id,
                "displayName": "My New Test Profile Run from PyTest",
            },
        )

        result = await run_client.stop_test_profile_run(test_profile_run_id)
        assert result is not None

        # Clean-up
        await run_client.delete_test_profile_run(test_profile_run_id)

        await self.close_run_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_delete_test_profile_run(self, loadtesting_endpoint, loadtesting_test_profile_run_id):
        set_bodiless_matcher()

        run_client = self.create_run_client(loadtesting_endpoint)

        result = await run_client.delete_test_profile_run(loadtesting_test_profile_run_id)
        assert result is None

        await self.close_run_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_delete_test_profile(self, loadtesting_endpoint, loadtesting_test_profile_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)

        result = await client.delete_test_profile(loadtesting_test_profile_id)
        assert result is None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_delete_test(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)

        result = await client.delete_test(loadtesting_test_id)
        assert result is None

        await self.close_admin_client()
