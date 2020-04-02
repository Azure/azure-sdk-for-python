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
    credential = CertificateCredential(
        live_certificate["tenant_id"], live_certificate["client_id"], live_certificate["cert_path"]
    )
    await get_token(credential)


@pytest.mark.asyncio
async def test_certificate_credential_with_password(live_certificate_with_password):
    credential = CertificateCredential(
        live_certificate_with_password["tenant_id"],
        live_certificate_with_password["client_id"],
        live_certificate_with_password["cert_path"],
        password=live_certificate_with_password["password"],
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
