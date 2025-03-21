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
from devtools_testutils import set_bodiless_matcher
from devtools_testutils.aio import recorded_by_proxy_async

DISPLAY_NAME = "TestingResourcePyTest"

class TestLoadTestAdministrationClient(LoadTestingAsyncTest):

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
    async def test_list_load_tests(self, loadtesting_endpoint):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.list_tests()
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
        result = await client.get_test_file(loadtesting_test_id, self.setup_file_name)
        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_list_test_files(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.list_test_files(loadtesting_test_id)
        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_delete_test_file(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.delete_test_file(loadtesting_test_id, "sample.jmx")
        assert result is None

        await self.close_admin_client()
    
    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_create_or_update_app_components(
        self, loadtesting_endpoint, loadtesting_test_id, loadtesting_app_component_id
    ):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.create_or_update_app_components(
            loadtesting_test_id,
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

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_get_app_components(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.get_app_components(loadtesting_test_id)
        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_create_or_update_server_metrics_config(
        self, loadtesting_endpoint, loadtesting_test_id, loadtesting_app_component_id
    ):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.create_or_update_server_metrics_config(
            loadtesting_test_id,
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

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_get_server_metrics_config(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()
        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.get_server_metrics_config(loadtesting_test_id)
        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    async def test_delete_load_test(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.delete_test(loadtesting_test_id)
        assert result is None

        await self.close_admin_client()
