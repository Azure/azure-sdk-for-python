# pylint: disable=line-too-long,useless-suppression
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import AzureRecordedTestCase, EnvironmentVariableLoader
from azure.developer.loadtesting import LoadTestAdministrationClient, LoadTestRunClient


class LoadTestingTest(AzureRecordedTestCase):

    def create_administration_client(self, endpoint) -> LoadTestAdministrationClient:
        credential = self.get_credential(LoadTestAdministrationClient)
        return self.create_client_from_credential(
            LoadTestAdministrationClient,
            credential=credential,
            endpoint=endpoint,
        )

    def create_run_client(self, endpoint) -> LoadTestRunClient:
        credential = self.get_credential(LoadTestRunClient)
        return self.create_client_from_credential(
            LoadTestRunClient,
            credential=credential,
            endpoint=endpoint,
        )


LoadTestingPreparer = functools.partial(
    EnvironmentVariableLoader,
    "loadtesting",
    loadtesting_endpoint="00000000-0000-0000-0000-000000000000.eastus.cnt-prod.loadtesting.azure.com",
    loadtesting_test_id="some-test-id",
    loadtesting_test_run_id="some-test-run-id",
    loadtesting_app_component_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myRG/providers/Microsoft.Web/sites/contoso-sampleapp",
    loadtesting_test_profile_id="some-test-profile-id",
    loadtesting_target_resource_id="/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/myRG/providers/Microsoft.Web/sites/myFlexFunction",
    loadtesting_test_profile_run_id="some-test-profile-run-id"
)
