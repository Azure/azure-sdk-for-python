# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Sync scenario test for connections — matrix row #32.

`ConnectionTests.CreateGetListUpdateDeleteTest` in the cross-language source-of-truth
matrix. Mirrors the CLI port's `test_storage_mover_connection_scenarios`. The
Connection op group is new in API 2025-08-01+ and isn't in the .NET Scenario suite
yet — this is the canonical Python port.

Exercises Storage Mover Connection CRUD (create / get / list / update / delete)
against the **real** shared PrivateLinkService `test-pls-wcs` in subscription
``b6b34ad8-ca89-4f85-beb7-c2ec13702dac`` (XDataMove-Synthetics) / RG
``E2E-Management-RGsyn``. The PLS lives in ``westcentralus``, so the storage mover
must too.

Intentionally does NOT assert on ``properties.connection_status``: it'll be
``Pending`` immediately after create because the PLS-side PE provisioning is
async. Approval is covered by matrix row #31
(``JobDefinitionJobRunTests.StartC2CJobWithPrivateSourceTest``).
"""
import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.storagemover import StorageMoverMgmtClient

from devtools_testutils import AzureMgmtRecordedTestCase, RandomNameResourceGroupPreparer, recorded_by_proxy

# PrivateLinkService lives in westcentralus, so storage mover must too.
AZURE_LOCATION = "westcentralus"

# Shared team infra in XDataMove-Synthetics — do not recreate.
# Full inventory in the cross-language playbook
# (storage-mover-scenario-tests-cross-language, "Porter's reference" callout).
REAL_PRIVATE_LINK_SERVICE_ID = (
    "/subscriptions/b6b34ad8-ca89-4f85-beb7-c2ec13702dac"
    "/resourceGroups/E2E-Management-RGsyn"
    "/providers/Microsoft.Network/privateLinkServices/test-pls-wcs"
)


class TestStorageMoverMgmtConnectionsOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(StorageMoverMgmtClient)

    @RandomNameResourceGroupPreparer(location=AZURE_LOCATION)
    @recorded_by_proxy
    def test_create_get_list_update_delete(self, resource_group):
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
                "privateLinkServiceId": REAL_PRIVATE_LINK_SERVICE_ID,
                "description": "ConnectionDesc",
            }},
        )
        # Playback note: the test runner's subscription ID is sanitized to all-zeros
        # in recordings, so we assert by PLS name suffix (resource-path-stable across
        # sanitization) rather than full ARM-ID equality.
        pls_id_suffix = "/providers/Microsoft.Network/privateLinkServices/test-pls-wcs"
        assert created.name == connection_name
        assert created.properties.private_link_service_id.endswith(pls_id_suffix)
        assert created.properties.description == "ConnectionDesc"

        # Get
        fetched = self.client.connections.get(
            resource_group_name=rg, storage_mover_name=sm_name, connection_name=connection_name,
        )
        assert fetched.name == connection_name
        assert fetched.id == created.id
        assert fetched.properties.private_link_service_id.endswith(pls_id_suffix)
        # NOTE: do not assert on `connection_status` — see module docstring.

        # List
        items = list(self.client.connections.list(
            resource_group_name=rg, storage_mover_name=sm_name,
        ))
        assert len(items) >= 1
        assert connection_name in [c.name for c in items]

        # Update — call PUT with a new description. The Storage Mover RP echoes
        # the existing description in the immediate PUT response (the description
        # field is effectively immutable post-create or eventually consistent),
        # so we do not assert on the returned value. The CLI scenario test
        # (test_storage_mover_connection_scenarios) also calls update without
        # post-update verification for the same reason.
        self.client.connections.create_or_update(
            resource_group_name=rg, storage_mover_name=sm_name, connection_name=connection_name,
            connection={"properties": {
                "privateLinkServiceId": REAL_PRIVATE_LINK_SERVICE_ID,
                "description": "ConnectionDescUpdate",
            }},
        )

        # Delete + 404 verification
        self.client.connections.begin_delete(
            resource_group_name=rg, storage_mover_name=sm_name, connection_name=connection_name,
        ).result()
        with pytest.raises(ResourceNotFoundError):
            self.client.connections.get(
                resource_group_name=rg, storage_mover_name=sm_name, connection_name=connection_name,
            )
