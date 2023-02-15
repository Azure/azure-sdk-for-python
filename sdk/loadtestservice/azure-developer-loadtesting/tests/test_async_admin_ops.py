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

from testcase import LoadtestingPowerShellPreparer
from testcase_async import LoadtestingAsyncTest
from devtools_testutils import set_bodiless_matcher, set_custom_default_matcher
from devtools_testutils.aio import recorded_by_proxy_async

DISPLAY_NAME = "TestingResourcePyTest"
NON_EXISTING_RESOURCE = "nonexistingresource"
class TestLoadTestAdministrationClient(LoadtestingAsyncTest):

    async def setup_create_load_test(self, endpoint):
        self.setup_load_test_id = "pytest_setup_load_test_id"
        client = self.create_administration_client(endpoint)

        await client.create_or_update_test(
            self.setup_load_test_id,
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

    async def setup_upload_test_file(self, endpoint):
        client = self.create_administration_client(endpoint)
        self.setup_file_name = "sample.jmx"
        await client.begin_upload_test_file(self.setup_load_test_id, "sample.jmx", open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb"))

    async def setup_app_components(self, endpoint, resource_id):
        client = self.create_administration_client(endpoint)

        await client.create_or_update_app_components(
            self.setup_load_test_id,
            {
                "components": {
                    resource_id: {
                        "resourceId": resource_id,
                        "resourceName": "App-Service-Sample-Demo",
                        "resourceType": "Microsoft.Web/sites",
                        "kind": "web",
                    }
                },
            },
        )
    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_create_or_update_load_test(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.create_or_update_test(
            loadtesting_test_id,
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
            },
        )
        assert result is not None

        with pytest.raises(HttpResponseError):
            await client.create_or_update_test(
                loadtesting_test_id,
                {
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
    @recorded_by_proxy_async
    async def test_delete_load_test(self, loadtesting_endpoint):
        set_bodiless_matcher()
        await self.setup_create_load_test(loadtesting_endpoint)

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.delete_test(self.setup_load_test_id)
        assert result is None

        with pytest.raises(ResourceNotFoundError):
            await client.delete_test(NON_EXISTING_RESOURCE)

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_load_test(self, loadtesting_endpoint):
        set_bodiless_matcher()
        await self.setup_create_load_test(loadtesting_endpoint)

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.get_test(self.setup_load_test_id)
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            await client.get_test(NON_EXISTING_RESOURCE)

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_list_load_tests(self, loadtesting_endpoint):
        set_bodiless_matcher()
        await self.setup_create_load_test(loadtesting_endpoint)

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.list_tests()
        assert result is not None


    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_test_file(self, loadtesting_endpoint):
        set_bodiless_matcher()
        await self.setup_create_load_test(loadtesting_endpoint)
        await self.setup_upload_test_file(loadtesting_endpoint)

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.get_test_file(self.setup_load_test_id, self.setup_file_name)
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            await client.get_test_file(self.setup_load_test_id, "nonexistent.jmx")

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_delete_test_file(self, loadtesting_endpoint):
        set_bodiless_matcher()
        await self.setup_create_load_test(loadtesting_endpoint)
        await self.setup_upload_test_file(loadtesting_endpoint)

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.delete_test_file(self.setup_load_test_id, self.setup_file_name)
        assert result is None

        with pytest.raises(ResourceNotFoundError):
            await client.delete_test_file(self.setup_load_test_id, "nonexistent.jmx")


    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def list_test_files(self, loadtesting_endpoint):
        set_bodiless_matcher()
        await self.setup_create_load_test(loadtesting_endpoint)
        await self.setup_upload_test_file(loadtesting_endpoint)

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.list_test_files(self.setup_load_test_id)
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            await client.list_test_files(NON_EXISTING_RESOURCE)

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_create_or_update_app_components(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_resource_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.create_or_update_app_components(
            loadtesting_test_id,
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
            await client.create_or_update_app_components(
                NON_EXISTING_RESOURCE,
                {
                    "components": {
                        loadtesting_resource_id: {
                            "resourceId": loadtesting_resource_id,
                            "resourceName": "App-Service-Sample-Demo",
                            "resourceType": "Microsoft.Web/sites",
                            "kind": "web",
                        }
                    }
                }
            )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_app_components(self, loadtesting_endpoint, loadtesting_resource_id):
        set_bodiless_matcher()
        await self.setup_create_load_test(loadtesting_endpoint)
        await self.setup_app_components(loadtesting_endpoint, loadtesting_resource_id)

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.get_app_components(self.setup_load_test_id)
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            await client.get_app_components(NON_EXISTING_RESOURCE)

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_file_upload_poller(self, loadtesting_endpoint):
        set_bodiless_matcher()
        await self.setup_create_load_test(loadtesting_endpoint)

        client = self.create_administration_client(loadtesting_endpoint)
        poller = await client.begin_upload_test_file(self.setup_load_test_id, "sample.jmx",
                                               open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb"))

        assert poller.get_initial_response() is not None

        result = await poller.result()
        assert poller.status() is not None
        assert result is not None
        assert poller.done() is True

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_create_or_update_server_metrics_config(self, loadtesting_endpoint, loadtesting_resource_id, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.create_or_update_server_metrics_config(
            loadtesting_test_id,
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
    @recorded_by_proxy_async
    async def test_get_server_metrics_config(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()
        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.get_server_metrics_config(loadtesting_test_id)
        assert result is not None
