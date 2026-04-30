# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Live-runnable rewrites of the generated InformationalOperations async tests."""
import pytest
from azure.mgmt.fileshares.aio import FileSharesClient

from devtools_testutils import AzureMgmtRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from _helpers import ARM_ENDPOINT, AZURE_LOCATION


class TestFileSharesInformationalOperationsOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            FileSharesClient,
            is_async=True,
            base_url=ARM_ENDPOINT,
            credential_scopes=["https://management.azure.com/.default"],
        )

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_informational_operations_get_usage_data(self):
        response = await self.client.informational_operations.get_usage_data(
            location=AZURE_LOCATION,
        )
        assert response is not None

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_informational_operations_get_limits(self):
        response = await self.client.informational_operations.get_limits(
            location=AZURE_LOCATION,
        )
        assert response is not None

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_informational_operations_get_provisioning_recommendation(self):
        response = await self.client.informational_operations.get_provisioning_recommendation(
            location=AZURE_LOCATION,
            body={"properties": {"provisionedStorageGiB": 1024}},
        )
        assert response is not None
