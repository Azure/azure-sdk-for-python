# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json

import pytest
import os
from pathlib import Path
import uuid

from testcase import LoadtestingTest, LoadtestingPowerShellPreparer
from azure.core.exceptions import HttpResponseError
from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import recorded_by_proxy, set_bodiless_matcher, set_custom_default_matcher

non_existing_test_run_id = "0000-0000"
non_existing_file_id = "000-000"
DISPLAY_NAME = "TestingResource"


class TestOperationsSmokeTest(LoadtestingTest):

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_create_or_update_loadtest(
            self,
            loadtesting_endpoint,
            loadtesting_test_id,
            loadtesting_subscription_id
    ):
        set_bodiless_matcher()
        # positive testing
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.create_or_update_test(
            loadtesting_test_id,
            {
                "resourceId": f"/subscriptions/{loadtesting_subscription_id}/resourceGroups/yashika-rg/providers/Microsoft.LoadTestService/loadtests/loadtestsdk",
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
                    "resourceId": f"/subscriptions/{loadtesting_subscription_id}/resourceGroups/yashika-rg/providers/Microsoft.LoadTestService/loadtests/loadtestsdk",
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
    @recorded_by_proxy
    def test_delete_loadtest(self, loadtesting_endpoint, loadtesting_subscription_id):
        set_bodiless_matcher()
        # creating a mock test to delete
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.create_or_update_test(
            "to-be-deleted-test-id",
            {
                "resourceId": f"/subscriptions/{loadtesting_subscription_id}/resourceGroups/yashika-rg/providers/Microsoft.LoadTestService/loadtests/loadtestsdk",
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
                test_id=non_existing_test_run_id
            )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_loadtest(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()
        # positive testing
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.get_load_test(
            test_id=loadtesting_test_id
        )
        assert result is not None

        # negative testing
        with pytest.raises(ResourceNotFoundError):
            client.load_test_administration.get_load_test(
                test_id=non_existing_test_run_id
            )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_file_upload(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_file_id):
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Type,x-ms-client-request-id,x-ms-request-id"
        )
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.upload_test_file(
            loadtesting_test_id,
            loadtesting_file_id,
            open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb")
        )
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            client.load_test_administration.upload_test_file(
                non_existing_test_run_id,
                loadtesting_file_id,
                open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb")
            )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_get_file_by_name(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_file_id):
        set_bodiless_matcher()
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = client.load_test_administration.get_test_file(
            loadtesting_test_id,
            loadtesting_file_id
        )
        print(result)
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            client.load_test_administration.get_test_file(
                non_existing_test_run_id,
                non_existing_file_id
            )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_delete_test_file(self, loadtesting_endpoint, loadtesting_test_id):
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Type,x-ms-client-request-id,x-ms-request-id"
        )
        # pushing a sample file to delete
        client = self.create_client(endpoint=loadtesting_endpoint)
        client.load_test_administration.upload_test_file(
            loadtesting_test_id,
            "unique-image-file-id",
            open(os.path.join(Path(__file__).resolve().parent, "sample-image.jpg"), "rb")
        )

        result = client.load_test_administration.delete_test_file(
            loadtesting_test_id,
            "unique-image-file-id"
        )
        assert result is None

        with pytest.raises(ResourceNotFoundError):
            client.load_test_administration.delete_test_file(
                loadtesting_test_id,
                "unique-image-file-id"
            )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy
    def test_list_test_files(self, loadtesting_endpoint, loadtesting_test_id):
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Type,x-ms-client-request-id,x-ms-request-id"
        )
        # pushing a sample file to test list
        client = self.create_client(endpoint=loadtesting_endpoint)
        client.load_test_administration.upload_test_file(
            loadtesting_test_id,
            "unique-image-file-id",
            open(os.path.join(Path(__file__).resolve().parent, "sample-image.jpg"), "rb")
        )

        result = client.load_test_administration.list_test_files(
            loadtesting_test_id
        )
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            client.load_test_administration.list_test_files(
                non_existing_test_run_id
            )

    # @LoadtestingPowerShellPreparer()
    # def test_loadtests_list_test_files_pagination(self, loadtesting_endpoint):
    #
    #     files = os.listdir(os.path.join(Path(__file__).resolve().parent, "files"))
    #     client = self.create_client(endpoint=loadtesting_endpoint)
    #
    #     for file in files:
    #         print(client.load_test_administration.upload_test_file(
    #             test_id,
    #             str(uuid.uuid4()),
    #             open(os.path.join(Path(__file__).resolve().parent, "files", file), "rb")
    #         ))
    #
    #     result = client.load_test_administration.list_test_files(
    #         test_id
    #     )
    #
    #     print(result)
        # assert result["nextLink"] is not None

    # @LoadtestingPowerShellPreparer()
    # def test_list_load_test_search(self, loadtesting_endpoint):
    #     client = self.create_client(endpoint=loadtesting_endpoint)
    #     result = client.load_test_administration.list_load_test_search(
    #         order_by="displayName asc",
    #         max_page_size=3
    #     )
    #     print(result)
