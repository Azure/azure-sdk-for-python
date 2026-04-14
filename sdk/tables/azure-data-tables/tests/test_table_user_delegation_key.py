# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy

from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential
from azure.core.exceptions import HttpResponseError
from azure.data.tables import (
    TableServiceClient,
    TableClient,
    TableSasPermissions,
    generate_table_sas,
    UserDelegationKey,
)

from _shared.testcase import TableTestCase
from preparers import tables_decorator

# ------------------------------------------------------------------------------


class TestTableUserDelegationKey(AzureRecordedTestCase, TableTestCase):

    @tables_decorator
    @recorded_by_proxy
    def test_get_user_delegation_key(self, tables_storage_account_name):
        """Test getting a user delegation key with valid start/expiry times."""
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(credential=self.get_token_credential(), endpoint=account_url)

        start_time = datetime.now(timezone.utc)
        expiry_time = start_time + timedelta(hours=1)

        user_delegation_key = tsc.get_user_delegation_key(
            key_start_time=start_time,
            key_expiry_time=expiry_time,
        )

        assert user_delegation_key is not None
        assert user_delegation_key.signed_oid is not None
        assert user_delegation_key.signed_tid is not None
        assert user_delegation_key.signed_start is not None
        assert user_delegation_key.signed_expiry is not None
        assert user_delegation_key.signed_service is not None
        assert user_delegation_key.signed_version is not None
        assert user_delegation_key.value is not None

    @tables_decorator
    @recorded_by_proxy
    def test_get_user_delegation_key_past_expiry(self, tables_storage_account_name):
        """Test that getting a user delegation key with an expiry in the past raises an error."""
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(credential=self.get_token_credential(), endpoint=account_url)

        start_time = datetime.now(timezone.utc) - timedelta(hours=2)
        expiry_time = datetime.now(timezone.utc) - timedelta(hours=1)

        with pytest.raises(HttpResponseError):
            tsc.get_user_delegation_key(
                key_start_time=start_time,
                key_expiry_time=expiry_time,
            )

    @tables_decorator
    @recorded_by_proxy
    def test_get_user_delegation_key_shared_key_auth(
        self, tables_storage_account_name, tables_primary_storage_account_key
    ):
        """Test that getting a user delegation key with SharedKey credential fails."""
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(account_url, credential=tables_primary_storage_account_key)

        start_time = datetime.now(timezone.utc)
        expiry_time = start_time + timedelta(hours=1)

        with pytest.raises(HttpResponseError):
            tsc.get_user_delegation_key(
                key_start_time=start_time,
                key_expiry_time=expiry_time,
            )

    def test_generate_user_delegation_sas(self):
        """Test generating a user delegation SAS token with correct query parameters."""
        udk = UserDelegationKey(
            signed_oid="00000000-0000-0000-0000-000000000001",
            signed_tid="00000000-0000-0000-0000-000000000002",
            signed_start="2025-01-01T00:00:00Z",
            signed_expiry="2025-01-02T00:00:00Z",
            signed_service="t",
            signed_version="2025-07-05",
            value="dGVzdGtleQ==",  # base64("testkey")
        )

        sas_token = generate_table_sas(
            credential=AzureNamedKeyCredential(name="fakeaccount", key="ZmFrZWtleQ=="),
            table_name="testtable",
            user_delegation_key=udk,
            permission=TableSasPermissions(read=True, add=True),
            expiry=datetime(2025, 1, 2, tzinfo=timezone.utc),
            start=datetime(2025, 1, 1, tzinfo=timezone.utc),
        )

        assert sas_token is not None
        params = parse_qs(sas_token)

        # Verify user delegation key parameters are present
        assert "skoid" in params
        assert params["skoid"][0] == "00000000-0000-0000-0000-000000000001"
        assert "sktid" in params
        assert params["sktid"][0] == "00000000-0000-0000-0000-000000000002"
        assert "skt" in params
        assert params["skt"][0] == "2025-01-01T00:00:00Z"
        assert "ske" in params
        assert params["ske"][0] == "2025-01-02T00:00:00Z"
        assert "sks" in params
        assert params["sks"][0] == "t"
        assert "skv" in params
        assert params["skv"][0] == "2025-07-05"

        # Verify standard SAS parameters
        assert "sig" in params
        assert "sp" in params
        assert "sv" in params
        assert "tn" in params
        assert params["tn"][0] == "testtable"

        # User delegation SAS should NOT have si (signed identifier)
        assert "si" not in params

    def test_generate_user_delegation_sas_with_account_name(self):
        """Test generating a user delegation SAS with explicit account_name parameter."""
        udk = UserDelegationKey(
            signed_oid="00000000-0000-0000-0000-000000000001",
            signed_tid="00000000-0000-0000-0000-000000000002",
            signed_start="2025-01-01T00:00:00Z",
            signed_expiry="2025-01-02T00:00:00Z",
            signed_service="t",
            signed_version="2025-07-05",
            value="dGVzdGtleQ==",
        )

        sas_token = generate_table_sas(
            credential=AzureNamedKeyCredential(name="fakeaccount", key="ZmFrZWtleQ=="),
            table_name="testtable",
            user_delegation_key=udk,
            account_name="myaccount",
            permission=TableSasPermissions(read=True),
            expiry=datetime(2025, 1, 2, tzinfo=timezone.utc),
        )

        assert sas_token is not None
        params = parse_qs(sas_token)
        assert "sig" in params
        assert "skoid" in params

    def test_generate_user_delegation_sas_with_delegated_user_tid(self):
        """Test generating a user delegation SAS with the optional delegated user TID."""
        udk = UserDelegationKey(
            signed_oid="00000000-0000-0000-0000-000000000001",
            signed_tid="00000000-0000-0000-0000-000000000002",
            signed_start="2025-01-01T00:00:00Z",
            signed_expiry="2025-01-02T00:00:00Z",
            signed_service="t",
            signed_version="2025-07-05",
            signed_delegated_user_tid="00000000-0000-0000-0000-000000000003",
            value="dGVzdGtleQ==",
        )

        sas_token = generate_table_sas(
            credential=AzureNamedKeyCredential(name="fakeaccount", key="ZmFrZWtleQ=="),
            table_name="testtable",
            user_delegation_key=udk,
            permission=TableSasPermissions(read=True),
            expiry=datetime(2025, 1, 2, tzinfo=timezone.utc),
        )

        params = parse_qs(sas_token)
        assert "skdutid" in params
        assert params["skdutid"][0] == "00000000-0000-0000-0000-000000000003"

    def test_generate_table_sas_backward_compatible(self):
        """Test that generate_table_sas still works with just AzureNamedKeyCredential (no user_delegation_key)."""
        fake_key = "a" * 30 + "b" * 30
        credential = AzureNamedKeyCredential(name="fakeaccount", key=fake_key)

        sas_token = generate_table_sas(
            credential=credential,
            table_name="testtable",
            permission=TableSasPermissions(read=True),
            expiry=datetime(2025, 1, 2, tzinfo=timezone.utc),
        )

        assert sas_token is not None
        params = parse_qs(sas_token)
        assert "sig" in params
        assert "sp" in params
        # Should NOT have user delegation key parameters
        assert "skoid" not in params
        assert "sktid" not in params

    @pytest.mark.skip(reason="User delegation SAS for Tables requires service-side support for sv=2025-07-05 string-to-sign format")
    @tables_decorator
    @recorded_by_proxy
    def test_user_delegation_sas_access_table(self, tables_storage_account_name):
        """End-to-end test: get key → generate SAS → use SAS to access table."""
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(credential=self.get_token_credential(), endpoint=account_url)

        # Create a test table
        table_name = self._get_table_reference()
        try:
            tsc.create_table(table_name)

            # Get user delegation key
            start_time = datetime.now(timezone.utc)
            expiry_time = start_time + timedelta(hours=1)
            user_delegation_key = tsc.get_user_delegation_key(
                key_start_time=start_time,
                key_expiry_time=expiry_time,
            )

            # Generate SAS token using user delegation key
            sas_token = generate_table_sas(
                credential=AzureNamedKeyCredential(
                    name=tables_storage_account_name, key="unused"
                ),
                table_name=table_name,
                user_delegation_key=user_delegation_key,
                account_name=tables_storage_account_name,
                permission=TableSasPermissions(read=True, add=True, update=True, delete=True),
                expiry=expiry_time,
                start=start_time,
            )

            # Use SAS token to access the table
            sas_client = TableClient(
                endpoint=account_url,
                table_name=table_name,
                credential=AzureSasCredential(sas_token),
            )

            # Insert an entity to verify the SAS token works
            entity = {
                "PartitionKey": "pk",
                "RowKey": "rk1",
                "Value": "test_value",
            }
            sas_client.upsert_entity(entity)

            # Query to verify
            queried = sas_client.get_entity("pk", "rk1")
            assert queried["Value"] == "test_value"

        finally:
            tsc.delete_table(table_name)
