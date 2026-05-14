# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Listing tests for ``Microsoft.FileShares`` covering both the resource-group and
subscription-scoped pagers."""

from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

from _fs_test_helpers import (  # type: ignore[import-not-found]
    RESOURCE_GROUP,
    build_share_payload,
    make_client,
    safe_delete_share,
    var_share,
)


class TestFileSharesListing(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = make_client(self)

    @recorded_by_proxy
    def test_list_by_subscription_includes_created_share(self, variables):
        name = var_share(variables, "share_name", "listsub")
        try:
            self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(),
            ).result()

            listed_names = {s.name for s in self.client.file_shares.list_by_subscription()}
            assert name in listed_names
        finally:
            safe_delete_share(self.client, RESOURCE_GROUP, name)
        return variables

    @recorded_by_proxy
    def test_list_by_parent_returns_pager(self, variables):
        name = var_share(variables, "share_name", "listrg")
        try:
            self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(),
            ).result()

            shares = list(self.client.file_shares.list_by_parent(resource_group_name=RESOURCE_GROUP))
            assert any(s.name == name for s in shares)
        finally:
            safe_delete_share(self.client, RESOURCE_GROUP, name)
        return variables
