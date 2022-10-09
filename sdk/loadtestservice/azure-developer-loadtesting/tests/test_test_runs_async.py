# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError

from testcase import LoadtestingPowerShellPreparer
from testcase_async import LoadtestingAsyncTest
from devtools_testutils.aio import recorded_by_proxy_async
from devtools_testutils import set_bodiless_matcher, set_custom_default_matcher
from pathlib import Path
import os

DISPLAY_NAME = "TestingResource"  # display name
non_existing_test_run_id = "0000-0000"


class TestRunSmokeAsyncTest(LoadtestingAsyncTest):

    async def create_run_prerequisite(
            self,
            endpoint,
            test_id,
            file_id,
            subscription_id
    ):
        client = self.create_client(endpoint=endpoint)

        await client.load_test_administration.create_or_update_test(
            test_id,
            {
                "resourceId": f"/subscriptions/{subscription_id}/resourceGroups/yashika-rg/providers/Microsoft.LoadTestService/loadtests/loadtestsdk",
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

        await client.load_test_administration.upload_test_file(
            test_id,
            file_id,
            open(os.path.join(Path(__file__).resolve().parent, "sample.jmx"), "rb")
        )

    async def create_test_run(self, endpoint, test_run_name, test_id, file_id, subscription_id):
        await self.create_run_prerequisite(endpoint=endpoint,
                                           test_id=test_id,
                                           file_id=file_id,
                                           subscription_id=subscription_id
                                           )

        client = self.create_client(endpoint=endpoint)
        await client.load_test_runs.create_or_update_test(
            test_run_name,
            {
                "testId": test_id,
                "displayName": DISPLAY_NAME
            }
        )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_create_or_update_loadtest(
            self,
            loadtesting_endpoint,
            loadtesting_test_id,
            loadtesting_file_id,
            loadtesting_test_run_id,
            loadtesting_subscription_id):
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Type,x-ms-client-request-id,x-ms-request-id"
        )
        # create prerequisites
        await self.create_run_prerequisite(
            endpoint=loadtesting_endpoint,
            test_id=loadtesting_test_id,
            file_id=loadtesting_file_id,
            subscription_id=loadtesting_subscription_id
        )

        client = self.create_client(endpoint=loadtesting_endpoint)
        result = await client.load_test_runs.create_or_update_test(
            loadtesting_test_run_id,
            {
                "testId": loadtesting_test_id,
                "displayName": DISPLAY_NAME
            }
        )
        assert result is not None

        with pytest.raises(ResourceNotFoundError):
            await client.load_test_runs.create_or_update_test(
                "another-unique-test-run-id",
                {
                    "testId": "some-non-existing-test-id",
                    "displayName": DISPLAY_NAME
                }
            )

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_delete_test_run(
            self,
            loadtesting_endpoint,
            loadtesting_test_id,
            loadtesting_file_id,
            loadtesting_test_run_id,
            loadtesting_subscription_id
    ):
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Type,x-ms-client-request-id,x-ms-request-id"
        )
        # creating test run
        await self.create_test_run(endpoint=loadtesting_endpoint,
                                   test_run_name=loadtesting_test_run_id,
                                   test_id=loadtesting_test_id,
                                   file_id=loadtesting_file_id,
                                   subscription_id=loadtesting_subscription_id
                                   )

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = await client.load_test_runs.delete_test_run(loadtesting_test_run_id)
        assert result is None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            await client.load_test_runs.delete_test_run(non_existing_test_run_id)

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_test_run(
            self,
            loadtesting_endpoint,
            loadtesting_test_id,
            loadtesting_file_id,
            loadtesting_test_run_id,
            loadtesting_subscription_id
    ):
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Type,x-ms-client-request-id,x-ms-request-id"
        )
        # creating test run
        await self.create_test_run(endpoint=loadtesting_endpoint,
                                   test_run_name=loadtesting_test_run_id,
                                   test_id=loadtesting_test_id,
                                   file_id=loadtesting_file_id,
                                   subscription_id=loadtesting_subscription_id
                                   )

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = await client.load_test_runs.get_test_run(loadtesting_test_run_id)
        assert result is not None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            await client.load_test_runs.get_test_run(non_existing_test_run_id)

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_test_run_file(
            self,
            loadtesting_endpoint,
            loadtesting_test_id,
            loadtesting_file_id,
            loadtesting_test_run_id,
            loadtesting_subscription_id
    ):
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Type,x-ms-client-request-id,x-ms-request-id"
        )

        # creating test run
        await self.create_test_run(endpoint=loadtesting_endpoint,
                                   test_run_name=loadtesting_test_run_id,
                                   test_id=loadtesting_test_id,
                                   file_id=loadtesting_file_id,
                                   subscription_id=loadtesting_subscription_id
                                   )

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = await client.load_test_runs.get_test_run_file(loadtesting_test_run_id, loadtesting_file_id)
        assert result is not None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            await client.load_test_runs.get_test_run_file(non_existing_test_run_id, loadtesting_file_id)

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_stop_test_run(
            self,
            loadtesting_endpoint,
            loadtesting_test_id,
            loadtesting_file_id,
            loadtesting_test_run_id,
            loadtesting_subscription_id
    ):
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Type,x-ms-client-request-id,x-ms-request-id"
        )

        # creating test run
        await self.create_test_run(endpoint=loadtesting_endpoint,
                                   test_run_name=loadtesting_test_run_id,
                                   test_id=loadtesting_test_id,
                                   file_id=loadtesting_file_id,
                                   subscription_id=loadtesting_subscription_id
                                   )

        # positive test
        client = self.create_client(endpoint=loadtesting_endpoint)
        result = await client.load_test_runs.stop_test_run(loadtesting_test_run_id)
        assert result is not None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            await client.load_test_runs.stop_test_run(non_existing_test_run_id)

    @LoadtestingPowerShellPreparer()
    @recorded_by_proxy_async
    async def test_get_test_run_client_metrics(
            self,
            loadtesting_endpoint,
            loadtesting_test_id,
            loadtesting_file_id,
            loadtesting_test_run_id,
            loadtesting_subscription_id
    ):
        set_custom_default_matcher(
            compare_bodies=False, excluded_headers="Authorization,Content-Type,x-ms-client-request-id,x-ms-request-id"
        )
        # creating test run
        await self.create_test_run(endpoint=loadtesting_endpoint,
                                   test_run_name=loadtesting_test_run_id,
                                   test_id=loadtesting_test_id,
                                   file_id=loadtesting_file_id,
                                   subscription_id=loadtesting_subscription_id
                                   )

        client = self.create_client(endpoint=loadtesting_endpoint)

        with pytest.raises(HttpResponseError):
            result = await client.load_test_runs.get_test_run_client_metrics_filters(
                loadtesting_test_run_id
            )
            assert result is not None

            result_metrics = await client.load_test_runs.get_test_run_client_metrics(
                loadtesting_test_run_id,
                {
                    "requestSamplers": ["GET"],
                    "startTime": result['timeRange']['startTime'],
                    "endTime": result['timeRange']['endTime']

                }
            )
            assert result_metrics is not None

        # negative test
        with pytest.raises(ResourceNotFoundError):
            await client.load_test_runs.get_test_run_client_metrics_filters(
                non_existing_test_run_id
            )

        # negative test
        with pytest.raises(HttpResponseError):
            await client.load_test_runs.get_test_run_client_metrics(
                non_existing_test_run_id,
                {
                    "requestSamplers": ["GET"],
                    "startTime": result['timeRange']['startTime'],
                    "endTime": result['timeRange']['endTime']
                }
            )
