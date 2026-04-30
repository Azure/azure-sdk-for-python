# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Live-runnable rewrites of the generated FileSharesOperations async tests.

See ``test_file_shares_file_shares_operations.py`` for the variables/sanitizer
rationale.
"""
import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.fileshares.aio import FileSharesClient
from azure.mgmt.fileshares import models as fs_models

from devtools_testutils import AzureMgmtRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from _helpers import (
    ARM_ENDPOINT,
    AZURE_LOCATION,
    RESOURCE_GROUP,
    build_share_payload,
    create_share_async,
    delete_share_async,
    random_share_name,
)


class TestFileSharesFileSharesOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            FileSharesClient,
            is_async=True,
            base_url=ARM_ENDPOINT,
            credential_scopes=["https://management.azure.com/.default"],
        )

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_file_shares_get(self, variables):
        name, _ = await create_share_async(self.client, variables)
        try:
            got = await self.client.file_shares.get(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
            )
            assert got is not None
            assert got.properties.provisioning_state == "Succeeded"
        finally:
            await delete_share_async(self.client, name)
        return variables

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_file_shares_begin_create_or_update(self, variables):
        name = random_share_name(variables)
        try:
            poller = await self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(),
            )
            created = await poller.result()
            assert created.location.lower() == AZURE_LOCATION.lower()
        finally:
            await delete_share_async(self.client, name)
        return variables

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_file_shares_begin_update(self, variables):
        name, _ = await create_share_async(self.client, variables)
        try:
            poller = await self.client.file_shares.begin_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                properties=fs_models.FileShareUpdate(
                    tags={"lifecycle": "crud", "test": "nfs", "updated": "true", "version": "2"},
                ),
            )
            updated = await poller.result()
            assert updated.tags.get("updated") == "true"
        finally:
            await delete_share_async(self.client, name)
        return variables

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_file_shares_begin_delete(self, variables):
        name, _ = await create_share_async(self.client, variables)
        poller = await self.client.file_shares.begin_delete(
            resource_group_name=RESOURCE_GROUP,
            resource_name=name,
        )
        await poller.result()
        with pytest.raises(ResourceNotFoundError):
            await self.client.file_shares.get(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
            )
        return variables

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_file_shares_list_by_subscription(self, variables):
        result = [r async for r in self.client.file_shares.list_by_subscription()]
        assert isinstance(result, list)
        return variables

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_file_shares_list_by_parent(self, variables):
        name, _ = await create_share_async(self.client, variables)
        try:
            result = [
                r
                async for r in self.client.file_shares.list_by_parent(
                    resource_group_name=RESOURCE_GROUP
                )
            ]
            assert len(result) >= 1
        finally:
            await delete_share_async(self.client, name)
        return variables

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_file_shares_check_name_availability(self, variables):
        name = random_share_name(variables)
        response = await self.client.file_shares.check_name_availability(
            location=AZURE_LOCATION,
            body={"name": name, "type": "Microsoft.FileShares/fileShares"},
        )
        assert response.name_available is True
        return variables
