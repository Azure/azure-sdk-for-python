# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

import pytest

from azure.identity import (
    DefaultAzureCredential,
    CertificateCredential,
    ClientSecretCredential,
    KnownAuthorities,
    ManagedIdentityCredential,
)
from azure.identity._constants import EnvironmentVariables
from azure.identity._credentials.managed_identity import ImdsCredential, MsiCredential
from azure.identity._internal import ConfidentialClientCredential

ARM_SCOPE = "https://management.azure.com/.default"


def get_token(credential):
    token = credential.get_token(ARM_SCOPE)
    assert token
    assert token.token
    assert token.expires_on


def test_certificate_credential(live_certificate_settings):
    credential = CertificateCredential(
        live_certificate_settings["tenant_id"],
        live_certificate_settings["client_id"],
        live_certificate_settings["cert_path"],
    )
    get_token(credential)


def test_client_secret_credential(live_identity_settings):
    credential = ClientSecretCredential(
        live_identity_settings["tenant_id"],
        live_identity_settings["client_id"],
        live_identity_settings["client_secret"],
    )
    get_token(credential)


def test_default_credential(live_identity_settings):
    credential = DefaultAzureCredential()
    get_token(credential)


def test_confidential_client_credential(live_identity_settings):
    credential = ConfidentialClientCredential(
        client_id=live_identity_settings["client_id"],
        client_credential=live_identity_settings["client_secret"],
        authority=KnownAuthorities.AZURE_PUBLIC_CLOUD,
        tenant_id=live_identity_settings["tenant_id"],
    )
    get_token(credential)


@pytest.mark.skipif("TEST_IMDS" not in os.environ, reason="To test IMDS authentication, set $TEST_IMDS with any value")
def test_imds_credential():
    get_token(ImdsCredential())


@pytest.mark.skipif(
    EnvironmentVariables.MSI_ENDPOINT not in os.environ or EnvironmentVariables.MSI_SECRET in os.environ,
    reason="Legacy MSI unavailable",
)
def test_msi_legacy():
    get_token(MsiCredential())


@pytest.mark.skipif(
    EnvironmentVariables.MSI_ENDPOINT not in os.environ or EnvironmentVariables.MSI_SECRET not in os.environ,
    reason="App Service MSI unavailable",
)
def test_msi_app_service():
    get_token(MsiCredential())
