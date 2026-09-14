# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import json
import os

from azure.identity.aio import DefaultAzureCredential
from azure.keyvault.keys import KeyOperation, KeyReleasePolicy
from azure.keyvault.keys.aio import KeyClient
from azure.keyvault.keys.crypto import KeySecureWrapAlgorithm
from azure.keyvault.keys.crypto.aio import CryptographyClient

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. An Azure Key Vault Managed HSM (https://learn.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli).
#    Secure Wrap/Unwrap operations are only supported on Managed HSM, not on standard Key Vaults.
#
# 2. azure-keyvault-keys and azure-identity libraries (pip install these)
#
# 3. Set environment variable MANAGED_HSM_URL with the URL of your Managed HSM
#
# 4. Set environment variable AZURE_KEYVAULT_ATTESTATION_URL with the URL of the Microsoft Azure Attestation (MAA)
#    authority that the wrapping key's release policy will trust
#
# 5. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# 6. Key create, get, and crypto wrap/unwrap permissions for your service principal in your Managed HSM
#
# 7. Set environment variable AZURE_KEYVAULT_TARGET_ATTESTATION_TOKEN with a valid attestation token signed by
#    Microsoft Azure Attestation (MAA) for the target trusted execution environment (TEE). This is required to
#    run the secure_unwrap_key step.
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


async def run_sample():
    # Instantiate clients that will be used to call the service.
    # Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
    MANAGED_HSM_URL = os.environ["MANAGED_HSM_URL"]
    ATTESTATION_URL = os.environ["AZURE_KEYVAULT_ATTESTATION_URL"]
    credential = DefaultAzureCredential()
    key_client = KeyClient(vault_url=MANAGED_HSM_URL, credential=credential)

    # Secure wrap/unwrap keys must be created with the secureWrapKey and secureUnwrapKey operations and a release
    # policy. The release policy governs which target environments (TEEs) the wrapping key may be released into.
    release_policy_json = {
        "anyOf": [
            {
                "anyOf": [{"claim": "sdk-test", "equals": True}],
                "authority": ATTESTATION_URL.rstrip("/") + "/",
            }
        ],
        "version": "1.0.0",
    }
    release_policy = KeyReleasePolicy(json.dumps(release_policy_json).encode())

    # Create an HSM-backed RSA key to act as the wrapping key.
    print("\n.. Create a wrapping key")
    key_name = "secureWrapKeyNameAsync"
    wrapping_key = await key_client.create_rsa_key(
        key_name,
        hardware_protected=True,
        key_operations=[KeyOperation.secure_wrap_key, KeyOperation.secure_unwrap_key],
        release_policy=release_policy,
    )
    print(f"Wrapping key '{wrapping_key.name}' created of type '{wrapping_key.key_type}'.")

    # Build a CryptographyClient bound to the wrapping key.
    crypto_client = CryptographyClient(wrapping_key, credential=credential)

    # Securely wrap a key generated inside the HSM trusted execution environment.
    print("\n.. Securely wrap a TEE-generated key")
    wrap_result = await crypto_client.secure_wrap_key(KeySecureWrapAlgorithm.rsa_oaep_256)
    print(f"Wrapped key produced for '{wrap_result.key_id}' using '{wrap_result.algorithm}'.")
    encrypted_key = wrap_result.encrypted_key

    # Unwrap the key into a target TEE. This requires a valid attestation token signed by Microsoft Azure
    # Attestation (MAA) for the target environment. The token is opaque to the SDK; obtain it from your TEE
    # / attestation flow and pass it as `target_attestation_token`.
    target_attestation_token = os.environ["AZURE_KEYVAULT_TARGET_ATTESTATION_TOKEN"]
    print("\n.. Securely unwrap the key into a target TEE")
    unwrap_result = await crypto_client.secure_unwrap_key(
        KeySecureWrapAlgorithm.rsa_oaep_256, encrypted_key, target_attestation_token
    )
    print(f"Unwrapped key returned for '{unwrap_result.key_id}' using '{unwrap_result.algorithm}'.")

    print("\nrun_sample done")
    await crypto_client.close()
    await key_client.close()
    await credential.close()


if __name__ == "__main__":
    asyncio.run(run_sample())
