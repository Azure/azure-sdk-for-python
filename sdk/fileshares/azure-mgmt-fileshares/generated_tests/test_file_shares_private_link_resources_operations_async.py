# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Live-runnable rewrites of the generated PrivateLinkResources async tests."""
import pytest
from azure.mgmt.fileshares.aio import FileSharesClient

from devtools_testutils import AzureMgmtRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from _helpers import (
    ARM_ENDPOINT,
    RESOURCE_GROUP,
    create_share_async,
    delete_share_async,
)


class TestFileSharesPrivateLinkResourcesOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            FileSharesClient,
            is_async=True,
            base_url=ARM_ENDPOINT,
            credential_scopes=["https://management.azure.com/.default"],
        )

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_private_link_resources_list(self, variables):
        share_name, _ = await create_share_async(self.client, variables)
        try:
            result = [
                r
                async for r in self.client.private_link_resources.list(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=share_name,
                )
            ]
            assert isinstance(result, list)
        finally:
            await delete_share_async(self.client, share_name)
        return variables

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_private_link_resources_get(self, variables):
        share_name, _ = await create_share_async(self.client, variables)
        try:
            resources = [
                r
                async for r in self.client.private_link_resources.list(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=share_name,
                )
            ]
            if not resources:
                return variables
            plr_name = variables.setdefault("plr_name", resources[0].name)
            got = await self.client.private_link_resources.get(
                resource_group_name=RESOURCE_GROUP,
                resource_name=share_name,
                private_link_resource_name=plr_name,
            )
            assert got is not None
        finally:
            await delete_share_async(self.client, share_name)
        return variables
