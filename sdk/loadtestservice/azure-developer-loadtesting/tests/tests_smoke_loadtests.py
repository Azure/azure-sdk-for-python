# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
import os
from pathlib import Path

from testcase import LoadtestingTest, LoadtestingPowerShellPreparer
from azure.core.exceptions import HttpResponseError
from azure.core.exceptions import ResourceNotFoundError

DISPLAY_NAME = "TestingResource"


class TestOperationsSmokeTest(LoadtestingTest):

    @LoadtestingPowerShellPreparer()
    def test_create_or_update_loadtest(self, loadtesting_endpoint):
        # positive testing
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.create_or_update_test(
            "some-unique-test-id",
            {
                "resourceId": f"/subscriptions/{self.subscription_id}/resourceGroups/yashika-rg/providers/Microsoft.LoadTestService/loadtests/loadtestsdk",
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

        # negative testing
        with pytest.raises(HttpResponseError):
            client.load_test_administration.create_or_update_test(
                "some-test-id",
                {
                    "resourceId": f"/subscriptions/{self.subscription_id}/resourceGroups/yashika-rg/providers/Microsoft.LoadTestService/loadtests/loadtestsdk",
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
    def test_delete_loadtest(self, loadtesting_endpoint):
        # creating a mock test to delete
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.create_or_update_test(
            "to-be-deleted-test-id",
            {
                "resourceId": f"/subscriptions/{self.subscription_id}/resourceGroups/yashika-rg/providers/Microsoft.LoadTestService/loadtests/loadtestsdk",
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

        # positive testing
        result = client.load_test_administration.delete_load_test(
            test_id="to-be-deleted-test-id"
        )
        assert result is None

        # negative testing
        with pytest.raises(ResourceNotFoundError):
            client.load_test_administration.delete_load_test(
                test_id="non-existing-test-id"
            )

    @LoadtestingPowerShellPreparer()
    def test_get_loadtest(self, loadtesting_endpoint):
        # positive testing
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.get_load_test(
            test_id="some-unique-test-id"
        )
        assert result is not None

        # negative testing
        with pytest.raises(ResourceNotFoundError):
            client.load_test_administration.get_load_test(
                test_id="non-existing-test-id"
            )

    @LoadtestingPowerShellPreparer()
    def test_file_upload(self, loadtesting_endpoint):
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.upload_test_file(
            "some-unique-test-id",
            "some-unique-file-id",
            open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb")
        )
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            client.load_test_administration.upload_test_file(
                "non-existing-test-id",
                "some-unique-file-id",
                open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb")
            )

    @LoadtestingPowerShellPreparer()
    def test_get_file_by_name(self, loadtesting_endpoint):
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.get_test_file(
            "some-unique-test-id",
            "some-unique-file-id"
        )
        print(result)
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            client.load_test_administration.get_test_file(
                "non-unique-test-id",
                "some-non-existing-file-id"
            )

    @LoadtestingPowerShellPreparer()
    def test_delete_test_file(self, loadtesting_endpoint):

        # pushing a sample file to delete
        client = self.create_client(endpoint=loadtesting_endpoint)
        client.load_test_administration.upload_test_file(
            "some-unique-test-id",
            "unique-image-file-id",
            open(os.path.join(Path(__file__).resolve().parent, "sample-image.jpg"), "rb")
        )

        result = client.load_test_administration.delete_test_file(
            "some-unique-test-id",
            "unique-image-file-id"
        )
        assert result is None

        with pytest.raises(ResourceNotFoundError):
            client.load_test_administration.delete_test_file(
                "some-unique-test-id",
                "unique-image-file-id"
            )

    @LoadtestingPowerShellPreparer()
    def test_list_test_files(self, loadtesting_endpoint):

        # pushing a sample file to test list
        client = self.create_client(endpoint=loadtesting_endpoint)
        client.load_test_administration.upload_test_file(
            "some-unique-test-id",
            "unique-image-file-id",
            open(os.path.join(Path(__file__).resolve().parent, "sample-image.jpg"), "rb")
        )

        result = client.load_test_administration.list_test_files(
            "some-unique-test-id"
        )
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            client.load_test_administration.list_test_files(
                "non-existing-test-id"
            )
