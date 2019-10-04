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


def test_certificate_credential(live_certificate):
    credential = CertificateCredential(
        live_certificate["client_id"], live_certificate["tenant_id"], live_certificate["cert_path"]
    )
    get_token(credential)


def test_client_secret_credential(live_service_principal):
    credential = ClientSecretCredential(
        live_service_principal["client_id"],
        live_service_principal["client_secret"],
        live_service_principal["tenant_id"],
    )
    get_token(credential)


def test_default_credential(live_service_principal):
    credential = DefaultAzureCredential()
    get_token(credential)


def test_confidential_client_credential(live_service_principal):
    credential = ConfidentialClientCredential(
        client_id=live_service_principal["client_id"],
        client_credential=live_service_principal["client_secret"],
        authority=KnownAuthorities.AZURE_PUBLIC_CLOUD,
        tenant=live_service_principal["tenant_id"],
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
