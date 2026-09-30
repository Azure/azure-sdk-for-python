# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Edge-case tests for ``Microsoft.FileShares``.

Scenarios mirrored from
``azure-powershell/src/FileShare/FileShare.Autorest/test/FileShare-EdgeCases.Tests.ps1``:
name-length boundaries, name characters, tag count and value shapes, network-access
toggles. PowerShell-only checks (``-InputObject`` identity) are intentionally omitted.
"""

import uuid

from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

from _fs_test_helpers import (  # type: ignore[import-not-found]
    RESOURCE_GROUP,
    build_share_payload,
    build_share_update,
    make_client,
    safe_delete_share,
    var_share,
)


class TestFileSharesEdgeCases(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = make_client(self)

    @recorded_by_proxy
    def test_min_length_name(self, variables):
        """Service-acceptable minimum name length (3 chars). Fixed name (no uuid)."""
        name = "fsa"
        try:
            created = self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(),
            ).result()
            assert created.name == name
        finally:
            safe_delete_share(self.client, RESOURCE_GROUP, name)
        return variables

    @recorded_by_proxy
    def test_max_length_name(self, variables):
        """Maximum length name (63 chars), lowercase letters + digits."""
        default = ("fs" + uuid.uuid4().hex + uuid.uuid4().hex)[:63]
        name = variables.setdefault("share_name", default)
        assert len(name) == 63
        try:
            created = self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(),
            ).result()
            assert created.name == name
        finally:
            safe_delete_share(self.client, RESOURCE_GROUP, name)
        return variables

    @recorded_by_proxy
    def test_name_with_hyphens_and_digits(self, variables):
        """Hyphens and digits are valid name characters."""
        name = var_share(variables, "share_name", "share-123-edge-456")
        try:
            created = self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(),
            ).result()
            assert created.name == name
        finally:
            safe_delete_share(self.client, RESOURCE_GROUP, name)
        return variables

    @recorded_by_proxy
    def test_many_tags(self, variables):
        """A reasonably large tag set round-trips."""
        many = {f"tag{i}": f"value{i}" for i in range(15)}
        name = var_share(variables, "share_name", "manytags")
        try:
            self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(tags=many),
            ).result()
            updated = self.client.file_shares.begin_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                properties=build_share_update(tags=many),
            ).result()
            assert len(updated.tags) >= len(many)
            for key, value in many.items():
                assert updated.tags.get(key) == value
        finally:
            safe_delete_share(self.client, RESOURCE_GROUP, name)
        return variables

    @recorded_by_proxy
    def test_tags_with_special_characters(self, variables):
        """Tag values with email/path/version-style strings round-trip unchanged."""
        special = {
            "email": "test@example.com",
            "path": "/var/log/app",
            "version": "1.0.0-beta+build.123",
        }
        name = var_share(variables, "share_name", "specialtags")
        try:
            created = self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(tags=special),
            ).result()
            assert created.tags.get("email") == "test@example.com"
            assert created.tags.get("path") == "/var/log/app"
            assert created.tags.get("version") == "1.0.0-beta+build.123"
        finally:
            safe_delete_share(self.client, RESOURCE_GROUP, name)
        return variables

    @recorded_by_proxy
    def test_public_network_access_disabled_at_create(self, variables):
        """Create a share with ``PublicNetworkAccess=Disabled``."""
        name = var_share(variables, "share_name", "pnadisabled")
        try:
            created = self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(public_network_access="Disabled"),
            ).result()
            assert created.properties.public_network_access == "Disabled"
        finally:
            safe_delete_share(self.client, RESOURCE_GROUP, name)
        return variables
