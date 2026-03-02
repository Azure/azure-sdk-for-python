# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from pathlib import Path

import pytest

from testcase import LoadTestingPreparer, LoadTestingTest
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher

DISPLAY_NAME = "TestingResourcePyTest"


class TestLoadTestAdministrationOperations(LoadTestingTest):

    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_create_or_update_load_test(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.create_or_update_test(
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

    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_get_load_test(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.get_test(loadtesting_test_id)
        assert result is not None

    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_list_load_tests(self, loadtesting_endpoint):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.list_tests()
        assert result is not None
        items = [r for r in result]
        assert len(items) > 0  # page has atleast one item

    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_upload_test_file(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        poller = client.begin_upload_test_file(
            loadtesting_test_id,
            "sample.jmx",
            open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb"),
        )

        result = poller.result(1000)
        assert poller.status() is not None
        assert result is not None
        assert poller.done() is True

    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_get_test_file(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.get_test_file(loadtesting_test_id, "sample.jmx")
        assert result is not None

    @LoadTestingPreparer()
    @recorded_by_proxy
    def list_test_files(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.list_test_files(loadtesting_test_id)
        assert result is not None
        items = [r for r in result]
        assert len(items) > 0  # page has atleast one item

    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_create_or_update_app_components(
        self, loadtesting_endpoint, loadtesting_test_id, loadtesting_app_component_id
    ):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.create_or_update_app_components(
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

    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_get_app_components(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.get_app_components(loadtesting_test_id)
        assert result is not None
        assert len(result) > 0

    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_create_or_update_server_metrics_config(
        self, loadtesting_endpoint, loadtesting_app_component_id, loadtesting_test_id
    ):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.create_or_update_server_metrics_config(
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

    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_get_server_metrics_config(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()
        client = self.create_administration_client(loadtesting_endpoint)
        result = client.get_server_metrics_config(loadtesting_test_id)
        assert result is not None

    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_delete_test_file(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.delete_test_file(loadtesting_test_id, "sample.jmx")
        assert result is None

# Trigger CRUD Tests
    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_create_or_update_trigger(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        trigger_id = "test-schedule-trigger-id-sync"
        result = client.create_or_update_trigger(
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

    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_get_trigger(self, loadtesting_endpoint):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        trigger_id = "test-schedule-trigger-id-sync"
        result = client.get_trigger(trigger_id)
        assert result is not None

    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_list_triggers(self, loadtesting_endpoint):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.list_triggers()
        assert result is not None
        items = [r for r in result]
        assert len(items) >= 0

    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_delete_trigger(self, loadtesting_endpoint):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        trigger_id = "test-schedule-trigger-id-sync"
        result = client.delete_trigger(trigger_id)
        assert result is None

    # Notification Rule CRUD Tests
    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_create_or_update_notification_rule(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_action_group_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        notification_rule_id = "test-notification-id-sync"
        result = client.create_or_update_notification_rule(
            notification_rule_id,
            {
                "displayName": "Test Notification Rule",
                "scope": "Tests",
                "testIds": [loadtesting_test_id],
                "actionGroupIds": [loadtesting_action_group_id],
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

    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_get_notification_rule(self, loadtesting_endpoint):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        notification_rule_id = "test-notification-id-sync"
        result = client.get_notification_rule(notification_rule_id)
        assert result is not None

    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_list_notification_rules(self, loadtesting_endpoint):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.list_notification_rules()
        assert result is not None
        items = [r for r in result]
        assert len(items) >= 0

    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_delete_notification_rule(self, loadtesting_endpoint):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        notification_rule_id = "test-notification-id-sync"
        result = client.delete_notification_rule(notification_rule_id)
        assert result is None

    # Test Plan Recommendations Test
    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_begin_generate_test_plan_recommendations(self, loadtesting_endpoint, loadtesting_recording_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.begin_generate_test_plan_recommendations(loadtesting_recording_test_id)
        assert result is not None
        
    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_begin_clone_test(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        new_test_id = "new-clone-test-id-sync"
        
        poller = client.begin_clone_test(
            loadtesting_test_id,
            new_test_id=new_test_id,
            display_name="Cloned Test",
            description="Cloned test for pytest",
        )
        
        result = poller.result()
        assert result is not None
        assert poller.done() is True

        # Get the cloned test to verify it was created successfully
        cloned_test = client.get_test(new_test_id)
        assert cloned_test is not None
        assert cloned_test.display_name == "Cloned Test"

        # Clean up cloned test
        result = client.delete_test(new_test_id)
        assert result is None

    @LoadTestingPreparer()
    @recorded_by_proxy
    def test_delete_load_test(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.delete_test(loadtesting_test_id)
        assert result is None