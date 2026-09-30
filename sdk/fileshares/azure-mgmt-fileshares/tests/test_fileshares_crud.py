# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""End-to-end CRUD test for the Microsoft.FileShares RP.

Creates a file share, gets it, updates a tag, lists by parent (resource group),
and finally deletes it. Targets the public East US region.
"""

import os
import uuid

import pytest
from azure.mgmt.fileshares import FileSharesMgmtClient
from azure.mgmt.fileshares import models as fs_models

from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

ARM_ENDPOINT = os.environ.get("ARM_ENDPOINT", "https://management.azure.com")

# Pre-existing resource group provisioned for CRUD testing in East US.
# Override via env var if you want to point the test at a different RG.
RESOURCE_GROUP = os.environ.get("FILESHARES_TEST_RG", "sdk-python-eastus-fileshares-crud-rg")
LOCATION = os.environ.get("FILESHARES_TEST_LOCATION", "eastus")


def _build_payload(location: str) -> fs_models.FileShare:
    """Build a minimal-but-valid FileShare payload (mirrors the sample GET response)."""
    # Values mirror the Az.FileShare PowerShell CRUD test
    # (src/FileShare/FileShare.Autorest/test/FileShare-CRUD.Tests.ps1).
    return fs_models.FileShare(
        location=location,
        tags={"lifecycle": "crud", "test": "nfs", "owner": "azsdk-crud-test"},
        properties=fs_models.FileShareProperties(
            mount_name="theshare",
            media_tier="SSD",
            redundancy="Local",
            protocol="NFS",
            provisioned_storage_gi_b=1024,
            provisioned_io_per_sec=4024,
            provisioned_throughput_mi_b_per_sec=228,
            nfs_protocol_properties=fs_models.NfsProtocolProperties(root_squash="NoRootSquash"),
        ),
    )


class TestFileSharesCrud(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            FileSharesMgmtClient,
            base_url=ARM_ENDPOINT,
            credential_scopes=["https://management.azure.com/.default"],
        )

    # No proxy recording is committed for this test yet, so it only runs when
    # AZURE_TEST_RUN_LIVE=true. Once a recording is captured and pushed to the
    # assets repo, this marker can be removed.
    @pytest.mark.live_test_only
    @recorded_by_proxy
    def test_file_share_crud(self):
        # Use a short, unique name per run so concurrent test runs don't collide.
        # Service requires lowercase letters/digits/hyphens; keep it under 63 chars.
        share_name = f"fs-azsdk-{uuid.uuid4().hex[:10]}"

        # ---------- CREATE ----------
        created = self.client.file_shares.begin_create_or_update(
            resource_group_name=RESOURCE_GROUP,
            resource_name=share_name,
            resource=_build_payload(LOCATION),
        ).result()

        assert created is not None
        assert created.name == share_name
        assert created.location.lower() == LOCATION.lower()
        assert created.properties is not None
        assert created.properties.provisioning_state == "Succeeded"
        assert created.properties.protocol == "NFS"
        assert created.properties.media_tier == "SSD"
        assert created.properties.provisioned_storage_gi_b == 1024

        try:
            # ---------- GET ----------
            got = self.client.file_shares.get(
                resource_group_name=RESOURCE_GROUP,
                resource_name=share_name,
            )
            assert got.name == share_name
            assert got.tags.get("lifecycle") == "crud"
            assert got.properties.host_name  # populated by service

            # ---------- UPDATE (tag only) ----------
            updated = self.client.file_shares.begin_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=share_name,
                properties=fs_models.FileShareUpdate(
                    tags={"lifecycle": "crud", "test": "nfs", "updated": "true", "version": "2"},
                ),
            ).result()
            assert updated.tags.get("updated") == "true"
            assert updated.tags.get("version") == "2"

            # ---------- LIST ----------
            listed = list(self.client.file_shares.list_by_parent(resource_group_name=RESOURCE_GROUP))
            assert any(s.name == share_name for s in listed)

        finally:
            # ---------- DELETE ----------
            self.client.file_shares.begin_delete(
                resource_group_name=RESOURCE_GROUP,
                resource_name=share_name,
            ).result()

        # Verify gone (404)
        from azure.core.exceptions import ResourceNotFoundError

        with pytest.raises(ResourceNotFoundError):
            self.client.file_shares.get(
                resource_group_name=RESOURCE_GROUP,
                resource_name=share_name,
            )
