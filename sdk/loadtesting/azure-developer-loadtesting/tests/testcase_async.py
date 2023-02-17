# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.developer.loadtesting.aio import LoadTestRunClient, LoadAdministrationClient
from devtools_testutils import AzureRecordedTestCase


class LoadtestingAsyncTest(AzureRecordedTestCase):
    def create_administration_client(self, endpoint):
        credential = self.get_credential(LoadAdministrationClient, is_async=True)
        return self.create_client_from_credential(
            LoadAdministrationClient,
            credential=credential,
            endpoint=endpoint,
        )

    def create_run_client(self, endpoint):
        credential = self.get_credential(LoadTestRunClient, is_async=True)
        return self.create_client_from_credential(
            LoadTestRunClient,
            credential=credential,
            endpoint=endpoint,
        )