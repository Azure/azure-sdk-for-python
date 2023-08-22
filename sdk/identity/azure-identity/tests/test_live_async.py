# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.identity.aio import DefaultAzureCredential, CertificateCredential, ClientSecretCredential

from helpers import get_token_payload_contents

ARM_SCOPE = "https://management.azure.com/.default"


async def get_token(credential, **kwargs):
    token = await credential.get_token(ARM_SCOPE, **kwargs)
    assert token
    assert token.token
    assert token.expires_on
    return token


@pytest.mark.asyncio
@pytest.mark.parametrize("certificate_fixture", ("live_pem_certificate", "live_pfx_certificate"))
async def test_certificate_credential(certificate_fixture, request):
    cert = request.getfixturevalue(certificate_fixture)

    tenant_id = cert["tenant_id"]
    client_id = cert["client_id"]

    credential = CertificateCredential(tenant_id, client_id, cert["cert_path"])
    await get_token(credential)

    credential = CertificateCredential(tenant_id, client_id, cert["cert_with_password_path"], password=cert["password"])
    await get_token(credential)

    credential = CertificateCredential(tenant_id, client_id, certificate_data=cert["cert_bytes"])
    await get_token(credential)

    credential = CertificateCredential(
        tenant_id, client_id, certificate_data=cert["cert_with_password_bytes"], password=cert["password"]
    )
    token = await get_token(credential, enable_cae=True)
    parsed_payload = get_token_payload_contents(token.token)
    assert "xms_cc" in parsed_payload and "CP1" in parsed_payload["xms_cc"]


@pytest.mark.asyncio
async def test_client_secret_credential(live_service_principal):
    credential = ClientSecretCredential(
        live_service_principal["tenant_id"],
        live_service_principal["client_id"],
        live_service_principal["client_secret"],
    )
    token = await get_token(credential, enable_cae=True)
    parsed_payload = get_token_payload_contents(token.token)
    assert "xms_cc" in parsed_payload and "CP1" in parsed_payload["xms_cc"]


@pytest.mark.asyncio
async def test_default_credential(live_service_principal):
    credential = DefaultAzureCredential()
    await get_token(credential)
