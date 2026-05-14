# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import base64
import asyncio

from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultEkmConnection
from azure.keyvault.administration.aio import KeyVaultEkmClient

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. A managed HSM (https://learn.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli)
#
# 2. azure-keyvault-administration and azure-identity libraries (pip install these)
#
# 3. Set environment variable MANAGED_HSM_URL with the URL of your managed HSM, EKM_PROXY_HOST with the host of your EKM proxy,
#    and CA_CERTIFICATE with the proxy server's certificate in DER format and base64 encoded.
#
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# 5. An EKM (External Key Manager) proxy reachable from the Managed HSM. Replace the placeholder host
#    and certificate bytes below with values that match your EKM proxy deployment.
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates Managed HSM External Key Manager (EKM) connection management
#
# 1. Create an EKM connection (create_ekm_connection)
#
# 2. Read the EKM connection (get_ekm_connection)
#
# 3. Get the EKM proxy client certificate (get_ekm_certificate)
#
# 4. Check an EKM connection (check_ekm_connection)
#
# 5. Update the EKM connection (update_ekm_connection)
#
# 6. Delete the EKM connection (delete_ekm_connection)
# ----------------------------------------------------------------------------------------------------------

# Instantiate an EKM client that will be used to call the service.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.


async def run_sample():
    MANAGED_HSM_URL = os.environ["MANAGED_HSM_URL"]
    credential = DefaultAzureCredential()
    client = KeyVaultEkmClient(vault_url=MANAGED_HSM_URL, credential=credential)

    # First, let's create an EKM connection
    print("\n.. Create EKM connection")
    EKM_PROXY_HOST = os.environ["EKM_PROXY_HOST"]
    CA_CERTIFICATE = os.environ["CA_CERTIFICATE"]
    CA_CERTIFICATES = [CA_CERTIFICATE]
    ekm_connection = KeyVaultEkmConnection(
        host=EKM_PROXY_HOST,
        server_ca_certificates=[base64.b64decode(cert) for cert in CA_CERTIFICATES],
        path_prefix="/api/v1",
    )
    created_ekm_connection = await client.create_ekm_connection(connection=ekm_connection)
    print(f"EKM connection created with host: {created_ekm_connection.host}")

    # Let's get the EKM connection we just created
    print("\n.. Get EKM connection")
    retrieved_ekm_connection = await client.get_ekm_connection()
    print("Retrieved EKM connection with:")
    print(f"\tHost: {retrieved_ekm_connection.host}")
    print(f"\tPath prefix: {retrieved_ekm_connection.path_prefix}")
    print(f"\tServer subject common name: {retrieved_ekm_connection.server_subject_common_name}")

    # Get the EKM certificate
    print("\n.. Get EKM certificate")
    ekm_certificate = await client.get_ekm_certificate()
    print(f"EKM certificate retrieved with subject: {ekm_certificate.subject_common_name}")

    # Check the EKM connection status
    print("\n.. Check EKM connection")
    connection_status = await client.check_ekm_connection()
    print("EKM connection status:")
    print(f"\tAPI Version: {connection_status.api_version}")
    print(f"\tProxy Vendor: {connection_status.proxy_vendor}")
    print(f"\tProxy Name: {connection_status.proxy_name}")
    print(f"\tEKM Vendor: {connection_status.ekm_vendor}")
    print(f"\tEKM Product: {connection_status.ekm_product}")

    # Update the EKM connection
    print("\n.. Update EKM connection")
    updated_ekm_connection = KeyVaultEkmConnection(
        host="ekm-proxy-updated.contoso.com",
        server_ca_certificates=[base64.b64decode(cert) for cert in CA_CERTIFICATES],
        path_prefix="/api/v2",
    )
    result = await client.update_ekm_connection(connection=updated_ekm_connection)
    print(f"EKM connection updated with host: {result.host}")

    # Finally, let's delete the EKM connection
    print("\n.. Delete EKM connection")
    deleted_ekm_connection = await client.delete_ekm_connection()
    print("EKM connection deleted successfully")

    await client.close()
    await credential.close()


if __name__ == "__main__":
    asyncio.run(run_sample())
