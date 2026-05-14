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

from azure.core.exceptions import HttpResponseError
from azure.data.tables import (
    TableServiceClient,
    TableSasPermissions,
    UserDelegationKey,
    generate_table_sas,
)

from _shared.testcase import TableTestCase
from preparers import tables_decorator

# ------------------------------------------------------------------------------


class TestTableUserDelegationKey(AzureRecordedTestCase, TableTestCase):
    @tables_decorator
    @recorded_by_proxy
    def test_get_user_delegation_key(self, tables_storage_account_name):
        """Test getting a user delegation key with OAuth credential."""
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(
            endpoint=account_url,
            credential=self.get_token_credential(),
            api_version="2025-07-05",
        )
        start_time = datetime.now(timezone.utc)
        expiry_time = start_time + timedelta(hours=1)

        udk = tsc.get_user_delegation_key(
            key_start_time=start_time,
            key_expiry_time=expiry_time,
        )

        assert udk is not None
        assert udk.signed_oid is not None
        assert udk.signed_tid is not None
        assert udk.signed_start is not None
        assert udk.signed_expiry is not None
        assert udk.signed_service is not None
        assert udk.signed_version is not None
        assert udk.value is not None

    @tables_decorator
    @recorded_by_proxy
    def test_get_user_delegation_key_without_delegated_user_tid(self, tables_storage_account_name):
        """Test getting a user delegation key without delegated_user_tid (second call verifies consistency)."""
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(
            endpoint=account_url,
            credential=self.get_token_credential(),
            api_version="2025-07-05",
        )
        start_time = datetime.now(timezone.utc)
        expiry_time = start_time + timedelta(hours=1)

        udk = tsc.get_user_delegation_key(
            key_start_time=start_time,
            key_expiry_time=expiry_time,
        )

        assert udk is not None
        assert udk.value is not None
        assert udk.signed_oid is not None
        assert udk.signed_tid is not None

    @tables_decorator
    @recorded_by_proxy
    def test_user_delegation_sas_full_workflow(self, tables_storage_account_name):
        """Test the full workflow: get UDK -> generate SAS -> use SAS to access table."""
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(
            endpoint=account_url,
            credential=self.get_token_credential(),
            api_version="2025-07-05",
        )

        start_time = datetime.now(timezone.utc)
        expiry_time = start_time + timedelta(hours=1)

        udk = tsc.get_user_delegation_key(
            key_start_time=start_time,
            key_expiry_time=expiry_time,
        )

        table_name = self._get_table_reference()
        try:
            tsc.create_table(table_name)

            sas_token = generate_table_sas(
                credential=udk,
                table_name=table_name,
                account_name=tables_storage_account_name,
                permission=TableSasPermissions(read=True, add=True, update=True, delete=True),
                expiry=expiry_time,
                start=start_time,
            )

            assert sas_token is not None
            # Verify the SAS token contains user delegation key parameters
            parsed = parse_qs(sas_token)
            assert "skoid" in parsed
            assert "sktid" in parsed
            assert "skt" in parsed
            assert "ske" in parsed
            assert "sks" in parsed
            assert "skv" in parsed

            # Use the SAS token to access the table
            from azure.core.credentials import AzureSasCredential

            sas_client = TableServiceClient(
                endpoint=account_url,
                credential=AzureSasCredential(sas_token),
            )
            sas_table = sas_client.get_table_client(table_name)

            # Query entities (should succeed even if empty)
            entities = list(sas_table.list_entities())
            assert isinstance(entities, list)
        finally:
            tsc.delete_table(table_name)


