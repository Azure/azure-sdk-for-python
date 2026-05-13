# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Async scenario tests for storage movers (provider operations + StorageMover CRUD).

Mirrors .NET StorageMoverCollectionTests + StorageMoverResourceTests at:
  Q:\\source\\azure-sdk-for-net\\sdk\\storagemover\\Azure.ResourceManager.StorageMover\\tests\\Scenario
"""
import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.storagemover.aio import StorageMoverMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

AZURE_LOCATION = "eastus"

FAKE_STORAGE_ACCOUNT_ID = (
    "/subscriptions/00000000-0000-0000-0000-000000000000"
    "/resourceGroups/fakeRg/providers/Microsoft.Storage/storageAccounts/fakeAccount"
)


class TestStorageMoverMgmtStorageMoversOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(StorageMoverMgmtClient, is_async=True)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_create_update_get_exists(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-create1"
        sm_name2 = "testsm-create2"

        body = {
            "location": AZURE_LOCATION,
            "tags": {"tag1": "value1"},
            "properties": {"description": "This is a new storage mover"},
        }

        sm1 = await self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, storage_mover=body
        )
        assert sm1.name == sm_name
        assert sm1.tags["tag1"] == "value1"
        assert sm1.properties.description == "This is a new storage mover"

        sm2 = await self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name2, storage_mover=body
        )
        assert sm2.name == sm_name2

        sm1 = await self.client.storage_movers.get(resource_group_name=rg, storage_mover_name=sm_name)
        assert sm1.name == sm_name
        assert sm1.tags["tag1"] == "value1"

        items = [r async for r in self.client.storage_movers.list(resource_group_name=rg)]
        assert len(items) == 2

        body["properties"]["description"] = "This is an updated storage mover"
        sm1 = await self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, storage_mover=body
        )
        assert sm1.properties.description == "This is an updated storage mover"

        with pytest.raises(ResourceNotFoundError):
            await self.client.storage_movers.get(resource_group_name=rg, storage_mover_name=sm_name + "111")

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_get_storage_mover(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-get1"

        created = await self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"location": AZURE_LOCATION, "tags": {"k": "v"}},
        )

        fetched1 = await self.client.storage_movers.get(resource_group_name=rg, storage_mover_name=sm_name)
        fetched2 = await self.client.storage_movers.get(resource_group_name=rg, storage_mover_name=sm_name)

        assert fetched1.name == fetched2.name == sm_name
        assert fetched1.location == fetched2.location
        assert fetched1.type == fetched2.type
        assert fetched1.id == fetched2.id == created.id
        assert fetched1.tags == fetched2.tags

    @pytest.mark.skip(reason="Agents cannot be created by the RP; this test requires a registered agent VM.")
    @pytest.mark.asyncio
    async def test_get_storage_mover_agent(self):
        pass

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_get_storage_mover_endpoint(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-getep"
        endpoint_name = "testblobendpoint"

        await self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"location": AZURE_LOCATION},
        )
        await self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
            endpoint={"properties": {
                "endpointType": "AzureStorageBlobContainer",
                "storageAccountResourceId": FAKE_STORAGE_ACCOUNT_ID,
                "blobContainerName": "testcontainer",
            }},
        )

        endpoint = await self.client.endpoints.get(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
        )
        assert endpoint.name == endpoint_name
        assert endpoint.properties.endpoint_type == "AzureStorageBlobContainer"

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_get_storage_mover_project(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-getproj"
        project_name = "testproj1"

        await self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"location": AZURE_LOCATION},
        )
        await self.client.projects.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            project={},
        )

        project = await self.client.projects.get(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
        )
        assert project.name == project_name

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_update_add_set_remove_tag_delete(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-updel"

        sm = await self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"location": AZURE_LOCATION},
        )
        assert sm.name == sm_name
        assert sm.location == AZURE_LOCATION

        sm = await self.client.storage_movers.update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"properties": {"description": "This is an updated storage mover"}},
        )
        assert sm.properties.description == "This is an updated storage mover"

        sm = await self.client.storage_movers.update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"tags": {"tag1": "val1"}},
        )
        assert len(sm.tags) == 1
        assert sm.tags["tag1"] == "val1"

        sm = await self.client.storage_movers.update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"tags": {"tag2": "val2", "tag3": "val3"}},
        )
        assert len(sm.tags) == 2

        sm = await self.client.storage_movers.update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"tags": {"tag3": "val3"}},
        )
        assert len(sm.tags) == 1
        assert "tag3" in sm.tags

        poller = await self.client.storage_movers.begin_delete(
            resource_group_name=rg, storage_mover_name=sm_name,
        )
        await poller.result()
        with pytest.raises(ResourceNotFoundError):
            await self.client.storage_movers.get(resource_group_name=rg, storage_mover_name=sm_name)
