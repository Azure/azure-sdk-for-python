# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultEkmClient, KeyVaultEkmConnection

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. A managed HSM (https://learn.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli)
#
# 2. azure-keyvault-administration and azure-identity libraries (pip install these)
#
# 3. Set environment variable MANAGED_HSM_URL with the URL of your managed HSM
#
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# 5. An EKM (External Key Manager) proxy reachable from the Managed HSM. Replace the placeholder host
#    and certificate bytes below with values that match your EKM proxy deployment. See
#    https://learn.microsoft.com/azure/key-vault/managed-hsm/external-key-manager-overview for details.
#
# Note: EKM operations are only available on the 2026-01-01-preview service API version. Pass
# api_version="2026-01-01-preview" when constructing the client.
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates Managed HSM External Key Manager (EKM) connection management
#
# 1. Get the EKM proxy client certificate (get_ekm_certificate)
#
# 2. Create an EKM connection (create_ekm_connection)
#
# 3. Read the EKM connection (get_ekm_connection)
#
# 4. Update the EKM connection (update_ekm_connection)
#
# 5. Check connectivity to the EKM proxy (check_ekm_connection)
#
# 6. Delete the EKM connection (delete_ekm_connection)
# ----------------------------------------------------------------------------------------------------------

MANAGED_HSM_URL = os.environ["MANAGED_HSM_URL"]

# Instantiate an EKM client. EKM operations require service API version 2026-01-01-preview.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
credential = DefaultAzureCredential()
client = KeyVaultEkmClient(vault_url=MANAGED_HSM_URL, credential=credential, api_version="2026-01-01-preview")

# 1. Inspect the EKM proxy client certificate the Managed HSM will present when contacting your EKM proxy.
#    Use the subject common name and CA chain to provision the proxy to trust the HSM as a client.
print("\n.. Get EKM proxy client certificate info")
cert_info = client.get_ekm_certificate()
print(f"Client subject common name: {cert_info.subject_common_name}")
print(f"Client CA certificate count: {len(cert_info.ca_certificates or [])}")

# 2. Create an EKM connection. Replace these placeholder values with the FQDN of your EKM proxy and the
#    DER-encoded server CA certificate chain that issued its server certificate.
ekm_proxy_host = "ekm.contoso.com"
server_ca_chain = [b"\x30\x82\x01\x00"]  # Replace with your real DER-encoded CA certificate(s)

print("\n.. Create EKM connection")
new_connection = KeyVaultEkmConnection(
    host=ekm_proxy_host,
    server_ca_certificates=server_ca_chain,
    path_prefix="/api",
    server_subject_common_name=ekm_proxy_host,
)
created = client.create_ekm_connection(new_connection)
print(f"EKM connection created for host: {created.host} (path_prefix={created.path_prefix})")

# 3. Read the EKM connection back from the service.
print("\n.. Get EKM connection")
fetched = client.get_ekm_connection()
print(f"Configured EKM host: {fetched.host}")

# 4. Update the EKM connection (e.g., flip the path_prefix to a new API version).
print("\n.. Update EKM connection path_prefix")
updated_input = KeyVaultEkmConnection(
    host=fetched.host,
    server_ca_certificates=fetched.server_ca_certificates,
    path_prefix="/v2",
    server_subject_common_name=fetched.server_subject_common_name,
)
updated = client.update_ekm_connection(updated_input)
print(f"Updated path_prefix to: {updated.path_prefix}")

# 5. Check the connection by having the HSM ping the EKM proxy.
print("\n.. Check EKM connection")
proxy_info = client.check_ekm_connection()
print(
    f"EKM proxy reachable: vendor={proxy_info.proxy_vendor}, name={proxy_info.proxy_name}, "
    f"api_version={proxy_info.api_version}, ekm_vendor={proxy_info.ekm_vendor}, "
    f"ekm_product={proxy_info.ekm_product}"
)

# 6. Tear down the EKM connection.
print("\n.. Delete EKM connection")
deleted = client.delete_ekm_connection()
print(f"Deleted EKM connection for host: {deleted.host}")
