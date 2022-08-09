# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os
from azure.keyvault.certificates.aio import CertificateClient
from azure.keyvault.certificates import CertificatePolicy
from azure.identity.aio import DefaultAzureCredential

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault (https://docs.microsoft.com/en-us/azure/key-vault/quick-create-cli)
#
# 2. azure-keyvault-certificates and azure-identity packages (pip install these)
#
# 3. Set up your environment to use azure-identity's DefaultAzureCredential. To authenticate a service principal with
#    environment variables, set AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_TENANT_ID
#    (See https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/keyvault/azure-keyvault-certificates#authenticate-the-client)
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
# 4. Purge a certificate (purge_deleted_certificate)
#
# 5. Restore a certificate (restore_certificate_backup)
# ----------------------------------------------------------------------------------------------------------


async def run_sample():
    # Instantiate a backup client that will be used to call the service.
    # Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
    vault_url = os.environ["VAULT_URL"]
    credential = DefaultAzureCredential()
    client = CertificateClient(vault_url=vault_url, credential=credential)

    print("\n.. Create Certificate")
    cert_name = "BackupRestoreCertificateAsync"

    # Let's create a certificate for your key vault.
    # if the certificate already exists in the Key Vault, then a new version of the certificate is created.
    # Awaiting the call returns a KeyVaultCertificate if creation is successful, and a CertificateOperation if not.
    certificate = await client.create_certificate(
        certificate_name=cert_name, policy=CertificatePolicy.get_default()
    )

    print("Certificate with name '{0}' created.".format(certificate.name))

    # Backups are good to have, if in case certificates gets deleted accidentally.
    # For long term storage, it is ideal to write the backup to a file.
    print("\n.. Create a backup for an existing certificate")
    certificate_backup = await client.backup_certificate(cert_name)
    print("Backup created for certificate with name '{0}'.".format(cert_name))

    # The storage account certificate is no longer in use, so you can delete it.
    print("\n.. Delete the certificate")
    await client.delete_certificate(cert_name)
    print("Deleted certificate with name '{0}'".format(cert_name))

    # Purge the deleted certificate.
    # The purge will take some time, so wait before restoring the backup to avoid a conflict.
    print("\n.. Purge the certificate")
    await client.purge_deleted_certificate(cert_name)
    await asyncio.sleep(60)
    print("Purged certificate with name '{0}'".format(cert_name))

    # In the future, if the certificate is required again, we can use the backup value to restore it in the Key Vault.
    print("\n.. Restore the certificate using the backed up certificate bytes")
    certificate = await client.restore_certificate_backup(certificate_backup)
    print("Restored certificate with name '{0}'".format(certificate.name))

    print("\nrun_sample done")
    await credential.close()
    await client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_sample())
    loop.close()
