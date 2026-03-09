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
    async def test_create_or_update_load_test(
        self, loadtesting_endpoint, loadtesting_test_id
    ):
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
                        "condition1": {
                            "clientmetric": "response_time_ms",
                            "aggregate": "avg",
                            "condition": ">",
                            "value": 300,
                        },
                        "condition2": {
                            "clientmetric": "error",
                            "aggregate": "percentage",
                            "condition": ">",
                            "value": 50,
                        },
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
                        "resourceName": "ado-sampleapp",
                        "resourceType": "Microsoft.Insights/components",
                        "resourceGroup": "nikita-rg",
                        "subscriptionId": "7c71b563-0dc0-4bc0-bcf6-06f8f0516c7a",
                        "resourceName": "ado-sampleapp",
                        "resourceType": "Microsoft.Insights/components",
                        "resourceGroup": "nikita-rg",
                        "subscriptionId": "7c71b563-0dc0-4bc0-bcf6-06f8f0516c7a",
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
    async def test_get_server_metrics_config(
        self, loadtesting_endpoint, loadtesting_test_id
    ):
        set_bodiless_matcher()
        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.get_server_metrics_config(loadtesting_test_id)
        assert result is not None

        await self.close_admin_client()

    # Trigger CRUD Tests
    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_create_or_update_trigger(
        self, loadtesting_endpoint, loadtesting_test_id
    ):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        trigger_id = "test-new-schedule-trigger-id-async"
        result = await client.create_or_update_trigger(
            trigger_id,
            {
                "displayName": "Test Trigger",
                "description": "Test trigger for pytest",
                "kind": "ScheduleTestsTrigger",
                "testIds": [loadtesting_test_id],
                "recurrence": {
                    "frequency": "Daily",
                    "interval": 1,
                },
                "startDateTime": "2026-03-04T05:42:51.038Z",
            },
        )

        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_get_trigger(self, loadtesting_endpoint):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        trigger_id = "test-new-schedule-trigger-id-async"
        result = await client.get_trigger(trigger_id)
        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_list_triggers(self, loadtesting_endpoint):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.list_triggers()
        assert result is not None
        items = [r async for r in result]
        assert len(items) >= 0

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_delete_trigger(self, loadtesting_endpoint):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        trigger_id = "test-new-schedule-trigger-id-async"
        result = await client.delete_trigger(trigger_id)
        assert result is None

        await self.close_admin_client()

    # Notification Rule CRUD Tests
    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_create_or_update_notification_rule(
        self, loadtesting_endpoint, loadtesting_test_id, loadtesting_action_group_id
    ):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        notification_rule_id = "test-new-notification-id-async"
        result = await client.create_or_update_notification_rule(
            notification_rule_id,
            {
                "displayName": "Test Notification Rule",
                "scope": "Tests",
                "testIds": [loadtesting_test_id],
                "actionGroupIds": [
                    loadtesting_action_group_id,
                ],
                "eventFilters": {
                    "testRunEnded": {
                        "kind": "TestRunEnded",
                        "condition": {
                            "testRunStatuses": ["DONE", "FAILED"],
                            "testRunResults": ["PASSED", "FAILED"],
                        },
                    },
                },
            },
        )

        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_get_notification_rule(self, loadtesting_endpoint):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        notification_rule_id = "test-new-notification-id-async"
        result = await client.get_notification_rule(notification_rule_id)
        assert result is not None

        await self.close_admin_client()

    # Test Plan Recommendations Test
    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_list_notification_rules(self, loadtesting_endpoint):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.list_notification_rules()
        assert result is not None
        items = [r async for r in result]
        assert len(items) >= 0

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_delete_notification_rule(self, loadtesting_endpoint):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        notification_rule_id = "test-new-notification-id-async"
        result = await client.delete_notification_rule(notification_rule_id)
        assert result is None

        await self.close_admin_client()

    # Test Plan Recommendations Test
    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_begin_generate_test_plan_recommendations(
        self, loadtesting_endpoint, loadtesting_recording_test_id
    ):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = await client.begin_generate_test_plan_recommendations(
            loadtesting_recording_test_id
        )
        assert result is not None

        await self.close_admin_client()

    @LoadTestingPreparer()
    @recorded_by_proxy_async
    @pytest.mark.asyncio
    async def test_begin_clone_test(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        new_test_id = "new-cloned-test-id-async"
        
        poller = await client.begin_clone_test(
            loadtesting_test_id,
            new_test_id=new_test_id,
            display_name="Cloned Test",
            description="Cloned test for pytest",
        )
        
        result = await poller.result()
        assert result is not None
        assert poller.done() is True

        # Get the cloned test to verify it was created successfully
        cloned_test = await client.get_test(new_test_id)
        assert cloned_test is not None
        assert cloned_test.display_name == "Cloned Test"

        # Clean up cloned test
        result = await client.delete_test(new_test_id)
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
