# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timedelta
from urllib.parse import parse_qs

import pytest
from azure.storage.blob import UserDelegationKey, generate_blob_sas
from azure.storage.blob._shared.shared_access_signature import QueryStringConstants

from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer


class TestSharedAccessSignatureGenerateBlobSas(StorageRecordedTestCase):

    def _create_user_delegation_key(self, key_value):
        user_delegation_key = UserDelegationKey()
        user_delegation_key.signed_oid = "oid"
        user_delegation_key.signed_tid = "tid"
        user_delegation_key.signed_start = "2020-01-01T00:00:00Z"
        user_delegation_key.signed_expiry = "2020-01-02T00:00:00Z"
        user_delegation_key.signed_service = "b"
        user_delegation_key.signed_version = "2020-02-10"
        user_delegation_key.value = key_value
        return user_delegation_key

    @BlobPreparer()
    def test_generate_blob_sas_when_policy_id_not_provided_and_permission_missing_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        with pytest.raises(ValueError) as error:
            generate_blob_sas(
                account_name=storage_account_name,
                container_name="container",
                blob_name="blob",
                account_key=storage_account_key.secret,
                expiry=datetime.utcnow() + timedelta(hours=1),
            )

        assert str(error.value) == "'permission' parameter must be provided when not using a stored access policy." 

    @BlobPreparer()
    def test_generate_blob_sas_when_account_key_is_user_delegation_key_uses_delegation_key_fields(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        token = generate_blob_sas(
            account_name=storage_account_name,
            container_name="container",
            blob_name="blob",
            account_key=self._create_user_delegation_key(storage_account_key.secret),
            permission="r",
            expiry=datetime.utcnow() + timedelta(hours=1),
        )
        parsed_token = parse_qs(token)

        assert parsed_token[QueryStringConstants.SIGNED_OID] == ["oid"]

    @BlobPreparer()
    def test_generate_blob_sas_when_snapshot_and_version_id_provided_raises_value_error(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        with pytest.raises(ValueError) as error:
            generate_blob_sas(
                account_name=storage_account_name,
                container_name="container",
                blob_name="blob",
                snapshot="2020-01-01T00:00:00.0000000Z",
                account_key=storage_account_key.secret,
                permission="r",
                expiry=datetime.utcnow() + timedelta(hours=1),
                version_id="2020-01-02T00:00:00.0000000Z",
            )

        assert str(error.value) == "snapshot and version_id cannot be set at the same time."
