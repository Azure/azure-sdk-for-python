# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import functools
from devtools_testutils import AzureRecordedTestCase, PowerShellPreparer
from azure.developer.loadtesting import LoadTestingClient

class LoadtestingTest(AzureRecordedTestCase):

    def create_client(self, endpoint):
        credential = self.get_credential(LoadTestingClient)
        return self.create_client_from_credential(
            LoadTestingClient,
            credential=credential,
            endpoint=endpoint,
        )


LoadtestingPowerShellPreparer = functools.partial(
    PowerShellPreparer,
    "loadtesting",
    loadtesting_endpoint="https://myservice.azure.com",
    loadtesting_test_id="000",
    loadtesting_file_id="000",
    loadtesting_test_run_id="000",
    loadtesting_app_component="000",
    loadtesting_subscription_id="000",
    loadtesting_resource_id="000",
)
