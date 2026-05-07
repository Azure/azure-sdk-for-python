# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import ApiVersion, KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, KeySecureWrapAlgorithm

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault Managed HSM (https://learn.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli)
#
# 2. azure-keyvault-keys and azure-identity libraries (pip install these)
#
# 3. Set environment variable VAULT_URL with the URL of your Managed HSM
#
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# 5. Key create, get, and crypto wrap/unwrap permissions for your service principal in your Managed HSM
#
# 6. To run secure_unwrap_key end-to-end, set environment variable AZURE_KEYVAULT_TARGET_ATTESTATION_TOKEN with a
#    valid attestation token signed by Microsoft Azure Attestation (MAA) for the target trusted execution
#    environment (TEE). Without it the unwrap step is skipped.
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates Secure Wrap and Secure Unwrap operations against a Managed HSM. These operations let
# the HSM generate a fresh key inside its trusted execution environment, wrap it under an HSM key, and (later)
# release it back into a target TEE that can prove its identity via an attestation token.
#
# Note: Secure Wrap/Unwrap operations require API version 2026-01-01-preview or later.
#
# 1. Create an HSM-backed RSA wrapping key (create_rsa_key)
#
# 2. Securely wrap a freshly generated TEE key (secure_wrap_key)
#
# 3. Securely unwrap the key into a target TEE (secure_unwrap_key)
# ----------------------------------------------------------------------------------------------------------

# Instantiate clients that will be used to call the service.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
VAULT_URL = os.environ["VAULT_URL"]
credential = DefaultAzureCredential()
key_client = KeyClient(vault_url=VAULT_URL, credential=credential, api_version=ApiVersion.V2026_01_01_PREVIEW)

# Create an HSM-backed RSA key to act as the wrapping key.
print("\n.. Create a wrapping key")
key_name = "secureWrapKeyName"
wrapping_key = key_client.create_rsa_key(key_name, hardware_protected=True)
print(f"Wrapping key '{wrapping_key.name}' created of type '{wrapping_key.key_type}'.")

# Build a CryptographyClient bound to the wrapping key.
crypto_client = CryptographyClient(
    wrapping_key, credential=credential, api_version=ApiVersion.V2026_01_01_PREVIEW
)

# Securely wrap a key generated inside the HSM trusted execution environment. The wrapped key bytes
# (`encrypted_key`) can later be exchanged with a target TEE via secure_unwrap_key.
print("\n.. Securely wrap a TEE-generated key")
wrap_result = crypto_client.secure_wrap_key(KeySecureWrapAlgorithm.rsa_oaep_256)
print(f"Wrapped key produced for '{wrap_result.key_id}' using '{wrap_result.algorithm}'.")
encrypted_key = wrap_result.encrypted_key

# Unwrap the key into a target TEE. This requires a valid attestation token signed by Microsoft Azure
# Attestation (MAA) for the target environment. The token is opaque to the SDK; obtain it from your TEE
# / attestation flow and pass it as `target_attestation_token`.
target_attestation_token = os.environ.get("AZURE_KEYVAULT_TARGET_ATTESTATION_TOKEN")
if target_attestation_token:
    print("\n.. Securely unwrap the key into a target TEE")
    unwrap_result = crypto_client.secure_unwrap_key(
        KeySecureWrapAlgorithm.rsa_oaep_256, encrypted_key, target_attestation_token
    )
    print(f"Unwrapped key returned for '{unwrap_result.key_id}' using '{unwrap_result.algorithm}'.")
else:
    print("\n.. Skipping secure_unwrap_key (set AZURE_KEYVAULT_TARGET_ATTESTATION_TOKEN to enable).")
