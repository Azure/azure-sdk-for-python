# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime
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


class TestSharedAccessSignatureUserDelegationGaps(StorageRecordedTestCase):

    def _create_user_delegation_key(self):
        user_delegation_key = UserDelegationKey()
        user_delegation_key.signed_oid = "signed-oid"
        user_delegation_key.signed_tid = "signed-tid"
        user_delegation_key.signed_start = "2024-01-01T00:00:00Z"
        user_delegation_key.signed_expiry = "2024-01-02T00:00:00Z"
        user_delegation_key.signed_service = "b"
        user_delegation_key.signed_version = X_MS_VERSION
        user_delegation_key.signed_delegated_user_tid = "delegated-user-tid"
        user_delegation_key.value = "a" * 30 + "b" * 30
        return user_delegation_key

    def test_generate_blob_sas_when_request_headers_provided_with_user_delegation_key_adds_srh_query_parameter(self):
        user_delegation_key = self._create_user_delegation_key()

        token = generate_blob_sas(
            account_name="testaccount",
            container_name="container",
            blob_name="blob",
            user_delegation_key=user_delegation_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime(2024, 1, 2, 0, 0),
            request_headers={"x-ms-meta-a": "value-a", "x-ms-meta-b": "value-b"},
        )

        parsed_token = parse_qs(token)
        assert parsed_token[QueryStringConstants.SIGNED_REQUEST_HEADERS] == ["x-ms-meta-a,x-ms-meta-b"]

    def test_generate_container_sas_when_request_query_params_provided_with_user_delegation_key_adds_srq_query_parameter(self):
        user_delegation_key = self._create_user_delegation_key()

        token = generate_container_sas(
            account_name="testaccount",
            container_name="container",
            user_delegation_key=user_delegation_key,
            permission=ContainerSasPermissions(read=True),
            expiry=datetime(2024, 1, 2, 0, 0),
            request_query_params={"comp": "metadata", "timeout": "30"},
        )

        parsed_token = parse_qs(token)
        assert parsed_token[QueryStringConstants.SIGNED_REQUEST_QUERY_PARAMS] == ["comp,timeout"]

    def test_generate_container_sas_when_hns_user_delegation_values_provided_includes_them_in_string_to_sign(self):
        user_delegation_key = self._create_user_delegation_key()
        string_to_sign = []

        generate_container_sas(
            account_name="testaccount",
            container_name="container",
            user_delegation_key=user_delegation_key,
            permission=ContainerSasPermissions(read=True),
            expiry=datetime(2024, 1, 2, 0, 0),
            user_delegation_oid="delegated-user-oid",
            preauthorized_agent_object_id="authorized-oid",
            agent_object_id="unauthorized-oid",
            correlation_id="correlation-id",
            sts_hook=string_to_sign.append,
        )

        assert len(string_to_sign) == 1
        assert "authorized-oid\nunauthorized-oid\ncorrelation-id\ndelegated-user-tid\ndelegated-user-oid" in string_to_sign[0]

    def test_generate_blob_sas_when_user_delegation_key_has_no_request_headers_adds_blank_headers_line_to_string_to_sign(self):
        user_delegation_key = self._create_user_delegation_key()
        string_to_sign = []

        generate_blob_sas(
            account_name="testaccount",
            container_name="container",
            blob_name="blob",
            user_delegation_key=user_delegation_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime(2024, 1, 2, 0, 0),
            encryption_scope="scope1",
            sts_hook=string_to_sign.append,
        )

        assert len(string_to_sign) == 1
        assert "\nscope1\n\n\n" in string_to_sign[0]

    def test_generate_blob_sas_when_request_query_params_provided_with_user_delegation_key_appends_query_param_lines_to_string_to_sign(self):
        user_delegation_key = self._create_user_delegation_key()
        string_to_sign = []

        generate_blob_sas(
            account_name="testaccount",
            container_name="container",
            blob_name="blob",
            user_delegation_key=user_delegation_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime(2024, 1, 2, 0, 0),
            encryption_scope="scope1",
            request_query_params={"comp": "metadata", "timeout": "30"},
            sts_hook=string_to_sign.append,
        )

        assert len(string_to_sign) == 1
        assert "scope1\n\n\ncomp:metadata\ntimeout:30\n" in string_to_sign[0]
