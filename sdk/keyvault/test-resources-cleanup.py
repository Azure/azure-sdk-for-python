# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from dotenv import load_dotenv
import os

from azure.identity.aio import ClientSecretCredential
from azure.keyvault.certificates.aio import CertificateClient
from azure.keyvault.keys.aio import KeyClient
from azure.keyvault.secrets.aio import SecretClient

load_dotenv()

if "AZURE_KEYVAULT_URL" not in os.environ:
    raise EnvironmentError("Missing a Key Vault URL")
if "KEYVAULT_TENANT_ID" not in os.environ:
    raise EnvironmentError("Missing a tenant ID for Key Vault")
if "KEYVAULT_CLIENT_ID" not in os.environ:
    raise EnvironmentError("Missing a client ID for Key Vault")
if "KEYVAULT_CLIENT_SECRET" not in os.environ:
    raise EnvironmentError("Missing a client secret for Key Vault")

hsm_present = "AZURE_MANAGEDHSM_URL" in os.environ

credential = ClientSecretCredential(
    tenant_id=os.environ["KEYVAULT_TENANT_ID"],
    client_id=os.environ["KEYVAULT_CLIENT_ID"],
    client_secret=os.environ["KEYVAULT_CLIENT_SECRET"]
)

cert_client = CertificateClient(os.environ["AZURE_KEYVAULT_URL"], credential)
key_client = KeyClient(os.environ["AZURE_KEYVAULT_URL"], credential)
hsm_client = KeyClient(os.environ["AZURE_MANAGEDHSM_URL"], credential) if hsm_present else None
secret_client = SecretClient(os.environ["AZURE_KEYVAULT_URL"], credential)

async def delete_certificates():
    coroutines = []

    test_certificates = cert_client.list_properties_of_certificates()
    async for certificate in test_certificates:
        if certificate.name.startswith("livekvtest"):
            coroutines.append(cert_client.delete_certificate(certificate.name))

    return await asyncio.gather(*coroutines)

async def delete_keys_and_secrets():
    coroutines = []

    test_keys = key_client.list_properties_of_keys()
    async for key in test_keys:
        if key.name.startswith("livekvtest"):
            coroutines.append(key_client.delete_key(key.name))

    if hsm_client:
        hsm_test_keys = hsm_client.list_properties_of_keys()
        async for key in hsm_test_keys:
            if key.name.startswith("livekvtest"):
                coroutines.append(hsm_client.delete_key(key.name))

    test_secrets = secret_client.list_properties_of_secrets()
    async for secret in test_secrets:
        if secret.name.startswith("livekvtest"):
            coroutines.append(secret_client.delete_secret(secret.name))

    return await asyncio.gather(*coroutines)

async def purge_resources():
    coroutines = []

    deleted_test_certificates = cert_client.list_deleted_certificates(include_pending=True)
    async for certificate in deleted_test_certificates:
        if certificate.name.startswith("livekvtest"):
            coroutines.append(cert_client.purge_deleted_certificate(certificate.name))

    deleted_test_keys = key_client.list_deleted_keys()
    async for key in deleted_test_keys:
        if key.name.startswith("livekvtest"):
            coroutines.append(key_client.purge_deleted_key(key.name))

    if hsm_client:
        hsm_deleted_test_keys = hsm_client.list_deleted_keys()
        async for key in hsm_deleted_test_keys:
            if key.name.startswith("livekvtest"):
                coroutines.append(hsm_client.purge_deleted_key(key.name))

    deleted_test_secrets = secret_client.list_deleted_secrets()
    async for secret in deleted_test_secrets:
        if secret.name.startswith("livekvtest"):
            coroutines.append(secret_client.purge_deleted_secret(secret.name))

    return await asyncio.gather(*coroutines)

async def close_sessions():
    await credential.close()
    await cert_client.close()
    await key_client.close()
    if hsm_client:
        await hsm_client.close()
    await secret_client.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(delete_certificates())
loop.run_until_complete(delete_keys_and_secrets())
loop.run_until_complete(purge_resources())
loop.run_until_complete(close_sessions())
loop.close()
