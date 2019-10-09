# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os
from azure.keyvault.certificates.aio import CertificateClient
from azure.identity.aio import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-certificates and azure-identity packages (pip install these)
#
# 3. Set Environment variables AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, vault_endpoint
#    (See https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/keyvault/azure-keyvault-keys#authenticate-the-client)
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic backup and restore operations on a vault(certificates) resource for Azure Key Vault
#
# 1. Create a certificate (create_certificate)
#
# 2. Backup a certificate (backup_certificate)
#
# 3. Delete a certificate (delete_certificate)
#
# 4. Purge a deleted certificate (purge_deleted_certificate)
#
# 5. Restore a certificate (restore_certificate)
# ----------------------------------------------------------------------------------------------------------


async def run_sample():
    # Instantiate a certificate client that will be used to call the service.
    # Notice that the client is using default Azure credentials.
    # To make default credentials work, ensure that environment variables 'AZURE_CLIENT_ID',
    # 'AZURE_CLIENT_SECRET' and 'AZURE_TENANT_ID' are set with the service principal credentials.
    vault_endpoint = os.environ["VAULT_ENDPOINT"]
    credential = DefaultAzureCredential()
    client = CertificateClient(vault_endpoint=vault_endpoint, credential=credential)
    try:

        print("\n.. Create Certificate")
        cert_name = "BackupRestoreCertificate"

        # Let's create a certificate for your key vault.
        # if the certificate already exists in the Key Vault, then a new version of the certificate is created.
        # An async poller is returned.
        create_certificate_poller = await client.create_certificate(name=cert_name)

        # Awaiting the poller will return a certificate if creation is successful, and will return the failed
        # CertificateOperation if not.
        await create_certificate_poller
        print("Certificate with name '{0}' created.".format(cert_name))

        # Backups are good to have, if in case certificates gets deleted accidentally.
        # For long term storage, it is ideal to write the backup to a file.
        print("\n.. Create a backup for an existing certificate")
        certificate_backup = await client.backup_certificate(name=cert_name)
        print("Backup created for certificate with name '{0}'.".format(cert_name))

        # The storage account certificate is no longer in use, so you can delete it.
        print("\n.. Delete the certificate")
        await client.delete_certificate(name=cert_name)
        print("Deleted Certificate with name '{0}'".format(cert_name))

        # In future, if the certificate is required again, we can use the backup value to restore it in the Key Vault.
        print("\n.. Restore the certificate using the backed up certificate bytes")
        certificate = await client.restore_certificate(certificate_backup)
        print("Restored Certificate with name '{0}'".format(certificate.name))

    except HttpResponseError as e:
        print("\nrun_sample has caught an error. {0}".format(e.message))

    finally:
        print("\nrun_sample done")


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(run_sample())
        loop.close()

    except Exception as e:
        print("Top level Error: {0}".format(str(e)))
