# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. A managed HSM (https://learn.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli)
#
# 2. azure-keyvault-administration and azure-identity libraries (pip install these)
#
# 3. Set environment variable MANAGED_HSM_URL with the URL of your managed HSM, and PRIVATE_LINK_SERVICE_ID with the
#    alias of the Private Link Service that fronts your EKM proxy.
#
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# 5. A Private Link Service that fronts an EKM (External Key Manager) proxy. A Managed HSM pool may have up to two EKM
#    proxy private endpoints.
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates Managed HSM External Key Manager (EKM) proxy private endpoint management
#
# 1. Create an EKM proxy private endpoint (begin_create_ekm_private_endpoint)
#
# 2. Read the EKM proxy private endpoint (get_ekm_private_endpoint)
#
# 3. List the EKM proxy private endpoints (list_ekm_private_endpoints)
#
# 4. Connect to the EKM proxy through the private endpoint (create_ekm_connection)
#
# 5. Delete the EKM proxy private endpoint (begin_delete_ekm_private_endpoint)
# ----------------------------------------------------------------------------------------------------------

# Instantiate an EKM client that will be used to call the service.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultEkmClient

MANAGED_HSM_URL = os.environ["MANAGED_HSM_URL"]
PRIVATE_LINK_SERVICE_ID = os.environ["PRIVATE_LINK_SERVICE_ID"]
credential = DefaultAzureCredential()
client = KeyVaultEkmClient(vault_url=MANAGED_HSM_URL, credential=credential)

PRIVATE_ENDPOINT_NAME = "ekm-proxy-pe"

# First, let's create an EKM proxy private endpoint. This is a long-running operation.
print("\n.. Create EKM private endpoint")
# [START begin_create_ekm_private_endpoint]
create_poller = client.begin_create_ekm_private_endpoint(
    PRIVATE_ENDPOINT_NAME,
    PRIVATE_LINK_SERVICE_ID,
    request_message="Please approve this connection from my Managed HSM",
)
create_operation = create_poller.result()
print(f"EKM private endpoint creation finished with status: {create_operation.status}")
# [END begin_create_ekm_private_endpoint]

# Let's get the private endpoint we just created. The Private Link Service owner has to approve the connection
# before the private endpoint can be used by an EKM connection.
print("\n.. Get EKM private endpoint")
# [START get_ekm_private_endpoint]
private_endpoint = client.get_ekm_private_endpoint(PRIVATE_ENDPOINT_NAME)
print("Retrieved EKM private endpoint with:")
print(f"\tName: {private_endpoint.name}")
print(f"\tLocation: {private_endpoint.location}")
print(f"\tProvisioning state: {private_endpoint.provisioning_state}")
if private_endpoint.private_link_service_connection_state:
    print(f"\tConnection status: {private_endpoint.private_link_service_connection_state.status}")
# [END get_ekm_private_endpoint]

# Let's list all of the private endpoints on the Managed HSM
print("\n.. List EKM private endpoints")
# [START list_ekm_private_endpoints]
private_endpoints = client.list_ekm_private_endpoints()
for endpoint in private_endpoints:
    print(f"EKM private endpoint {endpoint.name} is in state {endpoint.provisioning_state}")
# [END list_ekm_private_endpoints]

# Once the connection is approved, an EKM connection can reach the EKM proxy through the private endpoint. To do so,
# set the connection's `host` to the private endpoint's name and its `connectivity_mode` to `PRIVATE_ENDPOINT`.
print("\n.. Create EKM connection over the private endpoint")
# [START create_private_ekm_connection]
import base64
from azure.keyvault.administration import KeyVaultEkmConnection, KeyVaultEkmConnectivityMode

CA_CERTIFICATE = os.environ["CA_CERTIFICATE"]
ekm_connection = KeyVaultEkmConnection(
    host=PRIVATE_ENDPOINT_NAME,
    server_ca_certificates=[base64.b64decode(CA_CERTIFICATE)],
    path_prefix="/api/v1",
    connectivity_mode=KeyVaultEkmConnectivityMode.PRIVATE_ENDPOINT,
)
created_ekm_connection = client.create_ekm_connection(connection=ekm_connection)
print(f"EKM connection created with connectivity mode: {created_ekm_connection.connectivity_mode}")
# [END create_private_ekm_connection]

# Finally, let's delete the private endpoint. Deletion is rejected while an EKM connection still references the
# private endpoint, so we delete the EKM connection first.
print("\n.. Delete EKM private endpoint")
# [START begin_delete_ekm_private_endpoint]
client.delete_ekm_connection()
delete_poller = client.begin_delete_ekm_private_endpoint(PRIVATE_ENDPOINT_NAME)
delete_operation = delete_poller.result()
print(f"EKM private endpoint deletion finished with status: {delete_operation.status}")
# [END begin_delete_ekm_private_endpoint]
