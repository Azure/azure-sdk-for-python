# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Live-runnable rewrites of the generated FileShareSnapshots tests."""
import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.fileshares import FileSharesClient, models as fs_models

from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

from _helpers import (
    ARM_ENDPOINT,
    RESOURCE_GROUP,
    create_share,
    delete_share,
    random_snapshot_name,
)


class TestFileSharesFileShareSnapshotsOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            FileSharesClient,
            base_url=ARM_ENDPOINT,
            credential_scopes=["https://management.azure.com/.default"],
        )

    def _create_snapshot(self, share_name: str, snap_name: str):
        return self.client.file_share_snapshots.begin_create_or_update_file_share_snapshot(
            resource_group_name=RESOURCE_GROUP,
            resource_name=share_name,
            name=snap_name,
            resource=fs_models.FileShareSnapshot(
                properties=fs_models.FileShareSnapshotProperties(
                    metadata={"purpose": "testing", "environment": "test"},
                ),
            ),
        ).result()

    @recorded_by_proxy
    def test_file_share_snapshots_get_file_share_snapshot(self, variables):
        share_name, _ = create_share(self.client, variables)
        snap_name = random_snapshot_name(variables)
        try:
            self._create_snapshot(share_name, snap_name)
            got = self.client.file_share_snapshots.get_file_share_snapshot(
                resource_group_name=RESOURCE_GROUP,
                resource_name=share_name,
                name=snap_name,
            )
            assert got is not None
        finally:
            delete_share(self.client, share_name)
        return variables

    @recorded_by_proxy
    def test_file_share_snapshots_begin_create_or_update_file_share_snapshot(self, variables):
        share_name, _ = create_share(self.client, variables)
        snap_name = random_snapshot_name(variables)
        try:
            created = self._create_snapshot(share_name, snap_name)
            assert created is not None
            assert created.properties.metadata.get("purpose") == "testing"
        finally:
            delete_share(self.client, share_name)
        return variables

    @recorded_by_proxy
    def test_file_share_snapshots_begin_update_file_share_snapshot(self, variables):
        share_name, _ = create_share(self.client, variables)
        snap_name = random_snapshot_name(variables)
        try:
            self._create_snapshot(share_name, snap_name)
            updated = self.client.file_share_snapshots.begin_update_file_share_snapshot(
                resource_group_name=RESOURCE_GROUP,
                resource_name=share_name,
                name=snap_name,
                properties=fs_models.FileShareSnapshotUpdate(
                    properties=fs_models.FileShareSnapshotUpdateProperties(
                        metadata={"purpose": "testing", "stage": "updated"},
                    ),
                ),
            ).result()
            assert updated.properties.metadata.get("stage") == "updated"
        finally:
            delete_share(self.client, share_name)
        return variables

    @recorded_by_proxy
    def test_file_share_snapshots_begin_delete_file_share_snapshot(self, variables):
        share_name, _ = create_share(self.client, variables)
        snap_name = random_snapshot_name(variables)
        try:
            self._create_snapshot(share_name, snap_name)
            self.client.file_share_snapshots.begin_delete_file_share_snapshot(
                resource_group_name=RESOURCE_GROUP,
                resource_name=share_name,
                name=snap_name,
            ).result()
            with pytest.raises(ResourceNotFoundError):
                self.client.file_share_snapshots.get_file_share_snapshot(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=share_name,
                    name=snap_name,
                )
        finally:
            delete_share(self.client, share_name)
        return variables

    @recorded_by_proxy
    def test_file_share_snapshots_list_by_file_share(self, variables):
        share_name, _ = create_share(self.client, variables)
        snap_name = random_snapshot_name(variables)
        try:
            self._create_snapshot(share_name, snap_name)
            result = list(
                self.client.file_share_snapshots.list_by_file_share(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=share_name,
                )
            )
            assert len(result) >= 1
        finally:
            delete_share(self.client, share_name)
        return variables
