# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
from devtools_testutils import AzureTestCase

from azure.ai.metricsadvisor.models import (
    DatasourceSqlConnectionString,
    DatasourceDataLakeGen2SharedKey,
    DatasourceServicePrincipal,
    DatasourceServicePrincipalInKeyVault
)
from base_testcase_async import TestMetricsAdvisorAdministrationClientBaseAsync


class TestMetricsAdvisorAdministrationClient(TestMetricsAdvisorAdministrationClientBaseAsync):

    @AzureTestCase.await_prepared_test
    async def test_create_datasource_sql_connection_string(self):
        credential_name = self.create_random_name("testsqlcredential")
        async with self.admin_client:
            try:
                credential = await self.admin_client.create_datasource_credential(
                    datasource_credential=DatasourceSqlConnectionString(
                        name=credential_name,
                        connection_string=self.sql_server_connection_string,
                        description="my credential",
                    )
                )
                self.assertIsNotNone(credential.id)
                self.assertEqual(credential.name, credential_name)
                self.assertEqual(credential.credential_type, 'AzureSQLConnectionString')
            finally:
                await self.admin_client.delete_datasource_credential(credential.id)

    @AzureTestCase.await_prepared_test
    async def test_datasource_datalake_gen2_shared_key(self):
        credential_name = self.create_random_name("testdatalakecredential")
        async with self.admin_client:
            try:
                credential = await self.admin_client.create_datasource_credential(
                    datasource_credential=DatasourceDataLakeGen2SharedKey(
                        name=credential_name,
                        account_key=self.azure_datalake_account_key,
                        description="my credential",
                    )
                )
                self.assertIsNotNone(credential.id)
                self.assertEqual(credential.name, credential_name)
                self.assertEqual(credential.credential_type, 'DataLakeGen2SharedKey')
            finally:
                await self.admin_client.delete_datasource_credential(credential.id)

    @AzureTestCase.await_prepared_test
    async def test_datasource_service_principal(self):
        credential_name = self.create_random_name("testserviceprincipalcredential")
        async with self.admin_client:
            try:
                credential = await self.admin_client.create_datasource_credential(
                    datasource_credential=DatasourceServicePrincipal(
                        name=credential_name,
                        client_id="client_id",
                        client_secret="client_secret",
                        tenant_id="tenant_id",
                        description="my credential",
                    )
                )
                self.assertIsNotNone(credential.id)
                self.assertEqual(credential.name, credential_name)
                self.assertEqual(credential.credential_type, 'ServicePrincipal')
            finally:
                await self.admin_client.delete_datasource_credential(credential.id)

    @AzureTestCase.await_prepared_test
    async def test_datasource_service_principal_in_kv(self):
        credential_name = self.create_random_name("testserviceprincipalcredential")
        async with self.admin_client:
            try:
                credential = await self.admin_client.create_datasource_credential(
                    datasource_credential=DatasourceServicePrincipalInKeyVault(
                        name=credential_name,
                        key_vault_endpoint="key_vault_endpoint",
                        key_vault_client_id="key_vault_client_id",
                        key_vault_client_secret="key_vault_client_secret",
                        service_principal_id_name_in_kv="service_principal_id_name_in_kv",
                        service_principal_secret_name_in_kv="service_principal_secret_name_in_kv",
                        tenant_id="tenant_id",
                        description="my credential",
                    )
                )
                self.assertIsNotNone(credential.id)
                self.assertEqual(credential.name, credential_name)
                self.assertEqual(credential.credential_type, 'ServicePrincipalInKV')
            finally:
                await self.admin_client.delete_datasource_credential(credential.id)

    @AzureTestCase.await_prepared_test
    async def test_list_datasource_credentials(self):
        credential_name = self.create_random_name("testsqlcredential")
        async with self.admin_client:
            try:
                credential = await self.admin_client.create_datasource_credential(
                    datasource_credential=DatasourceSqlConnectionString(
                        name=credential_name,
                        connection_string=self.sql_server_connection_string,
                        description="my credential",
                    )
                )
                credentials = self.admin_client.list_datasource_credentials()
                credentials_list = []
                async for credential in credentials:
                    credentials_list.append(credential)
                assert len(credentials_list) > 0
            finally:
                await self.admin_client.delete_datasource_credential(credential.id)

    @AzureTestCase.await_prepared_test
    async def test_update_datasource_sql_connection_string(self):
        credential_name = self.create_random_name("testsqlcredential")
        async with self.admin_client:
            try:
                credential = await self.admin_client.create_datasource_credential(
                    datasource_credential=DatasourceSqlConnectionString(
                        name=credential_name,
                        connection_string=self.sql_server_connection_string,
                        description="my credential",
                    )
                )
                credential.connection_string = "update"
                credential.description = "update"
                credential_updated = await self.admin_client.update_datasource_credential(credential)
                self.assertEqual(credential_updated.description, "update")
            finally:
                await self.admin_client.delete_datasource_credential(credential.id)

    @AzureTestCase.await_prepared_test
    async def test_update_datasource_datalake_gen2_shared_key(self):
        credential_name = self.create_random_name("testdatalakecredential")
        async with self.admin_client:
            try:
                credential = await self.admin_client.create_datasource_credential(
                    datasource_credential=DatasourceDataLakeGen2SharedKey(
                        name=credential_name,
                        account_key=self.azure_datalake_account_key,
                        description="my credential",
                    )
                )
                credential.account_key = "update"
                credential.description = "update"
                credential_updated = await self.admin_client.update_datasource_credential(credential)
                self.assertEqual(credential_updated.description, "update")
            finally:
                await self.admin_client.delete_datasource_credential(credential.id)

    @AzureTestCase.await_prepared_test
    async def test_update_datasource_service_principal(self):
        credential_name = self.create_random_name("testserviceprincipalcredential")
        async with self.admin_client:
            try:
                credential = await self.admin_client.create_datasource_credential(
                    datasource_credential=DatasourceServicePrincipal(
                        name=credential_name,
                        client_id="client_id",
                        client_secret="client_secret",
                        tenant_id="tenant_id",
                        description="my credential",
                    )
                )
                credential.client_id = "update"
                credential.client_secret = "update"
                credential.tenant_id = "update"
                credential.description = "update"
                credential_updated = await self.admin_client.update_datasource_credential(credential)
                self.assertEqual(credential_updated.description, "update")
            finally:
                await self.admin_client.delete_datasource_credential(credential.id)

    @AzureTestCase.await_prepared_test
    async def test_update_datasource_service_principal_in_kv(self):
        credential_name = self.create_random_name("testserviceprincipalcredential")
        async with self.admin_client:
            try:
                credential = await self.admin_client.create_datasource_credential(
                    datasource_credential=DatasourceServicePrincipalInKeyVault(
                        name=credential_name,
                        key_vault_endpoint="key_vault_endpoint",
                        key_vault_client_id="key_vault_client_id",
                        key_vault_client_secret="key_vault_client_secret",
                        service_principal_id_name_in_kv="service_principal_id_name_in_kv",
                        service_principal_secret_name_in_kv="service_principal_secret_name_in_kv",
                        tenant_id="tenant_id",
                        description="my credential",
                    )
                )
                credential.key_vault_endpoint = "update"
                credential.key_vault_client_id = "update"
                credential.key_vault_client_secret = "update"
                credential.service_principal_id_name_in_kv = "update"
                credential.service_principal_secret_name_in_kv = "update"
                credential.tenant_id = "update"
                credential.description = "update"
                credential_updated = await self.admin_client.update_datasource_credential(credential)
                self.assertEqual(credential_updated.description, "update")
            finally:
                await self.admin_client.delete_datasource_credential(credential.id)
