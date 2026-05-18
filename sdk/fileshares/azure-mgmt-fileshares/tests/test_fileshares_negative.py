# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Negative / error-path tests for ``Microsoft.FileShares``."""

import pytest
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError

from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

from _fs_test_helpers import (  # type: ignore[import-not-found]
    RESOURCE_GROUP,
    build_share_payload,
    build_share_update,
    build_snapshot_payload,
    make_client,
    var_share,
)


class TestFileSharesNegative(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = make_client(self)

    @recorded_by_proxy
    def test_get_nonexistent_share_raises_404(self, variables):
        name = var_share(variables, "share_name", "missing")
        with pytest.raises(ResourceNotFoundError):
            self.client.file_shares.get(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
            )
        return variables

    @recorded_by_proxy
    def test_get_nonexistent_resource_group_raises(self, variables):
        name = var_share(variables, "share_name", "missing")
        with pytest.raises((ResourceNotFoundError, HttpResponseError)):
            self.client.file_shares.get(
                resource_group_name="rg-does-not-exist-azsdk-test",
                resource_name=name,
            )
        return variables

    @recorded_by_proxy
    def test_update_nonexistent_share_raises(self, variables):
        name = var_share(variables, "share_name", "missing")
        with pytest.raises((ResourceNotFoundError, HttpResponseError)):
            self.client.file_shares.begin_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                properties=build_share_update(tags={"should": "fail"}),
            ).result()
        return variables

    @recorded_by_proxy
    def test_create_invalid_location_raises(self, variables):
        name = var_share(variables, "share_name", "badloc")
        with pytest.raises(HttpResponseError):
            self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(location="invalidlocation123"),
            ).result()
        return variables

    @recorded_by_proxy
    def test_create_invalid_media_tier_raises(self, variables):
        name = var_share(variables, "share_name", "badtier")
        with pytest.raises(HttpResponseError):
            self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(media_tier="InvalidTier"),
            ).result()
        return variables

    @recorded_by_proxy
    def test_create_invalid_protocol_raises(self, variables):
        name = var_share(variables, "share_name", "badproto")
        with pytest.raises(HttpResponseError):
            self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(protocol="InvalidProtocol"),
            ).result()
        return variables

    @recorded_by_proxy
    def test_create_invalid_redundancy_raises(self, variables):
        name = var_share(variables, "share_name", "badredund")
        with pytest.raises(HttpResponseError):
            self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(redundancy="InvalidRedundancy"),
            ).result()
        return variables

    @recorded_by_proxy
    def test_create_zero_storage_raises(self, variables):
        name = var_share(variables, "share_name", "zerostorage")
        with pytest.raises(HttpResponseError):
            self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(provisioned_storage_gi_b=0),
            ).result()
        return variables

    @recorded_by_proxy
    def test_create_negative_storage_raises(self, variables):
        name = var_share(variables, "share_name", "negstorage")
        with pytest.raises(HttpResponseError):
            self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(provisioned_storage_gi_b=-100),
            ).result()
        return variables

    @recorded_by_proxy
    def test_snapshot_create_for_nonexistent_share_raises(self, variables):
        name = var_share(variables, "share_name", "missingparent")
        with pytest.raises((ResourceNotFoundError, HttpResponseError)):
            self.client.file_share_snapshots.begin_create_or_update_file_share_snapshot(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                name="orphan-snapshot",
                resource=build_snapshot_payload(),
            ).result()
        return variables
