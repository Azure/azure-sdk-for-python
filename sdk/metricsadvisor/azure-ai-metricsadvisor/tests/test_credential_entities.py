# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest

from azure.ai.metricsadvisor.models import (
    SQLConnectionStringCredentialEntity,
    DataLakeGen2SharedKeyCredentialEntity,
    ServicePrincipalCredentialEntity,
    ServicePrincipalInKVCredentialEntity
)
from base_testcase import TestMetricsAdvisorAdministrationClientBase


class TestMetricsAdvisorAdministrationClient(TestMetricsAdvisorAdministrationClientBase):

    def test_create_sql_connection_string_credential_entity(self):
        credential_entity_name = self.create_random_name("testsqlcredential")
        try:
            credential_entity = self.admin_client.create_credential_entity(
                credential_entity=SQLConnectionStringCredentialEntity(
                    name=credential_entity_name,
                    connection_string=self.sql_server_connection_string,
                    description="my credential entity",
                )
            )
            self.assertIsNotNone(credential_entity.id)
            self.assertEqual(credential_entity.name, credential_entity_name)
            self.assertEqual(credential_entity.credential_entity_type, 'AzureSQLConnectionString')
        finally:
            self.admin_client.delete_credential_entity(credential_entity.id)

    def test_datalake_gen2_shared_key_credential_entity(self):
        credential_entity_name = self.create_random_name("testdatalakecredential")
        try:
            credential_entity = self.admin_client.create_credential_entity(
                credential_entity=DataLakeGen2SharedKeyCredentialEntity(
                    name=credential_entity_name,
                    account_key=self.azure_datalake_account_key,
                    description="my credential entity",
                )
            )
            self.assertIsNotNone(credential_entity.id)
            self.assertEqual(credential_entity.name, credential_entity_name)
            self.assertEqual(credential_entity.credential_entity_type, 'DataLakeGen2SharedKey')
        finally:
            self.admin_client.delete_credential_entity(credential_entity.id)

    def test_service_principal_credential_entity(self):
        credential_entity_name = self.create_random_name("testserviceprincipalcredential")
        try:
            credential_entity = self.admin_client.create_credential_entity(
                credential_entity=ServicePrincipalCredentialEntity(
                    name=credential_entity_name,
                    client_id="client_id",
                    client_secret="client_secret",
                    tenant_id="tenant_id",
                    description="my credential entity",
                )
            )
            self.assertIsNotNone(credential_entity.id)
            self.assertEqual(credential_entity.name, credential_entity_name)
            self.assertEqual(credential_entity.credential_entity_type, 'ServicePrincipal')
        finally:
            self.admin_client.delete_credential_entity(credential_entity.id)

    def test_service_principal_in_kv_credential_entity(self):
        credential_entity_name = self.create_random_name("testserviceprincipalcredential")
        try:
            credential_entity = self.admin_client.create_credential_entity(
                credential_entity=ServicePrincipalInKVCredentialEntity(
                    name=credential_entity_name,
                    key_vault_endpoint="key_vault_endpoint",
                    key_vault_client_id="key_vault_client_id",
                    key_vault_client_secret="key_vault_client_secret",
                    service_principal_id_name_in_kv="service_principal_id_name_in_kv",
                    service_principal_secret_name_in_kv="service_principal_secret_name_in_kv",
                    tenant_id="tenant_id",
                    description="my credential entity",
                )
            )
            self.assertIsNotNone(credential_entity.id)
            self.assertEqual(credential_entity.name, credential_entity_name)
            self.assertEqual(credential_entity.credential_entity_type, 'ServicePrincipalInKV')
        finally:
            self.admin_client.delete_credential_entity(credential_entity.id)

    def test_list_credential_entities(self):
        credential_entity_name = self.create_random_name("testsqlcredential")
        try:
            credential_entity = self.admin_client.create_credential_entity(
                credential_entity=SQLConnectionStringCredentialEntity(
                    name=credential_entity_name,
                    connection_string=self.sql_server_connection_string,
                    description="my credential entity",
                )
            )
            credential_entities = self.admin_client.list_credential_entities()
            assert len(list(credential_entities)) > 0
        finally:
            self.admin_client.delete_credential_entity(credential_entity.id)

    def test_update_sql_connection_string_credential_entity(self):
        credential_entity_name = self.create_random_name("testsqlcredential")
        try:
            credential_entity = self.admin_client.create_credential_entity(
                credential_entity=SQLConnectionStringCredentialEntity(
                    name=credential_entity_name,
                    connection_string=self.sql_server_connection_string,
                    description="my credential entity",
                )
            )
            credential_entity.connection_string = "update"
            credential_entity.description = "update"
            credential_entity_updated = self.admin_client.update_credential_entity(credential_entity)
            self.assertEqual(credential_entity_updated.description, "update")
        finally:
            self.admin_client.delete_credential_entity(credential_entity.id)

    def test_update_datalake_gen2_shared_key_credential_entity(self):
        credential_entity_name = self.create_random_name("testdatalakecredential")
        try:
            credential_entity = self.admin_client.create_credential_entity(
                credential_entity=DataLakeGen2SharedKeyCredentialEntity(
                    name=credential_entity_name,
                    account_key=self.azure_datalake_account_key,
                    description="my credential entity",
                )
            )
            credential_entity.account_key = "update"
            credential_entity.description = "update"
            credential_entity_updated = self.admin_client.update_credential_entity(credential_entity)
            self.assertEqual(credential_entity_updated.description, "update")
        finally:
            self.admin_client.delete_credential_entity(credential_entity.id)

    def test_update_service_principal_credential_entity(self):
        credential_entity_name = self.create_random_name("testserviceprincipalcredential")
        try:
            credential_entity = self.admin_client.create_credential_entity(
                credential_entity=ServicePrincipalCredentialEntity(
                    name=credential_entity_name,
                    client_id="client_id",
                    client_secret="client_secret",
                    tenant_id="tenant_id",
                    description="my credential entity",
                )
            )
            credential_entity.client_id = "update"
            credential_entity.client_secret = "update"
            credential_entity.tenant_id = "update"
            credential_entity.description = "update"
            credential_entity_updated = self.admin_client.update_credential_entity(credential_entity)
            self.assertEqual(credential_entity_updated.description, "update")
        finally:
            self.admin_client.delete_credential_entity(credential_entity.id)

    def test_update_service_principal_in_kv_credential_entity(self):
        credential_entity_name = self.create_random_name("testserviceprincipalcredential")
        try:
            credential_entity = self.admin_client.create_credential_entity(
                credential_entity=ServicePrincipalInKVCredentialEntity(
                    name=credential_entity_name,
                    key_vault_endpoint="key_vault_endpoint",
                    key_vault_client_id="key_vault_client_id",
                    key_vault_client_secret="key_vault_client_secret",
                    service_principal_id_name_in_kv="service_principal_id_name_in_kv",
                    service_principal_secret_name_in_kv="service_principal_secret_name_in_kv",
                    tenant_id="tenant_id",
                    description="my credential entity",
                )
            )
            credential_entity.key_vault_endpoint = "update"
            credential_entity.key_vault_client_id = "update"
            credential_entity.key_vault_client_secret = "update"
            credential_entity.service_principal_id_name_in_kv = "update"
            credential_entity.service_principal_secret_name_in_kv = "update"
            credential_entity.tenant_id = "update"
            credential_entity.description = "update"
            credential_entity_updated = self.admin_client.update_credential_entity(credential_entity)
            self.assertEqual(credential_entity_updated.description, "update")
        finally:
            self.admin_client.delete_credential_entity(credential_entity.id)
