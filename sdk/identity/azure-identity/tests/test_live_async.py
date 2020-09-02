# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.identity.aio import DefaultAzureCredential, CertificateCredential, ClientSecretCredential


async def get_token(credential, scope):
    token = await credential.get_token(scope)
    assert token
    assert token.token
    assert token.expires_on


@pytest.mark.asyncio
async def test_certificate_credential(live_cloud_environment, live_certificate):
    credential = CertificateCredential(
        live_certificate["tenant_id"],
        live_certificate["client_id"],
        live_certificate["cert_path"],
        authority=live_cloud_environment["authority"],
    )
    await get_token(credential, live_cloud_environment["scope"])


@pytest.mark.asyncio
async def test_certificate_credential_with_password(live_cloud_environment, live_certificate_with_password):
    credential = CertificateCredential(
        live_certificate_with_password["tenant_id"],
        live_certificate_with_password["client_id"],
        live_certificate_with_password["cert_path"],
        password=live_certificate_with_password["password"],
        authority=live_cloud_environment["authority"],
    )
    await get_token(credential, live_cloud_environment["scope"])


@pytest.mark.asyncio
async def test_client_secret_credential(live_cloud_environment, live_service_principal):
    credential = ClientSecretCredential(
        live_service_principal["tenant_id"],
        live_service_principal["client_id"],
        live_service_principal["client_secret"],
        authority=live_cloud_environment["authority"],
    )
    await get_token(credential, live_cloud_environment["scope"])


@pytest.mark.asyncio
async def test_default_credential(live_cloud_environment):
    credential = DefaultAzureCredential(authority=live_cloud_environment["authority"])
    await get_token(credential, live_cloud_environment["scope"])
