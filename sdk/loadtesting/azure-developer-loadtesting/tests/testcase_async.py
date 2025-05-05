# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.developer.loadtesting.aio import LoadTestRunClient, LoadTestAdministrationClient
from devtools_testutils import AzureRecordedTestCase


class LoadTestingAsyncTest(AzureRecordedTestCase):
    def create_administration_client(self, endpoint) -> LoadTestAdministrationClient:
        self.admin_credential = self.get_credential(LoadTestAdministrationClient, is_async=True)
        self.admin_client = self.create_client_from_credential(
            LoadTestAdministrationClient,
            credential=self.admin_credential,
            endpoint=endpoint,
        )
        
        return self.admin_client

    def create_run_client(self, endpoint) -> LoadTestRunClient:
        self.run_credential = self.get_credential(LoadTestRunClient, is_async=True)
        self.run_client = self.create_client_from_credential(
            LoadTestRunClient,
            credential=self.run_credential,
            endpoint=endpoint,
        )

        return self.run_client
    
    async def close_admin_client(self):
        await self.admin_credential.close()
        await self.admin_client.close()
    
    async def close_run_client(self):
        await self.run_credential.close()
        await self.run_client.close()
