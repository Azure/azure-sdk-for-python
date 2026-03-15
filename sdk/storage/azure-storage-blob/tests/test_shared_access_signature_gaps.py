# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from datetime import datetime, timedelta
import base64
from urllib.parse import parse_qs

from azure.storage.blob import (
    BlobSasPermissions,
    ContainerSasPermissions,
    UserDelegationKey,
    generate_blob_sas,
    generate_container_sas,
)
from azure.storage.blob._shared.constants import X_MS_VERSION
from azure.storage.blob._shared.shared_access_signature import QueryStringConstants

from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer


class TestSharedAccessSignatureGaps(StorageRecordedTestCase):

    def _get_account_key(self):
        return base64.b64encode(b"shared-key-for-tests").decode("utf-8")

    def _get_user_delegation_key(self):
        user_delegation_key = UserDelegationKey()
        user_delegation_key.signed_oid = "object-id"
        user_delegation_key.signed_tid = "tenant-id"
        user_delegation_key.signed_start = "2023-01-01T00:00:00Z"
        user_delegation_key.signed_expiry = "2024-01-01T00:00:00Z"
        user_delegation_key.signed_service = "b"
        user_delegation_key.signed_version = "2020-10-02"
        user_delegation_key.signed_delegated_user_tid = "delegated-tenant-id"
        user_delegation_key.value = base64.b64encode(b"user-delegation-key").decode("utf-8")
        return user_delegation_key

    @BlobPreparer()
    def test_generate_blob_when_sts_hook_provided_calls_hook_with_string_to_sign(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        captured = []
        generate_blob_sas(
            account_name=storage_account_name,
            container_name="container",
            blob_name="blob",
            account_key=self._get_account_key(),
            permission=BlobSasPermissions(read=True),
            expiry="2024-01-01T00:00:00Z",
            sts_hook=captured.append,
        )

        expected = "\n".join([
            "r",
            "",
            "2024-01-01T00:00:00Z",
            f"/blob/{storage_account_name}/container/blob",
            "",
            "",
            "",
            X_MS_VERSION,
            "b",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ])
        assert captured == [expected]

    @BlobPreparer()
    def test_generate_container_when_sts_hook_provided_calls_hook_with_string_to_sign(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        captured = []
        generate_container_sas(
            account_name=storage_account_name,
            container_name="container",
            account_key=self._get_account_key(),
            permission=ContainerSasPermissions(read=True),
            expiry="2024-01-01T00:00:00Z",
            sts_hook=captured.append,
        )

        expected = "\n".join([
            "r",
            "",
            "2024-01-01T00:00:00Z",
            f"/blob/{storage_account_name}/container",
            "",
            "",
            "",
            X_MS_VERSION,
            "c",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ])
        assert captured == [expected]

    @BlobPreparer()
    def test_generate_blob_when_resource_path_has_no_leading_slash_adds_canonical_slash(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        captured = []
        generate_blob_sas(
            account_name=storage_account_name,
            container_name="container",
            blob_name="blob",
            account_key=self._get_account_key(),
            permission=BlobSasPermissions(read=True),
            expiry="2024-01-01T00:00:00Z",
            sts_hook=captured.append,
        )

        assert captured[0].split("\n")[3] == f"/blob/{storage_account_name}/container/blob"

    @BlobPreparer()
    def test_generate_container_when_user_delegation_key_provided_adds_delegation_fields(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        token = generate_container_sas(
            account_name=storage_account_name,
            container_name="container",
            user_delegation_key=self._get_user_delegation_key(),
            permission=ContainerSasPermissions(read=True),
            expiry="2024-01-01T00:00:00Z",
            correlation_id="correlation-id",
            user_delegation_oid="delegated-user-oid",
            request_headers={"x-ms-meta-test": "true"},
            request_query_params={"comp": "metadata"},
        )

        parsed_token = parse_qs(token)
        assert parsed_token[QueryStringConstants.SIGNED_OID] == ["object-id"]
        assert parsed_token[QueryStringConstants.SIGNED_KEY_VERSION] == ["2020-10-02"]
        assert parsed_token[QueryStringConstants.SIGNED_REQUEST_HEADERS] == ["x-ms-meta-test"]
        assert parsed_token[QueryStringConstants.SIGNED_REQUEST_QUERY_PARAMS] == ["comp"]
        assert parsed_token[QueryStringConstants.SIGNED_CORRELATION_ID] == ["correlation-id"]
        assert parsed_token[QueryStringConstants.SIGNED_KEY_DELEGATED_USER_TID] == ["delegated-tenant-id"]
        assert parsed_token[QueryStringConstants.SIGNED_DELEGATED_USER_OID] == ["delegated-user-oid"]

    @BlobPreparer()
    def test_generate_blob_when_user_delegation_key_provided_adds_signed_tid(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")

        token = generate_blob_sas(
            account_name=storage_account_name,
            container_name="container",
            blob_name="blob",
            user_delegation_key=self._get_user_delegation_key(),
            permission=BlobSasPermissions(read=True),
            expiry="2024-01-01T00:00:00Z",
        )

        parsed_token = parse_qs(token)
        assert parsed_token[QueryStringConstants.SIGNED_TID] == ["tenant-id"]
        assert parsed_token[QueryStringConstants.SIGNED_RESOURCE] == ["b"]

    def _create_user_delegation_key(self):
        user_delegation_key = UserDelegationKey()
        user_delegation_key.signed_oid = '11111111-1111-1111-1111-111111111111'
        user_delegation_key.signed_tid = '22222222-2222-2222-2222-222222222222'
        user_delegation_key.signed_start = '2024-01-01T00:00:00Z'
        user_delegation_key.signed_expiry = '2024-01-02T00:00:00Z'
        user_delegation_key.signed_service = 'b'
        user_delegation_key.signed_version = '2023-11-03'
        user_delegation_key.signed_delegated_user_tid = '33333333-3333-3333-3333-333333333333'
        user_delegation_key.value = 'a' * 30 + 'b' * 30
        return user_delegation_key

    @BlobPreparer()
    def test_generate_blob_sas_when_user_delegation_key_has_signed_start_adds_skt_query_parameter(self, **kwargs):
        storage_account_name = kwargs.pop('storage_account_name')
        user_delegation_key = self._create_user_delegation_key()

        token = generate_blob_sas(
            account_name=storage_account_name,
            container_name='container',
            blob_name='blob',
            user_delegation_key=user_delegation_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        parsed_token = parse_qs(token)
        assert parsed_token[QueryStringConstants.SIGNED_KEY_START] == [user_delegation_key.signed_start]

    @BlobPreparer()
    def test_generate_container_sas_when_user_delegation_key_has_signed_expiry_adds_ske_query_parameter(self, **kwargs):
        storage_account_name = kwargs.pop('storage_account_name')
        user_delegation_key = self._create_user_delegation_key()

        token = generate_container_sas(
            account_name=storage_account_name,
            container_name='container',
            user_delegation_key=user_delegation_key,
            permission=ContainerSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        parsed_token = parse_qs(token)
        assert parsed_token[QueryStringConstants.SIGNED_KEY_EXPIRY] == [user_delegation_key.signed_expiry]

    @BlobPreparer()
    def test_generate_blob_sas_when_user_delegation_key_passed_as_account_key_adds_sks_query_parameter(self, **kwargs):
        storage_account_name = kwargs.pop('storage_account_name')
        user_delegation_key = self._create_user_delegation_key()

        token = generate_blob_sas(
            account_name=storage_account_name,
            container_name='container',
            blob_name='blob',
            account_key=user_delegation_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        parsed_token = parse_qs(token)
        assert parsed_token[QueryStringConstants.SIGNED_KEY_SERVICE] == [user_delegation_key.signed_service]

    @BlobPreparer()
    def test_generate_container_sas_when_user_delegation_key_passed_as_account_key_adds_skv_query_parameter(self, **kwargs):
        storage_account_name = kwargs.pop('storage_account_name')
        user_delegation_key = self._create_user_delegation_key()

        token = generate_container_sas(
            account_name=storage_account_name,
            container_name='container',
            account_key=user_delegation_key,
            permission=ContainerSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
        )

        parsed_token = parse_qs(token)
        assert parsed_token[QueryStringConstants.SIGNED_KEY_VERSION] == [user_delegation_key.signed_version]

    @BlobPreparer()
    def test_generate_blob_sas_when_user_delegation_key_has_delegated_user_tid_adds_skdutid_query_parameter(self, **kwargs):
        storage_account_name = kwargs.pop('storage_account_name')
        user_delegation_key = self._create_user_delegation_key()

        token = generate_blob_sas(
            account_name=storage_account_name,
            container_name='container',
            blob_name='blob',
            user_delegation_key=user_delegation_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1),
            user_delegation_oid='44444444-4444-4444-4444-444444444444',
        )

        parsed_token = parse_qs(token)
        assert parsed_token[QueryStringConstants.SIGNED_KEY_DELEGATED_USER_TID] == [
            user_delegation_key.signed_delegated_user_tid
        ]
