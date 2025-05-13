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

class TestLoadTestAdministrationOperations(LoadTestingAsyncTest):

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
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
    @pytest.mark.asyncio
    async def test_get_load_test(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.get_test(loadtesting_test_id)
        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_list_load_tests(self, loadtesting_endpoint):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.list_tests()
        assert result is not None
        items = [r async for r in result]
        assert len(items) > 0  # page has at least one item

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
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
    @pytest.mark.asyncio
    async def test_get_test_file(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.get_test_file(loadtesting_test_id, "sample.jmx")
        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_list_test_files(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.list_test_files(loadtesting_test_id)
        assert result is not None
        items = [r async for r in result]
        assert len(items) > 0  # page has at least one item

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_delete_test_file(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.delete_test_file(loadtesting_test_id, "sample.jmx")
        assert result is None

        await self.close_admin_client()
    
    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
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
    @pytest.mark.asyncio
    async def test_get_app_components(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.get_app_components(loadtesting_test_id)
        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
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
    @pytest.mark.asyncio
    async def test_get_server_metrics_config(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()
        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.get_server_metrics_config(loadtesting_test_id)
        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_delete_load_test(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.delete_test(loadtesting_test_id)
        assert result is None

        await self.close_admin_client()

class TestTestProfileAdministrationOperations(LoadTestingAsyncTest):

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
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
    @pytest.mark.asyncio
    async def test_get_load_test(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.get_test(loadtesting_test_id)
        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
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
    @pytest.mark.asyncio
    async def test_get_test_profile(self, loadtesting_endpoint, loadtesting_test_profile_id):
        set_bodiless_matcher()
            
        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.get_test_profile(loadtesting_test_profile_id)
        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_list_test_profiles(self, loadtesting_endpoint):
        set_bodiless_matcher()
            
        client = self.create_administration_client(loadtesting_endpoint)
        result = client.list_test_profiles()
        assert result is not None
        items = [r async for r in result]
        assert len(items) > 0

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_delete_test_profile(self, loadtesting_endpoint, loadtesting_test_profile_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.delete_test_profile(loadtesting_test_profile_id)
        assert result is None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_delete_load_test(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.delete_test(loadtesting_test_id)
        assert result is None

        await self.close_admin_client()
