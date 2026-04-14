# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from datetime import datetime, timedelta, timezone

from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy, set_custom_default_matcher

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


class TestTableUserDelegationKey(AzureRecordedTestCase, TableTestCase):

    @tables_decorator
    @recorded_by_proxy
    def test_get_user_delegation_key(self, tables_storage_account_name):
        """Test getting a user delegation key with valid start/expiry times."""
        set_custom_default_matcher(compare_bodies=False)
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(
            credential=self.get_token_credential(), endpoint=account_url
        )

        start_time = datetime.now(timezone.utc)
        expiry_time = datetime.now(timezone.utc) + timedelta(hours=1)

        user_delegation_key = tsc.get_user_delegation_key(
            key_start_time=start_time,
            key_expiry_time=expiry_time,
        )

        # Verify all attributes exist on the returned key
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
    def test_user_delegation_sas_table_operations(self, tables_storage_account_name):
        """Test end-to-end: get delegation key, generate SAS, use SAS to access table."""
        set_custom_default_matcher(
            compare_bodies=False,
            ignored_query_parameters="skt,ske",
        )
        account_url = self.account_url(tables_storage_account_name, "table")
        tsc = TableServiceClient(
            credential=self.get_token_credential(), endpoint=account_url
        )

        start_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        expiry_time = datetime.now(timezone.utc) + timedelta(hours=1)

        # Step 1: Get user delegation key
        user_delegation_key = tsc.get_user_delegation_key(
            key_start_time=start_time,
            key_expiry_time=expiry_time,
        )

        # Step 2: Create a table for testing
        table_name = self._get_table_reference()
        tsc.create_table(table_name)

        try:
            # Step 3: Generate user delegation SAS
            sas_token = generate_table_sas(
                table_name=table_name,
                user_delegation_key=user_delegation_key,
                account_name=tables_storage_account_name,
                permission=TableSasPermissions(read=True, add=True, update=True, delete=True),
                expiry=expiry_time,
                start=start_time,
            )

            assert sas_token is not None
            assert "sig=" in sas_token
            assert "skoid=" in sas_token  # User delegation key OID
            assert "sktid=" in sas_token  # User delegation key TID

            # Step 4: Use SAS to access the table
            sas_client = TableClient(
                endpoint=account_url,
                table_name=table_name,
                credential=AzureSasCredential(sas_token),
            )

            # Insert an entity using SAS
            entity = {
                "PartitionKey": "pk",
                "RowKey": "rk1",
                "Value": "test_value",
            }
            sas_client.create_entity(entity)

            # Query the entity using SAS
            retrieved = sas_client.get_entity("pk", "rk1")
            assert retrieved["Value"] == "test_value"

        finally:
            tsc.delete_table(table_name)


class TestTableUserDelegationKeyUnitTests(TableTestCase):

    def test_generate_table_sas_with_user_delegation_key(self):
        """Unit test: verify generate_table_sas works with a user delegation key."""
        udk = UserDelegationKey(
            signed_oid="test-oid",
            signed_tid="test-tid",
            signed_start="2025-01-01T00:00:00Z",
            signed_expiry="2025-01-01T01:00:00Z",
            signed_service="t",
            signed_version="2025-07-05",
            value="dGVzdGtleQ==",  # base64 of "testkey"
        )

        sas_token = generate_table_sas(
            table_name="testtable",
            user_delegation_key=udk,
            account_name="testaccount",
            permission=TableSasPermissions(read=True),
            expiry=datetime(2025, 1, 1, 2, 0, 0),
            start=datetime(2025, 1, 1, 0, 0, 0),
        )

        assert sas_token is not None
        assert "sig=" in sas_token
        assert "skoid=test-oid" in sas_token
        assert "sktid=test-tid" in sas_token
        assert "skt=" in sas_token
        assert "ske=" in sas_token
        assert "sks=t" in sas_token
        assert "skv=2025-07-05" in sas_token
        assert "tn=testtable" in sas_token

    def test_generate_table_sas_requires_account_name_with_udk(self):
        """Unit test: ensure account_name is required when using user delegation key."""
        udk = UserDelegationKey(
            signed_oid="test-oid",
            signed_tid="test-tid",
            signed_start="2025-01-01T00:00:00Z",
            signed_expiry="2025-01-01T01:00:00Z",
            signed_service="t",
            signed_version="2025-07-05",
            value="dGVzdGtleQ==",
        )

        with pytest.raises(ValueError):
            generate_table_sas(
                table_name="testtable",
                user_delegation_key=udk,
                # account_name intentionally omitted
                permission=TableSasPermissions(read=True),
                expiry=datetime(2025, 1, 1, 2, 0, 0),
            )

    def test_generate_table_sas_backward_compatible(self):
        """Unit test: ensure generate_table_sas still works with credential (backward compat)."""
        credential = AzureNamedKeyCredential(name="testaccount", key="dGVzdGtleQ==")

        sas_token = generate_table_sas(
            credential,
            "testtable",
            permission=TableSasPermissions(read=True),
            expiry=datetime(2025, 1, 1, 2, 0, 0),
        )

        assert sas_token is not None
        assert "sig=" in sas_token
        assert "tn=testtable" in sas_token
        # Should NOT have user delegation key fields
        assert "skoid=" not in sas_token

    def test_generate_table_sas_with_partition_and_row_key_ranges(self):
        """Unit test: verify partition/row key ranges work with user delegation SAS."""
        udk = UserDelegationKey(
            signed_oid="test-oid",
            signed_tid="test-tid",
            signed_start="2025-01-01T00:00:00Z",
            signed_expiry="2025-01-01T01:00:00Z",
            signed_service="t",
            signed_version="2025-07-05",
            value="dGVzdGtleQ==",
        )

        sas_token = generate_table_sas(
            table_name="testtable",
            user_delegation_key=udk,
            account_name="testaccount",
            permission=TableSasPermissions(read=True),
            expiry=datetime(2025, 1, 1, 2, 0, 0),
            start_pk="pk1",
            start_rk="rk1",
            end_pk="pk2",
            end_rk="rk2",
        )

        assert "spk=pk1" in sas_token
        assert "srk=rk1" in sas_token
        assert "epk=pk2" in sas_token
        assert "erk=rk2" in sas_token
