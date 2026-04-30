# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Live-runnable rewrites of the generated FileShareSnapshots async tests."""
import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.fileshares.aio import FileSharesClient
from azure.mgmt.fileshares import models as fs_models

from devtools_testutils import AzureMgmtRecordedTestCase
from devtools_testutils.aio import recorded_by_proxy_async

from _helpers import (
    ARM_ENDPOINT,
    RESOURCE_GROUP,
    create_share_async,
    delete_share_async,
    random_snapshot_name,
)


class TestFileSharesFileShareSnapshotsOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            FileSharesClient,
            is_async=True,
            base_url=ARM_ENDPOINT,
            credential_scopes=["https://management.azure.com/.default"],
        )

    async def _create_snapshot(self, share_name: str, snap_name: str):
        poller = await self.client.file_share_snapshots.begin_create_or_update_file_share_snapshot(
            resource_group_name=RESOURCE_GROUP,
            resource_name=share_name,
            name=snap_name,
            resource=fs_models.FileShareSnapshot(
                properties=fs_models.FileShareSnapshotProperties(
                    metadata={"purpose": "testing", "environment": "test"},
                ),
            ),
        )
        return await poller.result()

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_file_share_snapshots_get_file_share_snapshot(self, variables):
        share_name, _ = await create_share_async(self.client, variables)
        snap_name = random_snapshot_name(variables)
        try:
            await self._create_snapshot(share_name, snap_name)
            got = await self.client.file_share_snapshots.get_file_share_snapshot(
                resource_group_name=RESOURCE_GROUP,
                resource_name=share_name,
                name=snap_name,
            )
            assert got is not None
        finally:
            await delete_share_async(self.client, share_name)
        return variables

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_file_share_snapshots_begin_create_or_update_file_share_snapshot(self, variables):
        share_name, _ = await create_share_async(self.client, variables)
        snap_name = random_snapshot_name(variables)
        try:
            created = await self._create_snapshot(share_name, snap_name)
            assert created.properties.metadata.get("purpose") == "testing"
        finally:
            await delete_share_async(self.client, share_name)
        return variables

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_file_share_snapshots_begin_update_file_share_snapshot(self, variables):
        share_name, _ = await create_share_async(self.client, variables)
        snap_name = random_snapshot_name(variables)
        try:
            await self._create_snapshot(share_name, snap_name)
            poller = await self.client.file_share_snapshots.begin_update_file_share_snapshot(
                resource_group_name=RESOURCE_GROUP,
                resource_name=share_name,
                name=snap_name,
                properties=fs_models.FileShareSnapshotUpdate(
                    properties=fs_models.FileShareSnapshotUpdateProperties(
                        metadata={"purpose": "testing", "stage": "updated"},
                    ),
                ),
            )
            updated = await poller.result()
            assert updated.properties.metadata.get("stage") == "updated"
        finally:
            await delete_share_async(self.client, share_name)
        return variables

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_file_share_snapshots_begin_delete_file_share_snapshot(self, variables):
        share_name, _ = await create_share_async(self.client, variables)
        snap_name = random_snapshot_name(variables)
        try:
            await self._create_snapshot(share_name, snap_name)
            poller = await self.client.file_share_snapshots.begin_delete_file_share_snapshot(
                resource_group_name=RESOURCE_GROUP,
                resource_name=share_name,
                name=snap_name,
            )
            await poller.result()
            with pytest.raises(ResourceNotFoundError):
                await self.client.file_share_snapshots.get_file_share_snapshot(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=share_name,
                    name=snap_name,
                )
        finally:
            await delete_share_async(self.client, share_name)
        return variables

    @pytest.mark.asyncio
    @recorded_by_proxy_async
    async def test_file_share_snapshots_list_by_file_share(self, variables):
        share_name, _ = await create_share_async(self.client, variables)
        snap_name = random_snapshot_name(variables)
        try:
            await self._create_snapshot(share_name, snap_name)
            result = [
                r
                async for r in self.client.file_share_snapshots.list_by_file_share(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=share_name,
                )
            ]
            assert len(result) >= 1
        finally:
            await delete_share_async(self.client, share_name)
        return variables
