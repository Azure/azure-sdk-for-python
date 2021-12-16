# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import functools
from devtools_testutils import recorded_by_proxy
from azure.ai.metricsadvisor import MetricsAdvisorAdministrationClient
from azure.ai.metricsadvisor.models import (
    DatasourceSqlConnectionString,
    DatasourceDataLakeGen2SharedKey,
    DatasourceServicePrincipal,
    DatasourceServicePrincipalInKeyVault
)
from base_testcase import TestMetricsAdvisorClientBase, MetricsAdvisorClientPreparer, CREDENTIALS, ids
MetricsAdvisorPreparer = functools.partial(MetricsAdvisorClientPreparer, MetricsAdvisorAdministrationClient, aad=False)


class TestMetricsAdvisorAdministrationClient(TestMetricsAdvisorClientBase):

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_create_datasource_sql_connection_string(self, client, variables):
        credential_name = self.create_random_name("testsqlcredential")
        if self.is_live:
            variables["credential_name"] = credential_name
        try:
            credential = client.create_datasource_credential(
                datasource_credential=DatasourceSqlConnectionString(
                    name=variables["credential_name"],
                    connection_string=self.sql_server_connection_string,
                    description="my credential",
                )
            )
            if self.is_live:
                variables["credential_id"] = credential.id
            assert credential.id is not None
            assert credential.name == variables["credential_name"]
            assert credential.credential_type == 'AzureSQLConnectionString'

        finally:
            self.clean_up(client.delete_datasource_credential, variables, key="credential_id")
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_datasource_datalake_gen2_shared_key(self, client, variables):
        credential_name = self.create_random_name("testdatalakecredential")
        if self.is_live:
            variables["credential_name"] = credential_name
        try:
            credential = client.create_datasource_credential(
                datasource_credential=DatasourceDataLakeGen2SharedKey(
                    name=variables["credential_name"],
                    account_key="azure_datalake_account_key",
                    description="my credential",
                )
            )
            if self.is_live:
                variables["credential_id"] = credential.id
            assert credential.id is not None
            assert credential.name == variables["credential_name"]
            assert credential.credential_type == 'DataLakeGen2SharedKey'

        finally:
            self.clean_up(client.delete_datasource_credential, variables, key="credential_id")
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_datasource_service_principal(self, client, variables):
        credential_name = self.create_random_name("testserviceprincipalcredential")
        if self.is_live:
            variables["credential_name"] = credential_name
        try:
            credential = client.create_datasource_credential(
                datasource_credential=DatasourceServicePrincipal(
                    name=variables["credential_name"],
                    client_id="client_id",
                    client_secret="client_secret",
                    tenant_id="tenant_id",
                    description="my credential",
                )
            )
            if self.is_live:
                variables["credential_id"] = credential.id
            assert credential.id is not None
            assert credential.name == variables["credential_name"]
            assert credential.credential_type == 'ServicePrincipal'
        finally:
            self.clean_up(client.delete_datasource_credential, variables, key="credential_id")
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_datasource_service_principal_in_kv(self, client, variables):
        credential_name = self.create_random_name("testserviceprincipalcredential")
        if self.is_live:
            variables["credential_name"] = credential_name
        try:
            credential = client.create_datasource_credential(
                datasource_credential=DatasourceServicePrincipalInKeyVault(
                    name=variables["credential_name"],
                    key_vault_endpoint="key_vault_endpoint",
                    key_vault_client_id="key_vault_client_id",
                    key_vault_client_secret="key_vault_client_secret",
                    service_principal_id_name_in_kv="service_principal_id_name_in_kv",
                    service_principal_secret_name_in_kv="service_principal_secret_name_in_kv",
                    tenant_id="tenant_id",
                    description="my credential",
                )
            )
            if self.is_live:
                variables["credential_id"] = credential.id
            assert credential.id is not None
            assert credential.name == variables["credential_name"]
            assert credential.credential_type == 'ServicePrincipalInKV'
        finally:
            self.clean_up(client.delete_datasource_credential, variables, key="credential_id")
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_list_datasource_credentials(self, client, variables):
        credential_name = self.create_random_name("testsqlcredential")
        if self.is_live:
            variables["credential_name"] = credential_name
        try:
            credential = client.create_datasource_credential(
                datasource_credential=DatasourceSqlConnectionString(
                    name=variables["credential_name"],
                    connection_string=self.sql_server_connection_string,
                    description="my credential",
                )
            )
            if self.is_live:
                variables["credential_id"] = credential.id
            credentials = client.list_datasource_credentials()
            assert len(list(credentials)) > 0
        finally:
            self.clean_up(client.delete_datasource_credential, variables, key="credential_id")
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_update_datasource_sql_connection_string(self, client, variables):
        credential_name = self.create_random_name("testsqlcredential")
        if self.is_live:
            variables["credential_name"] = credential_name
        try:
            credential = client.create_datasource_credential(
                datasource_credential=DatasourceSqlConnectionString(
                    name=variables["credential_name"],
                    connection_string=self.sql_server_connection_string,
                    description="my credential",
                )
            )
            if self.is_live:
                variables["credential_id"] = credential.id
            credential.connection_string = "update"
            credential.description = "update"
            credential_updated = client.update_datasource_credential(credential)
            assert credential_updated.description == "update"
        finally:
            self.clean_up(client.delete_datasource_credential, variables, key="credential_id")
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_update_datasource_datalake_gen2_shared_key(self, client, variables):
        credential_name = self.create_random_name("testdatalakecredential")
        if self.is_live:
            variables["credential_name"] = credential_name
        try:
            credential = client.create_datasource_credential(
                datasource_credential=DatasourceDataLakeGen2SharedKey(
                    name=variables["credential_name"],
                    account_key="azure_datalake_account_key",
                    description="my credential",
                )
            )
            if self.is_live:
                variables["credential_id"] = credential.id
            credential.account_key = "update"
            credential.description = "update"
            credential_updated = client.update_datasource_credential(credential)
            assert credential_updated.description == "update"
        finally:
            self.clean_up(client.delete_datasource_credential, variables, key="credential_id")
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_update_datasource_service_principal(self, client, variables):
        credential_name = self.create_random_name("testserviceprincipalcredential")
        if self.is_live:
            variables["credential_name"] = credential_name
        try:
            credential = client.create_datasource_credential(
                datasource_credential=DatasourceServicePrincipal(
                    name=variables["credential_name"],
                    client_id="client_id",
                    client_secret="client_secret",
                    tenant_id="tenant_id",
                    description="my credential",
                )
            )
            if self.is_live:
                variables["credential_id"] = credential.id
            credential.client_id = "update"
            credential.client_secret = "update"
            credential.tenant_id = "update"
            credential.description = "update"
            credential_updated = client.update_datasource_credential(credential)
            assert credential_updated.description == "update"
        finally:
            self.clean_up(client.delete_datasource_credential, variables, key="credential_id")
        return variables

    @pytest.mark.parametrize("credential", CREDENTIALS, ids=ids)
    @MetricsAdvisorPreparer()
    @recorded_by_proxy
    def test_update_datasource_service_principal_in_kv(self, client, variables):
        credential_name = self.create_random_name("testserviceprincipalcredential")
        if self.is_live:
            variables["credential_name"] = credential_name
        try:
            credential = client.create_datasource_credential(
                datasource_credential=DatasourceServicePrincipalInKeyVault(
                    name=variables["credential_name"],
                    key_vault_endpoint="key_vault_endpoint",
                    key_vault_client_id="key_vault_client_id",
                    key_vault_client_secret="key_vault_client_secret",
                    service_principal_id_name_in_kv="service_principal_id_name_in_kv",
                    service_principal_secret_name_in_kv="service_principal_secret_name_in_kv",
                    tenant_id="tenant_id",
                    description="my credential",
                )
            )
            if self.is_live:
                variables["credential_id"] = credential.id
            credential.key_vault_endpoint = "update"
            credential.key_vault_client_id = "update"
            credential.key_vault_client_secret = "update"
            credential.service_principal_id_name_in_kv = "update"
            credential.service_principal_secret_name_in_kv = "update"
            credential.tenant_id = "update"
            credential.description = "update"
            credential_updated = client.update_datasource_credential(credential)
            assert credential_updated.description == "update"
        finally:
            self.clean_up(client.delete_datasource_credential, variables, key="credential_id")
        return variables
