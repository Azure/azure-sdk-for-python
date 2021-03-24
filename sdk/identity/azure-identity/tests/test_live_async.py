# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.identity.aio import DefaultAzureCredential, CertificateCredential, ClientSecretCredential

ARM_SCOPE = "https://management.azure.com/.default"


async def get_token(credential):
    token = await credential.get_token(ARM_SCOPE)
    assert token
    assert token.token
    assert token.expires_on


@pytest.mark.asyncio
async def test_certificate_credential(live_certificate):
    tenant_id = live_certificate["tenant_id"]
    client_id = live_certificate["client_id"]

    credential = CertificateCredential(tenant_id, client_id, live_certificate["cert_path"])
    await get_token(credential)

    credential = CertificateCredential(
        tenant_id, client_id, live_certificate["cert_with_password_path"], password=live_certificate["password"]
    )
    await get_token(credential)

    credential = CertificateCredential(tenant_id, client_id, certificate_data=live_certificate["cert_bytes"])
    await get_token(credential)

    credential = CertificateCredential(
        tenant_id,
        client_id,
        certificate_data=live_certificate["cert_with_password_bytes"],
        password=live_certificate["password"],
    )
    await get_token(credential)


@pytest.mark.asyncio
async def test_client_secret_credential(live_service_principal):
    credential = ClientSecretCredential(
        live_service_principal["tenant_id"],
        live_service_principal["client_id"],
        live_service_principal["client_secret"],
    )
    await get_token(credential)


@pytest.mark.asyncio
async def test_default_credential(live_service_principal):
    credential = DefaultAzureCredential()
    await get_token(credential)
