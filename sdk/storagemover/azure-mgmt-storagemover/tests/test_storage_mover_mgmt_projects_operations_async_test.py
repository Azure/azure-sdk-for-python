# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Async scenario tests for projects.

Mirrors .NET ProjectCollectionTests + ProjectResourceTests at:
  Q:\\source\\azure-sdk-for-net\\sdk\\storagemover\\Azure.ResourceManager.StorageMover\\tests\\Scenario
"""
import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.storagemover.aio import StorageMoverMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"


class TestStorageMoverMgmtProjectsOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(StorageMoverMgmtClient, is_async=True)

    async def _create_storage_mover(self, rg, sm_name):
        return await self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"location": AZURE_LOCATION},
        )

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_create_get_exists(self, resource_group):
        rg = resource_group.name
        sm_name = "stomover-projcol"
        await self._create_storage_mover(rg, sm_name)

        project_name = "project-col1"
        project = await self.client.projects.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            project={},
        )
        assert project.name == project_name
        assert project.properties.description is None
        assert project.type.lower() == "microsoft.storagemover/storagemovers/projects"

        project = await self.client.projects.get(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
        )
        assert project.name == project_name

        items = [p async for p in self.client.projects.list(
            resource_group_name=rg, storage_mover_name=sm_name,
        )]
        assert len(items) >= 1
        names = [p.name for p in items]
        assert project_name in names

        with pytest.raises(ResourceNotFoundError):
            await self.client.projects.get(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name + "111",
            )

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_get_update_delete(self, resource_group):
        rg = resource_group.name
        sm_name = "stomover-projres"
        await self._create_storage_mover(rg, sm_name)

        project_name = "project-res1"
        created = await self.client.projects.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            project={},
        )

        fetched = await self.client.projects.get(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
        )
        assert fetched.name == created.name
        assert fetched.id == created.id

        updated = await self.client.projects.update(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            project={"properties": {"description": "This is an updated project"}},
        )
        assert updated.properties.description == "This is an updated project"

        poller = await self.client.projects.begin_delete(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
        )
        await poller.result()
        with pytest.raises(ResourceNotFoundError):
            await self.client.projects.get(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            )
