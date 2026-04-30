# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Live-runnable rewrites of the generated FileSharesOperations tests.

Uses the test-proxy ``variables`` mechanism so randomly-generated resource
names are persisted across record/playback (proxy URI matching is exact).
Assertions avoid fields the proxy scrubs to ``"Sanitized"`` (id/name) and
focus on payload/response fields that survive sanitization (tags, location,
provisioning_state, protocol, etc).
"""
import pytest
from azure.core.exceptions import ResourceNotFoundError
from azure.mgmt.fileshares import FileSharesClient, models as fs_models

from devtools_testutils import AzureMgmtRecordedTestCase, recorded_by_proxy

from _helpers import (
    ARM_ENDPOINT,
    AZURE_LOCATION,
    RESOURCE_GROUP,
    build_share_payload,
    create_share,
    delete_share,
    random_share_name,
)


class TestFileSharesFileSharesOperations(AzureMgmtRecordedTestCase):
    def setup_method(self, method):
        self.client = self.create_mgmt_client(
            FileSharesClient,
            base_url=ARM_ENDPOINT,
            credential_scopes=["https://management.azure.com/.default"],
        )

    @recorded_by_proxy
    def test_file_shares_get(self, variables):
        name, _ = create_share(self.client, variables)
        try:
            got = self.client.file_shares.get(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
            )
            assert got is not None
            assert got.properties.provisioning_state == "Succeeded"
        finally:
            delete_share(self.client, name)
        return variables

    @recorded_by_proxy
    def test_file_shares_begin_create_or_update(self, variables):
        name = random_share_name(variables)
        try:
            created = self.client.file_shares.begin_create_or_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                resource=build_share_payload(),
            ).result()
            assert created.location.lower() == AZURE_LOCATION.lower()
            assert created.properties.protocol == "NFS"
        finally:
            delete_share(self.client, name)
        return variables

    @recorded_by_proxy
    def test_file_shares_begin_update(self, variables):
        name, _ = create_share(self.client, variables)
        try:
            updated = self.client.file_shares.begin_update(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
                properties=fs_models.FileShareUpdate(
                    tags={"lifecycle": "crud", "test": "nfs", "updated": "true", "version": "2"},
                ),
            ).result()
            assert updated.tags.get("updated") == "true"
            assert updated.tags.get("version") == "2"
        finally:
            delete_share(self.client, name)
        return variables

    @recorded_by_proxy
    def test_file_shares_begin_delete(self, variables):
        name, _ = create_share(self.client, variables)
        self.client.file_shares.begin_delete(
            resource_group_name=RESOURCE_GROUP,
            resource_name=name,
        ).result()
        with pytest.raises(ResourceNotFoundError):
            self.client.file_shares.get(
                resource_group_name=RESOURCE_GROUP,
                resource_name=name,
            )
        return variables

    @recorded_by_proxy
    def test_file_shares_list_by_subscription(self, variables):
        result = list(self.client.file_shares.list_by_subscription())
        assert isinstance(result, list)
        return variables

    @recorded_by_proxy
    def test_file_shares_list_by_parent(self, variables):
        name, _ = create_share(self.client, variables)
        try:
            result = list(
                self.client.file_shares.list_by_parent(resource_group_name=RESOURCE_GROUP)
            )
            # Names are sanitized in playback; just verify the list is non-empty.
            assert len(result) >= 1
        finally:
            delete_share(self.client, name)
        return variables

    @recorded_by_proxy
    def test_file_shares_check_name_availability(self, variables):
        name = random_share_name(variables)
        response = self.client.file_shares.check_name_availability(
            location=AZURE_LOCATION,
            body={"name": name, "type": "Microsoft.FileShares/fileShares"},
        )
        assert response.name_available is True
        return variables
