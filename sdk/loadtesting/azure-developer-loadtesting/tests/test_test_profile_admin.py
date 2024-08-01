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
)

DISPLAY_NAME = "TestingResourcePyTest"
NON_EXISTING_RESOURCE = "nonexistingresource"


class TestTestProfileAdministrationClient(LoadtestingTest):

    def setup_create_test_profile(self, endpoint, testId, targetResourceId):
        self.setup_test_profile_id = "test-profile-3"
        client = self.create_administration_client(endpoint)

        client.create_or_update_test_profile(
            self.setup_test_profile_id,
            {
                "description": "",
                "displayName": DISPLAY_NAME,
                "testId": testId,
                "targetResourceId": targetResourceId,
                "targetResourceConfigurations": {
                    "kind": "FunctionsFlexConsumption",
                    "configurations": {
                        "config1": {"instanceMemoryMB": 2048, "httpConcurrency": 16},
                        "config2": {"instanceMemoryMB": 4096, "httpConcurrency": 16},
                    },
                },
            },
        )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_create_or_update_test_profile(
        self,
        loadtesting_endpoint,
        loadtesting_test_profile_id,
        loadtesting_test_id,
        loadtesting_target_resource_id,
    ):
        set_bodiless_matcher()

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.create_or_update_test_profile(
            loadtesting_test_profile_id,
            {
                "description": "",
                "displayName": DISPLAY_NAME,
                "testId": loadtesting_test_id,
                "targetResourceId": loadtesting_target_resource_id,
                "targetResourceConfigurations": {
                    "kind": "FunctionsFlexConsumption",
                    "configurations": {
                        "config1": {"instanceMemoryMB": 2048, "httpConcurrency": 16},
                        "config2": {"instanceMemoryMB": 4096, "httpConcurrency": 16},
                    },
                },
            },
        )
        assert result is not None
        with pytest.raises(HttpResponseError):
            client.create_or_update_test_profile(
                loadtesting_test_profile_id,
                {
                    "description": DISPLAY_NAME + "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz",
                    "displayName": "",
                    "testId": loadtesting_test_id,
                    "targetResourceId": loadtesting_target_resource_id,
                    "targetResourceConfigurations": {
                        "kind": "FunctionsFlexConsumption",
                        "configurations": {
                            "config1": {
                                "instanceMemoryMB": 2048,
                                "httpConcurrency": 16,
                            },
                            "config2": {
                                "instanceMemoryMB": 4096,
                                "httpConcurrency": 16,
                            },
                        },
                    },
                },
            )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_test_profile(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_target_resource_id):
        set_bodiless_matcher()

        self.setup_create_test_profile(loadtesting_endpoint, loadtesting_test_id, loadtesting_target_resource_id)

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.get_test_profile(self.setup_test_profile_id)
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            client.get_test_profile(NON_EXISTING_RESOURCE)

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_list_test_profiles(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_target_resource_id):
        set_bodiless_matcher()
        self.setup_create_test_profile(loadtesting_endpoint, loadtesting_test_id, loadtesting_target_resource_id)

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.list_test_profiles()
        assert result is not None

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_delete_test_profile(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_target_resource_id):
        set_bodiless_matcher()
        self.setup_create_test_profile(loadtesting_endpoint, loadtesting_test_id, loadtesting_target_resource_id)

        client = self.create_administration_client(loadtesting_endpoint)
        result = client.delete_test_profile(self.setup_test_profile_id)
        assert result is None
