# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Sync scenario tests for projects.

Mirrors .NET ProjectCollectionTests + ProjectResourceTests at:
  Q:\\source\\azure-sdk-for-net\\sdk\\storagemover\\Azure.ResourceManager.StorageMover\\tests\\Scenario
"""
import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.storagemover import StorageMoverMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"


class TestStorageMoverMgmtProjectsOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(StorageMoverMgmtClient)

    def _create_storage_mover(self, rg, sm_name):
        return self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"location": AZURE_LOCATION},
        )

    # ----- ProjectCollectionTests.CrateGetExistTest -----

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_create_get_exists(self, resource_group):
        rg = resource_group.name
        sm_name = "stomover-projcol"
        self._create_storage_mover(rg, sm_name)

        project_name = "project-col1"
        project = self.client.projects.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            project={},
        )
        assert project.name == project_name
        assert project.properties.description is None
        assert project.type.lower() == "microsoft.storagemover/storagemovers/projects"

        project = self.client.projects.get(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
        )
        assert project.name == project_name
        assert project.properties.description is None

        items = list(self.client.projects.list(
            resource_group_name=rg, storage_mover_name=sm_name,
        ))
        assert len(items) >= 1
        names = [p.name for p in items]
        assert project_name in names

        # Existence via get
        assert self.client.projects.get(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
        ).name == project_name
        with pytest.raises(ResourceNotFoundError):
            self.client.projects.get(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name + "111",
            )

    # ----- ProjectResourceTests.GetUpdateDeleteTest -----

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_get_update_delete(self, resource_group):
        rg = resource_group.name
        sm_name = "stomover-projres"
        self._create_storage_mover(rg, sm_name)

        project_name = "project-res1"
        created = self.client.projects.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            project={},
        )

        fetched = self.client.projects.get(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
        )
        assert fetched.name == created.name
        assert fetched.properties.description == created.properties.description
        assert fetched.id == created.id

        updated = self.client.projects.update(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            project={"properties": {"description": "This is an updated project"}},
        )
        assert updated.properties.description == "This is an updated project"

        self.client.projects.begin_delete(
            resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
        ).result()
        with pytest.raises(ResourceNotFoundError):
            self.client.projects.get(
                resource_group_name=rg, storage_mover_name=sm_name, project_name=project_name,
            )
