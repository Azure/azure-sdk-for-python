import os
from pathlib import Path

import pytest
import time
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from testcase import LoadtestingPowerShellPreparer, LoadtestingTest
from devtools_testutils import (
    recorded_by_proxy,
    set_bodiless_matcher,
    set_custom_default_matcher,
    EnvironmentVariableLoader,
)
from devtools_testutils import AzureRecordedTestCase

NON_EXISTING_RESOURCE = "nonexistingresource"
DISPLAY_NAME = "TestingResourcePyTest"


class TestTestProfileRunClient(LoadtestingTest):

    def setup_test_profile(self, endpoint, target_resource_id, test_id):
        client = self.create_administration_client(endpoint)

        client.create_or_update_test(
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
            },
        )

        validation_poller = client.begin_upload_test_file(
            test_id,
            "sample.jmx",
            open(os.path.join(os.path.dirname(__file__), "sample.jmx"), "rb"),
        )

        self.setup_test_profile_id = "test-profile-15-07-2024-14-23"
        client.create_or_update_test_profile(
            self.setup_test_profile_id,
            {
                "description": "",
                "displayName": DISPLAY_NAME,
                "testId": test_id,
                "targetResourceId": target_resource_id,
                "targetResourceConfigurations": {
                    "kind": "FunctionsFlexConsumption",
                    "configurations": {
                        "config1": {"instanceMemoryMB": 2048, "httpConcurrency": 16},
                        "config2": {"instanceMemoryMB": 4096, "httpConcurrency": 16},
                    },
                },
            },
        )

        validation_poller.result(6000)

    def setup_test_profile_run(
        self,
        endpoint,
        test_profile_run_id,
        target_resource_id,
        test_id,
    ):
        self.setup_test_profile(endpoint, target_resource_id, test_id)

        run_client = self.create_run_client(endpoint)

        run_poller = run_client.begin_test_profile_run(
            test_profile_run_id,
            {
                "testProfileId": self.setup_test_profile_id,
                "displayName": "My new profile run test from pytest",
            },
        )
        run_poller.result(10800)

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_test_profile_run_poller(
        self,
        loadtesting_endpoint,
        loadtesting_test_profile_run_id,
        loadtesting_target_resource_id,
        loadtesting_test_id,
    ):
        set_bodiless_matcher()

        self.setup_test_profile(
            loadtesting_endpoint, loadtesting_target_resource_id, loadtesting_test_id
        )

        run_client = self.create_run_client(loadtesting_endpoint)

        run_poller = run_client.begin_test_profile_run(
            loadtesting_test_profile_run_id,
            {
                "testProfileId": self.setup_test_profile_id,
                "display name": "My new test profile run from Pytest",
            },
        )

        result = run_poller.result(10800)
        assert result is not None

        assert run_poller.status() is not None
        assert run_poller.done() is True

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_test_profile_run(
        self, loadtesting_endpoint, loadtesting_test_profile_run_id
    ):
        set_bodiless_matcher()

        run_client = self.create_run_client(loadtesting_endpoint)

        result = run_client.get_test_profile_run(loadtesting_test_profile_run_id)
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            run_client.get_test_profile_run(NON_EXISTING_RESOURCE)

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_list_test_profile_runs(
        self,
        loadtesting_endpoint,
        loadtesting_test_profile_run_id,
        loadtesting_target_resource_id,
        loadtesting_test_id,
    ):
        set_bodiless_matcher()

        self.setup_test_profile_run(
            loadtesting_endpoint,
            loadtesting_test_profile_run_id,
            loadtesting_target_resource_id,
            loadtesting_test_id,
        )

        run_client = self.create_run_client(loadtesting_endpoint)

        result = run_client.list_test_profile_runs()
        assert result is not None

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_delete_test_profile_run(
        self,
        loadtesting_endpoint,
        loadtesting_test_profile_run_id,
        loadtesting_target_resource_id,
        loadtesting_test_id,
    ):
        set_bodiless_matcher()

        self.setup_test_profile_run(
            loadtesting_endpoint,
            loadtesting_test_profile_run_id,
            loadtesting_target_resource_id,
            loadtesting_test_id,
        )

        run_client = self.create_run_client(loadtesting_endpoint)

        result = run_client.delete_test_profile_run(loadtesting_test_profile_run_id)
        assert result is None

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_stop_test_profile_run(
        self, loadtesting_endpoint, loadtesting_target_resource_id, loadtesting_test_id
    ):
        set_bodiless_matcher()

        self.setup_test_profile(
            loadtesting_endpoint,
            loadtesting_target_resource_id,
            loadtesting_test_id,
        )
        run_client = self.create_run_client(loadtesting_endpoint)

        run_poller = run_client.begin_test_profile_run(
            "test-profile-run-id-15-07-2024-14-23",
            {
                "testId": loadtesting_test_id,
                "testProfileId": self.setup_test_profile_id,
                "displayName": "My New Test Profile Run from PyTest",
            },
        )

        result = run_client.stop_test_profile_run(
            "test-profile-run-id-15-07-2024-14-23"
        )
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            run_client.stop_test_profile_run(NON_EXISTING_RESOURCE)
