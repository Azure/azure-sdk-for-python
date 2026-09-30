# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Private-endpoint surface tests for ``Microsoft.FileShares``.

Inspired by the read-only portions of
``azure-powershell/src/FileShare/FileShare.Autorest/test/FileShare-PrivateEndpoint.Tests.ps1``.
VNet/Subnet/PE provisioning belongs to ``azure-mgmt-network`` and is intentionally
excluded — these tests cover only the FileShares-side PE/private-link surface.
"""

from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

from _fs_test_helpers import (  # type: ignore[import-not-found]
    RESOURCE_GROUP,
    build_share_payload,
    make_client,
    safe_delete_share,
    var_share,
)


class TestFileSharesPrivateEndpoint(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = make_client(self)

    @recorded_by_proxy
    def test_list_private_link_resources(self, variables):
        name = var_share(variables, "share_name", "plr")
        try:
            self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(),
            ).result()

            resources = list(
                self.client.private_link_resources.list(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=name,
                )
            )
            assert len(resources) > 0
            for plr in resources:
                assert plr.name
                assert plr.properties is not None
        finally:
            safe_delete_share(self.client, RESOURCE_GROUP, name)
        return variables

    @recorded_by_proxy
    def test_list_private_endpoint_connections_empty(self, variables):
        name = var_share(variables, "share_name", "pec-empty")
        try:
            self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(),
            ).result()

            connections = list(
                self.client.private_endpoint_connections.list_by_file_share(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=name,
                )
            )
            assert connections == []
        finally:
            safe_delete_share(self.client, RESOURCE_GROUP, name)
        return variables
