# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. A managed HSM (https://learn.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli)
#
# 2. azure-keyvault-administration and azure-identity libraries (pip install these)
#
# 3. Set environment variable MANAGED_HSM_URL with the URL of your managed HSM and CA_CERTIFICATE with the proxy server's
#    certificate in DER format and base64 encoded.
#
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates Key Vault setting management operations for Managed HSM
#
# 1. Crate EKM connection (create_ekm_connection)
#
# 2. Get EKM connection (get_ekm_connection)
#
# 3. Get EKM certificate (get_ekm_certificate)
#
# 2. Check EKM connection (check_ekm_connection)
#
# 3. Update EKM connection (update_ekm_connection)
#
# 2. Delete EKM connection (delete_ekm_connection)
# ----------------------------------------------------------------------------------------------------------

# Instantiate an access control client that will be used to call the service.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
# [START create_a_settings_client]
import base64
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultEkmConnection
from azure.keyvault.administration.aio import KeyVaultEkmClient


async def run_sample():
    MANAGED_HSM_URL = os.environ["MANAGED_HSM_URL"]
    CA_CERTIFICATE = os.environ["CA_CERTIFICATE"]
    credential = DefaultAzureCredential()
    client = KeyVaultEkmClient(vault_url=MANAGED_HSM_URL, credential=credential)
    # [END create_a_settings_client]

    # First, let's create an EKM connection
    print("\n.. Create EKM connection")
    # [START create_ekm_connection]
    ekm_connection = KeyVaultEkmConnection(
        host="my-ekm-host",
        server_ca_certificates=[base64.b64encode(CA_CERTIFICATE.encode())],
        path_prefix="/ekm-path-prefix",
        server_subject_common_name="my-ekm-subject-common-name",
    )
    created_ekm_connection = await client.create_ekm_connection(ekm_connection=ekm_connection)
    print(f"EKM connection created with host: {created_ekm_connection.host}")
    # [END create_ekm_connection]

    # Let's get the EKM connection we just created
    print("\n.. Get EKM connection")
    # [START get_ekm_connection]
    retrieved_ekm_connection = await client.get_ekm_connection()
    print(f"Retrieved EKM connection with host: {retrieved_ekm_connection.host}")
    # [END get_ekm_connection]

    # Get the EKM certificate
    print("\n.. Get EKM certificate")
    # [START get_ekm_certificate]
    ekm_certificate = await client.get_ekm_certificate()
    print(f"EKM certificate retrieved")
    # [END get_ekm_certificate]

    # Check the EKM connection status
    print("\n.. Check EKM connection")
    # [START check_ekm_connection]
    connection_status = await client.check_ekm_connection()
    print(f"EKM connection status: {connection_status}")
    # [END check_ekm_connection]

    # Update the EKM connection
    print("\n.. Update EKM connection")
    # [START update_ekm_connection]
    updated_ekm_connection = KeyVaultEkmConnection(
        host="my-updated-ekm-host",
        server_ca_certificates=[base64.b64encode(CA_CERTIFICATE.encode())],
        path_prefix="/updated-ekm-path-prefix",
        server_subject_common_name="my-updated-ekm-subject-common-name",
    )
    result = await client.update_ekm_connection(ekm_connection=updated_ekm_connection)
    print(f"EKM connection updated with host: {result.host}")
    # [END update_ekm_connection]

    # Finally, let's delete the EKM connection
    print("\n.. Delete EKM connection")
    # [START delete_ekm_connection]
    await client.delete_ekm_connection()
    print("EKM connection deleted successfully")
    # [END delete_ekm_connection]

    await client.close()
    await credential.close()


if __name__ == "__main__":
    asyncio.run(run_sample())
