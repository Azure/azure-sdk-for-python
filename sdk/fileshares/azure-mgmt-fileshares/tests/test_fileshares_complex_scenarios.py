# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Complex scenario tests for ``Microsoft.FileShares``."""

from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

from _fs_test_helpers import (  # type: ignore[import-not-found]
    RESOURCE_GROUP,
    build_share_payload,
    build_share_update,
    make_client,
    safe_delete_share,
    var_share,
)


class TestFileSharesComplexScenarios(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = make_client(self)

    @recorded_by_proxy
    def test_bulk_create_list_update_delete(self, variables):
        bulk_count = 3
        names = [var_share(variables, f"share_name_{i}", f"bulk-{i}") for i in range(bulk_count)]
        try:
            for i, name in enumerate(names):
                created = self.client.file_shares.begin_create_or_update(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=name,
                    resource=build_share_payload(
                        provisioned_storage_gi_b=100 + (i * 50),
                        tags={"bulk": "true", "index": str(i)},
                    ),
                ).result()
                assert created.name == name
                assert created.properties.provisioning_state == "Succeeded"

            listed_names = {s.name for s in self.client.file_shares.list_by_parent(resource_group_name=RESOURCE_GROUP)}
            for name in names:
                assert name in listed_names

            for name in names:
                updated = self.client.file_shares.begin_update(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=name,
                    properties=build_share_update(tags={"bulk": "true", "stage": "updated"}),
                ).result()
                assert updated.tags.get("stage") == "updated"
        finally:
            for name in names:
                safe_delete_share(self.client, RESOURCE_GROUP, name)
        return variables

    @recorded_by_proxy
    def test_nfs_root_squash_variants(self, variables):
        for squash in ("RootSquash", "NoRootSquash", "AllSquash"):
            name = var_share(variables, f"share_name_{squash}", f"squash-{squash.lower()}")
            try:
                created = self.client.file_shares.begin_create_or_update(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=name,
                    resource=build_share_payload(
                        nfs_root_squash=squash,
                        tags={"squash": squash},
                    ),
                ).result()
                assert created.properties.nfs_protocol_properties is not None
                assert created.properties.nfs_protocol_properties.root_squash == squash
            finally:
                safe_delete_share(self.client, RESOURCE_GROUP, name)
        return variables

    @recorded_by_proxy
    def test_redundancy_variants(self, variables):
        for redundancy in ("Local", "Zone"):
            name = var_share(variables, f"share_name_{redundancy}", f"redund-{redundancy.lower()}")
            try:
                created = self.client.file_shares.begin_create_or_update(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=name,
                    resource=build_share_payload(
                        redundancy=redundancy,
                        tags={"redundancy": redundancy},
                    ),
                ).result()
                assert created.properties.redundancy == redundancy
            finally:
                safe_delete_share(self.client, RESOURCE_GROUP, name)
        return variables

    @recorded_by_proxy
    def test_scale_up_via_update(self, variables):
        name = var_share(variables, "share_name", "scaleup")
        try:
            self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(
                    provisioned_storage_gi_b=100,
                    provisioned_io_per_sec=3300,
                    provisioned_throughput_mi_b_per_sec=200,
                ),
            ).result()

            updated = self.client.file_shares.begin_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                properties=build_share_update(
                    provisioned_storage_gi_b=200,
                    provisioned_io_per_sec=4000,
                    provisioned_throughput_mi_b_per_sec=300,
                ),
            ).result()
            assert updated.properties.provisioning_state == "Succeeded"
            assert updated.properties.provisioned_storage_gi_b == 200
            assert updated.properties.provisioned_io_per_sec == 4000
            assert updated.properties.provisioned_throughput_mi_b_per_sec == 300
        finally:
            safe_delete_share(self.client, RESOURCE_GROUP, name)
        return variables
