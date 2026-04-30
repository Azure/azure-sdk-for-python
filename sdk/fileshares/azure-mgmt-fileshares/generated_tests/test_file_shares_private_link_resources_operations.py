# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Live-runnable rewrites of the generated PrivateLinkResources tests."""
from azure.mgmt.fileshares import FileSharesClient

from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

from _helpers import (
    ARM_ENDPOINT,
    RESOURCE_GROUP,
    create_share,
    delete_share,
)


class TestFileSharesPrivateLinkResourcesOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            FileSharesClient,
            base_url=ARM_ENDPOINT,
            credential_scopes=["https://management.azure.com/.default"],
        )

    @recorded_by_proxy
    def test_private_link_resources_list(self, variables):
        share_name, _ = create_share(self.client, variables)
        try:
            result = list(
                self.client.private_link_resources.list(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=share_name,
                )
            )
            assert isinstance(result, list)
        finally:
            delete_share(self.client, share_name)
        return variables

    @recorded_by_proxy
    def test_private_link_resources_get(self, variables):
        share_name, _ = create_share(self.client, variables)
        try:
            resources = list(
                self.client.private_link_resources.list(
                    resource_group_name=RESOURCE_GROUP,
                    resource_name=share_name,
                )
            )
            if not resources:
                return variables
            plr_name = variables.setdefault("plr_name", resources[0].name)
            got = self.client.private_link_resources.get(
                resource_group_name=RESOURCE_GROUP,
                resource_name=share_name,
                private_link_resource_name=plr_name,
            )
            assert got is not None
        finally:
            delete_share(self.client, share_name)
        return variables
