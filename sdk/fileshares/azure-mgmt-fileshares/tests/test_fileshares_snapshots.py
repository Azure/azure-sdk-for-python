# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Snapshot tests for ``Microsoft.FileShares``."""

import pytest
from azure.core.exceptions import ResourceNotFoundError

from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

from _fs_test_helpers import (  # type: ignore[import-not-found]
    RESOURCE_GROUP,
    build_share_payload,
    build_snapshot_payload,
    make_client,
    safe_delete_share,
    safe_delete_snapshot,
    var_share,
    var_snapshot,
)


class TestFileSharesSnapshots(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = make_client(self)

    @recorded_by_proxy
    def test_snapshot_crud(self, variables):
        share_name = var_share(variables, "share_name", "snap-parent")
        snapshot_name = var_snapshot(variables, "snapshot_name", "snap")
        try:
            self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=share_name,
                resource=build_share_payload(),
            ).result()

            try:
                created = self.client.file_share_snapshots.begin_create_or_update_file_share_snapshot(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=share_name,
                    name=snapshot_name,
                    resource=build_snapshot_payload(metadata={"purpose": "testing"}),
                ).result()
                assert created.name == snapshot_name
                assert created.properties is not None
                assert created.properties.metadata.get("purpose") == "testing"

                got = self.client.file_share_snapshots.get_file_share_snapshot(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=share_name,
                    name=snapshot_name,
                )
                assert got.name == snapshot_name

                listed = list(
                    self.client.file_share_snapshots.list_by_file_share(
                        resource_group_name=RESOURCE_GROUP,
                        resource_name=share_name,
                    )
                )
                assert any(s.name == snapshot_name for s in listed)

                self.client.file_share_snapshots.begin_delete_file_share_snapshot(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=share_name,
                    name=snapshot_name,
                ).result()
                with pytest.raises(ResourceNotFoundError):
                    self.client.file_share_snapshots.get_file_share_snapshot(
                        resource_group_name=RESOURCE_GROUP,
                        resource_name=share_name,
                        name=snapshot_name,
                    )
            finally:
                safe_delete_snapshot(self.client, RESOURCE_GROUP, share_name, snapshot_name)
        finally:
            safe_delete_share(self.client, RESOURCE_GROUP, share_name)
        return variables

    @recorded_by_proxy
    def test_multiple_snapshots_listing(self, variables):
        share_name = var_share(variables, "share_name", "multisnap-parent")
        snapshot_names = [var_snapshot(variables, f"snapshot_name_{i}", f"snap-{i}") for i in range(3)]
        try:
            self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=share_name,
                resource=build_share_payload(),
            ).result()

            for i, snap in enumerate(snapshot_names):
                self.client.file_share_snapshots.begin_create_or_update_file_share_snapshot(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=share_name,
                    name=snap,
                    resource=build_snapshot_payload(metadata={"generation": str(i)}),
                ).result()

            listed = {
                s.name
                for s in self.client.file_share_snapshots.list_by_file_share(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=share_name,
                )
            }
            for snap in snapshot_names:
                assert snap in listed
        finally:
            for snap in snapshot_names:
                safe_delete_snapshot(self.client, RESOURCE_GROUP, share_name, snap)
            safe_delete_share(self.client, RESOURCE_GROUP, share_name)
        return variables
