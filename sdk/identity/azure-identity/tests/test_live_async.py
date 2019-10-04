# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

import pytest
from azure.identity.aio import DefaultAzureCredential, CertificateCredential, ClientSecretCredential

ARM_SCOPE = "https://management.azure.com/.default"


async def get_token(credential):
    token = await credential.get_token(ARM_SCOPE)
    assert token
    assert token.token
    assert token.expires_on


@pytest.mark.asyncio
async def test_certificate_credential(live_certificate_settings):
    credential = CertificateCredential(
        live_certificate_settings["tenant_id"],
        live_certificate_settings["client_id"],
        live_certificate_settings["cert_path"],
    )
    await get_token(credential)


@pytest.mark.asyncio
async def test_client_secret_credential(live_identity_settings):
    credential = ClientSecretCredential(
        live_identity_settings["tenant_id"],
        live_identity_settings["client_id"],
        live_identity_settings["client_secret"],
    )
    await get_token(credential)


@pytest.mark.asyncio
async def test_default_credential(live_identity_settings):
    credential = DefaultAzureCredential()
    await get_token(credential)
