# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os

try:
    from unittest import mock
except ImportError:  # python < 3.3
    import mock  # type: ignore

from azure.identity.aio import DefaultAzureCredential, CertificateCredential, ClientSecretCredential
from azure.identity.constants import EnvironmentVariables
import pytest

ARM_SCOPE = "https://management.azure.com/.default"


@pytest.mark.asyncio
async def test_certificate_credential(live_certificate_settings):
    credential = CertificateCredential(
        live_certificate_settings["client_id"],
        live_certificate_settings["tenant_id"],
        live_certificate_settings["cert_path"],
    )
    token = await credential.get_token(ARM_SCOPE)
    assert token
    assert token.token
    assert token.expires_on


@pytest.mark.asyncio
async def test_client_secret_credential(live_identity_settings):
    credential = ClientSecretCredential(
        live_identity_settings["client_id"],
        live_identity_settings["client_secret"],
        live_identity_settings["tenant_id"],
    )
    token = await credential.get_token(ARM_SCOPE)
    assert token
    assert token.token
    assert token.expires_on


@pytest.mark.asyncio
async def test_default_credential(live_identity_settings):
    credential = DefaultAzureCredential()
    token = await credential.get_token(ARM_SCOPE)
    assert token
    assert token.token
    assert token.expires_on
