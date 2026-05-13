# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Sync scenario tests for storage movers (provider operations + StorageMover CRUD).

Mirrors .NET StorageMoverCollectionTests + StorageMoverResourceTests at:
  Q:\\source\\azure-sdk-for-net\\sdk\\storagemover\\Azure.ResourceManager.StorageMover\\tests\\Scenario
"""
import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.storagemover import StorageMoverMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"

FAKE_STORAGE_ACCOUNT_ID = (
    "/subscriptions/00000000-0000-0000-0000-000000000000"
    "/resourceGroups/fakeRg/providers/Microsoft.Storage/storageAccounts/fakeAccount"
)


class TestStorageMoverMgmtStorageMoversOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(StorageMoverMgmtClient)

    # ----- StorageMoverCollectionTests.CreateUpdateGetExistsTest -----

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_create_update_get_exists(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-create1"
        sm_name2 = "testsm-create2"

        body = {
            "location": AZURE_LOCATION,
            "tags": {"tag1": "value1"},
            "properties": {"description": "This is a new storage mover"},
        }

        sm1 = self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, storage_mover=body
        )
        assert sm1.name == sm_name
        assert sm1.tags["tag1"] == "value1"
        assert sm1.properties.description == "This is a new storage mover"

        sm2 = self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name2, storage_mover=body
        )
        assert sm2.name == sm_name2

        sm1 = self.client.storage_movers.get(resource_group_name=rg, storage_mover_name=sm_name)
        assert sm1.name == sm_name
        assert sm1.tags["tag1"] == "value1"
        assert sm1.properties.description == "This is a new storage mover"

        items = list(self.client.storage_movers.list(resource_group_name=rg))
        assert len(items) == 2

        body["properties"]["description"] = "This is an updated storage mover"
        sm1 = self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, storage_mover=body
        )
        assert sm1.properties.description == "This is an updated storage mover"

        # Existence check via get (Python SDK has no Exists helper)
        assert self.client.storage_movers.get(resource_group_name=rg, storage_mover_name=sm_name).name == sm_name
        with pytest.raises(ResourceNotFoundError):
            self.client.storage_movers.get(resource_group_name=rg, storage_mover_name=sm_name + "111")

    # ----- StorageMoverResourceTests.GetStorageMoverTest -----

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_get_storage_mover(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-get1"

        created = self.client.storage_movers.create_or_update(
            resource_group_name=rg,
            storage_mover_name=sm_name,
            storage_mover={"location": AZURE_LOCATION, "tags": {"k": "v"}},
        )

        fetched1 = self.client.storage_movers.get(resource_group_name=rg, storage_mover_name=sm_name)
        fetched2 = self.client.storage_movers.get(resource_group_name=rg, storage_mover_name=sm_name)

        assert fetched1.name == fetched2.name == sm_name
        assert fetched1.location == fetched2.location
        assert fetched1.type == fetched2.type
        assert fetched1.id == fetched2.id == created.id
        assert fetched1.tags == fetched2.tags

    # ----- StorageMoverResourceTests.GetStorageMoverAgentTest -----
    # SKIP: agents cannot be created via RP — they are registered by an actual agent VM.

    @pytest.mark.skip(reason="Agents cannot be created by the RP; this test requires a registered agent VM.")
    def test_get_storage_mover_agent(self):
        pass

    # ----- StorageMoverResourceTests.GetStorageMoverEndpointTest -----

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_get_storage_mover_endpoint(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-getep"
        endpoint_name = "testblobendpoint"

        self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"location": AZURE_LOCATION},
        )
        self.client.endpoints.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
            endpoint={"properties": {
                "endpointType": "AzureStorageBlobContainer",
                "storageAccountResourceId": FAKE_STORAGE_ACCOUNT_ID,
                "blobContainerName": "testcontainer",
            }},
        )

        endpoint = self.client.endpoints.get(
            resource_group_name=rg, storage_mover_name=sm_name, endpoint_name=endpoint_name,
        )
        assert endpoint.name == endpoint_name
        assert endpoint.properties.endpoint_type == "AzureStorageBlobContainer"

    # ----- StorageMoverResourceTests.GetStorageMoverProjectTest -----

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_get_storage_mover_project(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-getproj"
        project_name = "testproj1"

        self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"location": AZURE_LOCATION},
        )
        self.client.projects.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            project={},
        )

        project = self.client.projects.get(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
        )
        assert project.name == project_name

    # ----- StorageMoverResourceTests.UpdateAddSetRemoveTagDeletTest -----

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_update_add_set_remove_tag_delete(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-updel"

        sm = self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"location": AZURE_LOCATION},
        )
        assert sm.name == sm_name
        assert sm.location == AZURE_LOCATION

        # Update description via PATCH
        sm = self.client.storage_movers.update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"properties": {"description": "This is an updated storage mover"}},
        )
        assert sm.properties.description == "This is an updated storage mover"

        # Add a single tag (mirrors AddTagAsync) — Python SDK has no AddTag helper, so use update.
        # Subscription policies may inject extra tags, so only assert on the tag we set.
        sm = self.client.storage_movers.update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"tags": {"tag1": "val1"}},
        )
        assert sm.tags.get("tag1") == "val1"

        # Set tags (mirrors SetTagsAsync — PATCH with a new tag map).
        sm = self.client.storage_movers.update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"tags": {"tag2": "val2", "tag3": "val3"}},
        )
        assert sm.tags.get("tag2") == "val2"
        assert sm.tags.get("tag3") == "val3"

        # Remove a tag (mirrors RemoveTagAsync) — verify tag3 is still present.
        sm = self.client.storage_movers.update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"tags": {"tag3": "val3"}},
        )
        assert sm.tags.get("tag3") == "val3"

        # Delete and confirm 404
        self.client.storage_movers.begin_delete(
            resource_group_name=rg, storage_mover_name=sm_name,
        ).result()
        with pytest.raises(ResourceNotFoundError):
            self.client.storage_movers.get(resource_group_name=rg, storage_mover_name=sm_name)
