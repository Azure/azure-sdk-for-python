# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

import pytest

from azure.identity._constants import EnvironmentVariables
from azure.identity.aio import DefaultAzureCredential, CertificateCredential, ClientSecretCredential
from azure.identity.aio._credentials.managed_identity import ImdsCredential, MsiCredential

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


@pytest.mark.skipif("TEST_IMDS" not in os.environ, reason="To test IMDS authentication, set $TEST_IMDS with any value")
@pytest.mark.asyncio
async def test_imds_credential():
    await get_token(ImdsCredential())


@pytest.mark.skipif(
    EnvironmentVariables.MSI_ENDPOINT not in os.environ or EnvironmentVariables.MSI_SECRET in os.environ,
    reason="Legacy MSI unavailable",
)
@pytest.mark.asyncio
async def test_msi_legacy():
    await get_token(MsiCredential())


@pytest.mark.skipif(
    EnvironmentVariables.MSI_ENDPOINT not in os.environ or EnvironmentVariables.MSI_SECRET not in os.environ,
    reason="App Service MSI unavailable",
)
@pytest.mark.asyncio
async def test_msi_app_service():
    await get_token(MsiCredential())
