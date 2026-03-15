# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timedelta
from urllib.parse import parse_qs

import pytest
from azure.storage.blob import (
    BlobSasPermissions,
    ContainerSasPermissions,
    UserDelegationKey,
    generate_blob_sas,
    generate_container_sas,
)

from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer


class TestSharedAccessSignatureValidationGaps(StorageRecordedTestCase):

    def _create_user_delegation_key(self, account_key):
        user_delegation_key = UserDelegationKey()
        user_delegation_key.signed_oid = "delegated-object-id"
        user_delegation_key.signed_tid = "delegated-tenant-id"
        user_delegation_key.signed_start = "2020-01-01T00:00:00Z"
        user_delegation_key.signed_expiry = "2020-01-02T00:00:00Z"
        user_delegation_key.signed_service = "b"
        user_delegation_key.signed_version = "2020-02-10"
        user_delegation_key.signed_delegated_user_tid = "delegated-user-tenant-id"
        user_delegation_key.value = account_key
        return user_delegation_key

    @BlobPreparer()
    def test_generate_blob_sas_when_content_type_provided_trims_trailing_newline(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        captured = []
        token = generate_blob_sas(
            account_name=storage_account_name,
            container_name="container",
            blob_name="blob",
            account_key=storage_account_key.secret,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            content_type="text/plain",
            sts_hook=captured.append,
        )

        parsed_token = parse_qs(token)
        assert captured[0].endswith("text/plain")
        assert captured[0][-1] == "n"
        assert parsed_token["rsct"] == ["text/plain"]

    @BlobPreparer()
    def test_generate_container_sas_when_policy_id_not_provided_generates_permission_based_token(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        token = generate_container_sas(
            account_name=storage_account_name,
            container_name="container",
            account_key=storage_account_key.secret,
            permission=ContainerSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        parsed_token = parse_qs(token)
        assert parsed_token["sp"] == ["r"]
        assert parsed_token["sr"] == ["c"]
        assert "si" not in parsed_token

    @BlobPreparer()
    def test_generate_container_sas_when_policy_id_not_provided_and_permission_missing_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        with pytest.raises(ValueError) as error:
            generate_container_sas(
                account_name=storage_account_name,
                container_name="container",
                account_key=storage_account_key.secret,
                expiry=datetime.utcnow() + timedelta(hours=1),
            )

        assert str(error.value) == "'permission' parameter must be provided when not using a stored access policy."

    @BlobPreparer()
    def test_generate_container_sas_when_user_delegation_key_passed_as_account_key_uses_delegation_fields(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        user_delegation_key = self._create_user_delegation_key(storage_account_key.secret)
        token = generate_container_sas(
            account_name=storage_account_name,
            container_name="container",
            account_key=user_delegation_key,
            permission=ContainerSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        parsed_token = parse_qs(token)
        assert parsed_token["skoid"] == ["delegated-object-id"]
        assert parsed_token["sktid"] == ["delegated-tenant-id"]
        assert parsed_token["sr"] == ["c"]

    @BlobPreparer()
    def test_generate_blob_sas_when_policy_id_not_provided_and_credentials_missing_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        with pytest.raises(ValueError) as error:
            generate_blob_sas(
                account_name=storage_account_name,
                container_name="container",
                blob_name="blob",
                permission=BlobSasPermissions(read=True),
                expiry=datetime.utcnow() + timedelta(hours=1),
            )

        assert str(error.value) == "Either user_delegation_key or account_key must be provided."
