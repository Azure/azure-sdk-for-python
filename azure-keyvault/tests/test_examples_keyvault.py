# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import time

from azure.keyvault.secrets._client import SecretClient
from azure.core.exceptions import ClientRequestError
from devtools_testutils import ResourceGroupPreparer
from keyvault_preparer import KeyVaultPreparer
from keyvault_testcase import KeyvaultTestCase

def create_vault_client():
    # [START create_vault_client
    from azure.keyvault.vault_client import VaultClient
    from azure.common.credentials import ServicePrincipalCredentials

    credentials = ServicePrincipalCredentials(
        client_id=client_id,
        secret=client_secret,
        tenant=tenant_id,
        resource="https://vault.azure.net"
    )

    # Create a new Vault client using Azure credentials
    vault_client = VaultClient(
        vault_url=vault_url, credentials=credentials)
    # [END create_vault_client]
    return vault_client

def create_secret_client():
    client_id = ''
    client_secret = ''
    tenant_id = ''

    # [START create_secret_client
    from azure.keyvault.secrets._client import SecretClient

    credentials = ServicePrincipalCredentials(
        client_id=client_id,
        secret=client_secret,
        tenant=tenant_id,
        resource='https://vault.azure.net'
    )

    # Create a new Secret client using Azure credentials
    secret_client = SecretClient(vault_url=vault_url, credentials=credentials)
    # [END create_secret_client]
    return secret_client

class TestExamplesKeyVault(KeyvaultTestCase):

    @ResourceGroupPreparer()
    @KeyVaultPreparer(enable_soft_delete=True)
    def test_example_secret_crud_operations(self, vault_client, **kwargs):
        secret_client = vault_client.secrets
        try:
            # [START set_secret]
            from dateutil import parser as date_parse

            expires = date_parse.parse('2050-02-02T08:00:00.000Z')

            # create a secret with optional arguments
            secret = secret_client.set_secret('secret-name', 'secret-value', enabled=True, expires=expires)
            
            print(secret.version)
            print(secret.created)
            print(secret.enabled)
            print(secret.expires)

            # [END set_secret]
        except ClientRequestError:
            pass

        try:
            # [START get_secret]
            secret_version = secret.version

            # get secret with version
            secret = secret_client.get_secret('secret-name', secret_version)

            # get secret with version as none, returns secret's latest version
            secret = secret_client.get_secret('secret-name', '')

            # gets a secret properties
            print(secret.id)
            print(secret.name)
            print(secret.version)
            print(secret.vault_url)
            # [END get_secret]
        except ClientRequestError:
            pass

        try:
            # [START update_secret_attributes]

            # update attributes of an existing secret using name and version

            content_type = 'text/plain'
            tags = {'foo': 'updated tag'}
            secret_version = secret.version
            updated_secret = secret_client.update_secret_attributes(
                'secret-name', secret_version,
                content_type=content_type,
                tags=tags)
                
            # should get a new version and updated value
            print(updated_secret.version)
            print(updated_secret.updated)
            print(updated_secret.content_type)
            print(updated_secret.tags)

            # [END update_secret_attributes]
        except ClientRequestError:
            pass

        try:
            # [START delete_secret]

            # delete a secret
            deleted_secret = secret_client.delete_secret('secret-name')

            print(deleted_secret.name)
            print(deleted_secret.deleted_date)

            # [END delete_secret]
        except ClientRequestError:
            pass

    @ResourceGroupPreparer()
    @KeyVaultPreparer(enable_soft_delete=True)
    def test_example_secret_list_operations(self, vault_client, **kwargs):
        secret_client = vault_client.secrets
        try:
            # [START list_secrets]

            # list secrets without max_page_size (default = 25)
            secrets = secret_client.list_secrets()

            # prints a list of secrets from the generator object
            print(list(secrets))

            # Note: list operation does not return values or versions of the secrets.

            # [END list_secrets]
        except ClientRequestError:
            pass

        try:
            # [START list_secret_versions]
            from azure.keyvault.vault_client import VaultClient

            # gets a list of all versions of a secret, with max_page_size
            secret_versions = secret_client.list_secret_versions('secret-name', max_page_size=26)

            # gets a list of all versions of a secret, without max_page_size
            secret_versions = secret_client.list_secret_versions('secret-name')

            # prints a list of versions of a secret from the generator object
            print(list(secret_versions))

            # Note: list operation does not return values of the secrets. 

            # [END list_secret_versions]
        except ClientRequestError:
            pass

        try:
            # [START list_deleted_secrets]

            # get a list of deleted secrets with max_page_size
            deleted_secrets = secret_client.list_deleted_secrets(max_page_size=26)

            # get a list of deleted secrets without max_page_size
            deleted_secrets = secret_client.list_deleted_secrets()

            # prints a list of deleted secrets from the generator object
            print(list(deleted_secrets))

            # Note: list operation does not return versions or values of the secrets. 

            # [END list_deleted_secrets]
        except ClientRequestError:
            pass

    @ResourceGroupPreparer()
    @KeyVaultPreparer(enable_soft_delete=True)
    def test_example_secrets_backup_restore(self, vault_client, **kwargs):
        secret_client = vault_client.secrets
        created_secret = secret_client.set_secret('secret-name', 'secret-value')
        secret_name = created_secret.name
        try:
            # [START backup_secret]
            # backup secret
            secret_backup = secret_client.backup_secret(secret_name)

            # returns the raw bytes of the backed up secret
            print(secret_backup)

            # [END backup_secret]
        except ClientRequestError:
            pass

        try:
            deleted_secret = secret_client.delete_secret(secret_name)
            if self.is_live:
                # wait a second to ensure the secret has been deleted
                time.sleep(1)

            # [START get_deleted_secret]
            # gets a deleted secret
            deleted_secret = secret_client.get_deleted_secret('secret-name')
            print(deleted_secret.name)

            # [END get_deleted_secret]
        except ClientRequestError:
            pass

        try:
            # [START restore_secret]

            # restores a backed up secret
            restored_secret = secret_client.restore_secret(secret_backup)
            print(restored_secret.id)
            print(restored_secret.value)
            print(restored_secret.version)

            # [END restore_secret]
        except ClientRequestError:
            pass

    @ResourceGroupPreparer()
    @KeyVaultPreparer(enable_soft_delete=True)
    def test_example_secrets_recover_purge(self, vault_client, **kwargs):
        secret_client = vault_client.secrets
        created_secret = secret_client.set_secret('secret-name', 'secret-value')
        secret_client.delete_secret(created_secret.name)
        if self.is_live:
            # wait a second to ensure the secret has been deleted
            time.sleep(1)

        try:
            # [START recover_deleted_secret]

            # recover deleted secret to the latest version
            recover_deleted_secret = secret_client.recover_deleted_secret('secret-name')
            print(recover_deleted_secret.id)
            print(recover_deleted_secret.name)

            # [END recover_deleted_secret]
        except ClientRequestError:
            pass

        try:
            if self.is_live:
                # wait a second to ensure the secret has been recovered
                time.sleep(1)
            secret_client.delete_secret(created_secret.name)
            if self.is_live:
                # wait a second to ensure the secret has been deleted
                time.sleep(1)
            # [START purge_deleted_secret]

            # purge deleted secret, performs permanent deletion of a secret
            secret_client.purge_deleted_secret('secret-name')

            # [END purge_deleted_secret]
        except ClientRequestError:
            pass
