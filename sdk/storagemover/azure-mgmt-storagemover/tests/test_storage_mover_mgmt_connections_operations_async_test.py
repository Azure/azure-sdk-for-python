# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Async scenario test for connections — matrix row #32.

See the sync sibling (test_storage_mover_mgmt_connections_operations_test.py)
for the full rationale.
"""
import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.storagemover.aio import StorageMoverMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer
from devtools_testutils.aio import recorded_by_proxy_async

# PrivateLinkService lives in westcentralus, so storage mover must too.
AZURE_LOCATION = "westcentralus"

REAL_PRIVATE_LINK_SERVICE_ID = (
    "/subscriptions/b6b34ad8-ca89-4f85-beb7-c2ec13702dac"
    "/resourceGroups/E2E-Management-RGsyn"
    "/providers/Microsoft.Network/privateLinkServices/test-pls-wcs"
)


class TestStorageMoverMgmtConnectionsOperationsAsync(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(StorageMoverMgmtClient, is_async=True)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy_async
    async def test_create_get_list_update_delete(self, resource_group):
        rg = resource_group.name
        sm_name = "testsm-conn"
        connection_name = "testconn1"

        await self.client.storage_movers.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name,
            storage_mover={"location": AZURE_LOCATION},
        )

        # Create
        created = await self.client.connections.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, connection_name=connection_name,
            connection={"properties": {
                "privateLinkServiceId": REAL_PRIVATE_LINK_SERVICE_ID,
                "description": "ConnectionDesc",
            }},
        )
        # See sync sibling for why we compare by PLS name suffix instead of full ARM ID.
        pls_id_suffix = "/providers/Microsoft.Network/privateLinkServices/test-pls-wcs"
        assert created.name == connection_name
        assert created.properties.private_link_service_id.endswith(pls_id_suffix)
        assert created.properties.description == "ConnectionDesc"

        # Get
        fetched = await self.client.connections.get(
            resource_group_name=rg, storage_mover_name=sm_name, connection_name=connection_name,
        )
        assert fetched.name == connection_name
        assert fetched.id == created.id
        assert fetched.properties.private_link_service_id.endswith(pls_id_suffix)
        # NOTE: do not assert on `connection_status` — see sync sibling docstring.

        # List
        items = [c async for c in self.client.connections.list(
            resource_group_name=rg, storage_mover_name=sm_name,
        )]
        assert len(items) >= 1
        assert connection_name in [c.name for c in items]

        # Update — see sync sibling docstring for why we don't assert on the response.
        await self.client.connections.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, connection_name=connection_name,
            connection={"properties": {
                "privateLinkServiceId": REAL_PRIVATE_LINK_SERVICE_ID,
                "description": "ConnectionDescUpdate",
            }},
        )

        # Delete + 404 verification
        poller = await self.client.connections.begin_delete(
            resource_group_name=rg, storage_mover_name=sm_name, connection_name=connection_name,
        )
        await poller.result()
        with pytest.raises(ResourceNotFoundError):
            await self.client.connections.get(
                resource_group_name=rg, storage_mover_name=sm_name, connection_name=connection_name,
            )
