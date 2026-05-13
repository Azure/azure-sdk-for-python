# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Sync scenario tests for connections.

No .NET ConnectionsTests.cs equivalent — the Connection resource only exists
in api-version 2025-08-01+ and isn't covered by the .NET scenario suite. This
test exercises the full CRUD surface (createOrUpdate/get/list/delete) using
a placeholder privateLinkServiceId that the RP accepts at metadata level.
"""
import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.storagemover import StorageMoverMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

AZURE_LOCATION = "eastus"

FAKE_PRIVATE_LINK_SERVICE_ID = (
    "/subscriptions/00000000-0000-0000-0000-000000000000"
    "/resourceGroups/fakeRg/providers/Microsoft.Network/privateLinkServices/fakePls"
)


class TestStorageMoverMgmtConnectionsOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(StorageMoverMgmtClient)

    @pytest.mark.skip(reason="Connection create requires a real PrivateLinkService resource (the RP validates existence). The E2E suite at Storage-XDataMove-RP/test/E2ETest/C2CTest/ConnectionTests.cs provisions one per class run via Microsoft.Network; a fake PLS resource ID returns 500. Unskip and supply a real PLS resource ID via the body to run live.")
    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_create_get_list_delete(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-conn"
        connection_name = "testconn1"

        self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"location": AZURE_LOCATION},
        )

        # Create
        created = self.client.connections.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, connection_name=connection_name,
            connection={"properties": {
                "privateLinkServiceId": FAKE_PRIVATE_LINK_SERVICE_ID,
                "description": "Test connection",
            }},
        )
        assert created.name == connection_name
        assert created.properties.private_link_service_id == FAKE_PRIVATE_LINK_SERVICE_ID
        assert created.properties.description == "Test connection"

        # Get
        fetched = self.client.connections.get(
            resource_group_name=rg, storage_mover_name=sm_name, connection_name=connection_name,
        )
        assert fetched.name == connection_name
        assert fetched.id == created.id
        assert fetched.properties.private_link_service_id == FAKE_PRIVATE_LINK_SERVICE_ID

        # List
        items = list(self.client.connections.list(
            resource_group_name=rg, storage_mover_name=sm_name,
        ))
        assert len(items) >= 1
        assert connection_name in [c.name for c in items]

        # Delete + 404 verification
        self.client.connections.begin_delete(
            resource_group_name=rg, storage_mover_name=sm_name, connection_name=connection_name,
        ).result()
        with pytest.raises(ResourceNotFoundError):
            self.client.connections.get(
                resource_group_name=rg, storage_mover_name=sm_name, connection_name=connection_name,
            )
