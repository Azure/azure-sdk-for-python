# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from itertools import product
import pytest

from azure.identity.aio import (
    DefaultAzureCredential,
    CertificateCredential,
    ClientSecretCredential,
    AzureCliCredential,
    AzurePowerShellCredential,
    AzureDeveloperCliCredential,
)

from helpers import get_token_payload_contents, GET_TOKEN_METHODS

ARM_SCOPE = "https://management.azure.com/.default"


async def get_token(credential, get_token_method, **kwargs):
    token = await getattr(credential, get_token_method)(ARM_SCOPE, **kwargs)
    assert token
    assert token.token
    assert token.expires_on
    return token


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "certificate_fixture,get_token_method", product(("live_pem_certificate", "live_pfx_certificate"), GET_TOKEN_METHODS)
)
async def test_certificate_credential(certificate_fixture, get_token_method, request):
    cert = request.getfixturevalue(certificate_fixture)

    tenant_id = cert["tenant_id"]
    client_id = cert["client_id"]

    credential = CertificateCredential(tenant_id, client_id, cert["cert_path"])
    await get_token(credential, get_token_method)

    credential = CertificateCredential(tenant_id, client_id, certificate_data=cert["cert_bytes"])
    token = await get_token(credential, get_token_method, enable_cae=True)
    parsed_payload = get_token_payload_contents(token.token)
    assert "xms_cc" in parsed_payload and "CP1" in parsed_payload["xms_cc"]

    if "password" in cert:
        credential = CertificateCredential(
            tenant_id, client_id, cert["cert_with_password_path"], password=cert["password"]
        )
        await get_token(credential, get_token_method)

        credential = CertificateCredential(
            tenant_id, client_id, certificate_data=cert["cert_with_password_bytes"], password=cert["password"]
        )
        await get_token(credential, get_token_method, enable_cae=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_client_secret_credential(live_service_principal, get_token_method):
    credential = ClientSecretCredential(
        live_service_principal["tenant_id"],
        live_service_principal["client_id"],
        live_service_principal["client_secret"],
    )
    token = await get_token(credential, get_token_method, enable_cae=True)
    parsed_payload = get_token_payload_contents(token.token)
    assert "xms_cc" in parsed_payload and "CP1" in parsed_payload["xms_cc"]


@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_default_credential(live_service_principal, get_token_method):
    credential = DefaultAzureCredential()
    await get_token(credential, get_token_method)


@pytest.mark.manual
@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_cli_credential(get_token_method):
    credential = AzureCliCredential()
    await get_token(credential, get_token_method)


@pytest.mark.manual
@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_dev_cli_credential(get_token_method):
    credential = AzureDeveloperCliCredential()
    await get_token(credential, get_token_method)


@pytest.mark.manual
@pytest.mark.asyncio
@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
async def test_powershell_credential(get_token_method):
    credential = AzurePowerShellCredential()
    await get_token(credential, get_token_method)