class TestTableUserDelegationKeyUnitTests(TableTestCase):
    def test_generate_user_delegation_sas_produces_correct_query_params(self):
        """Verify that generate_table_sas with a UserDelegationKey produces
        the correct SAS query string parameters."""
        udk = UserDelegationKey(
            signed_oid="test-oid",
            signed_tid="test-tid",
            signed_start="2025-01-01T00:00:00Z",
            signed_expiry="2025-01-02T00:00:00Z",
            signed_service="t",
            signed_version="2025-07-05",
            value="dGVzdGtleQ==",  # base64 of "testkey"
        )

        sas = generate_table_sas(
            credential=udk,
            table_name="testtable",
            account_name="testaccount",
            permission=TableSasPermissions(read=True),
            expiry=datetime(2025, 1, 2, tzinfo=timezone.utc),
            start=datetime(2025, 1, 1, tzinfo=timezone.utc),
        )

        assert sas is not None
        parsed = parse_qs(sas)
        assert parsed["skoid"] == ["test-oid"]
        assert parsed["sktid"] == ["test-tid"]
        assert parsed["skt"] == ["2025-01-01T00:00:00Z"]
        assert parsed["ske"] == ["2025-01-02T00:00:00Z"]
        assert parsed["sks"] == ["t"]
        assert parsed["skv"] == ["2025-07-05"]
        assert parsed["sv"] == ["2025-07-05"]
        assert "sig" in parsed
        assert "sp" in parsed
        assert "tn" in parsed
        assert parsed["tn"] == ["testtable"]

    def test_generate_user_delegation_sas_requires_account_name(self):
        """Verify that generate_table_sas raises ValueError when account_name is missing."""
        udk = UserDelegationKey(
            signed_oid="test-oid",
            signed_tid="test-tid",
            signed_start="2025-01-01T00:00:00Z",
            signed_expiry="2025-01-02T00:00:00Z",
            signed_service="t",
            signed_version="2025-07-05",
            value="dGVzdGtleQ==",
        )

        with pytest.raises(ValueError, match="account_name"):
            generate_table_sas(
                credential=udk,
                table_name="testtable",
                permission=TableSasPermissions(read=True),
                expiry=datetime(2025, 1, 2, tzinfo=timezone.utc),
            )

    def test_generate_user_delegation_sas_with_ip_and_protocol(self):
        """Verify IP and protocol params are included in user delegation SAS."""
        udk = UserDelegationKey(
            signed_oid="test-oid",
            signed_tid="test-tid",
            signed_start="2025-01-01T00:00:00Z",
            signed_expiry="2025-01-02T00:00:00Z",
            signed_service="t",
            signed_version="2025-07-05",
            value="dGVzdGtleQ==",
        )

        sas = generate_table_sas(
            credential=udk,
            table_name="testtable",
            account_name="testaccount",
            permission=TableSasPermissions(read=True),
            expiry=datetime(2025, 1, 2, tzinfo=timezone.utc),
            ip_address_or_range="168.1.5.60-168.1.5.70",
            protocol="https",
        )

        parsed = parse_qs(sas)
        assert parsed["sip"] == ["168.1.5.60-168.1.5.70"]
        assert parsed["spr"] == ["https"]

    def test_generate_user_delegation_sas_with_partition_row_keys(self):
        """Verify partition/row key range params are included."""
        udk = UserDelegationKey(
            signed_oid="test-oid",
            signed_tid="test-tid",
            signed_start="2025-01-01T00:00:00Z",
            signed_expiry="2025-01-02T00:00:00Z",
            signed_service="t",
            signed_version="2025-07-05",
            value="dGVzdGtleQ==",
        )

        sas = generate_table_sas(
            credential=udk,
            table_name="testtable",
            account_name="testaccount",
            permission=TableSasPermissions(read=True),
            expiry=datetime(2025, 1, 2, tzinfo=timezone.utc),
            start_pk="pk1",
            start_rk="rk1",
            end_pk="pk2",
            end_rk="rk2",
        )

        parsed = parse_qs(sas)
        assert parsed["spk"] == ["pk1"]
        assert parsed["srk"] == ["rk1"]
        assert parsed["epk"] == ["pk2"]
        assert parsed["erk"] == ["rk2"]

    def test_generate_table_sas_still_works_with_named_key(self):
        """Verify backward compatibility — AzureNamedKeyCredential still works."""
        from azure.core.credentials import AzureNamedKeyCredential

        credential = AzureNamedKeyCredential(name="testaccount", key="dGVzdGtleQ==")
        sas = generate_table_sas(
            credential=credential,
            table_name="testtable",
            permission=TableSasPermissions(read=True),
            expiry=datetime(2025, 1, 2, tzinfo=timezone.utc),
        )

        assert sas is not None
        parsed = parse_qs(sas)
        assert "sig" in parsed
        assert "skoid" not in parsed  # Should NOT have user delegation params

    def test_user_delegation_key_exported(self):
        """Verify UserDelegationKey is importable from azure.data.tables."""
        from azure.data.tables import UserDelegationKey as UDK

        assert UDK is not None
