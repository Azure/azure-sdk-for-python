# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest

from testcase import LoadtestingPowerShellPreparer
from testcase_async import LoadtestingAsyncTest
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_bodiless_matcher, set_custom_default_matcher
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
import os
from pathlib import Path

non_existing_test_run_id = "0000-0000"
non_existing_file_id = "000-000"
DISPLAY_NAME = "TestingResource"

class TestOperationsAsyncSmokeTest(LoadtestingAsyncTest):

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_create_or_update_loadtest(
            self,
            loadtesting_endpoint,
            loadtesting_test_id,
            loadtesting_subscription_id
    ):
        set_bodiless_matcher()

        client = self.create_client(endpoint=loadtesting_endpoint)
        result = await client.load_test_administration.create_or_update_test(
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
            }
        )
        assert result is not None

        # negative testing
        with pytest.raises(HttpResponseError):
            await client.load_test_administration.create_or_update_test(
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
    @recorded_by_proxy_async
    async def test_delete_loadtest(self, loadtesting_endpoint, loadtesting_subscription_id):

        set_bodiless_matcher()
        # creating a mock test to delete
        client = self.create_client(endpoint=loadtesting_endpoint)
        await client.load_test_administration.create_or_update_test(
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
        result = await client.load_test_administration.delete_load_test(
            test_id="to-be-deleted-test-id"
        )
        assert result is None

        # negative testing
        with pytest.raises(ResourceNotFoundError):
            await client.load_test_administration.delete_load_test(
                test_id=non_existing_test_run_id
            )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_loadtest(self, loadtesting_endpoint, loadtesting_test_id):
        set_bodiless_matcher()
        # positive testing
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = await client.load_test_administration.get_load_test(
            test_id=loadtesting_test_id
        )
        assert result is not None

        # negative testing
        with pytest.raises(ResourceNotFoundError):
            await client.load_test_administration.get_load_test(
                test_id=non_existing_test_run_id
            )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_file_upload(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_file_id):
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Type,x-ms-client-request-id,x-ms-request-id"
        )
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = await client.load_test_administration.upload_test_file(
            loadtesting_test_id,
            loadtesting_file_id,
            open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb")
        )
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            await client.load_test_administration.upload_test_file(
                non_existing_test_run_id,
                loadtesting_file_id,
                open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb")
            )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_file_by_name(self, loadtesting_endpoint, loadtesting_test_id, loadtesting_file_id):
        set_bodiless_matcher()
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = await client.load_test_administration.get_test_file(
            loadtesting_test_id,
            loadtesting_file_id
        )
        print(result)
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            await client.load_test_administration.get_test_file(
                non_existing_test_run_id,
                non_existing_file_id
            )
