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
    DeviceCodeCredential,
    KnownAuthorities,
    InteractiveBrowserCredential,
    ManagedIdentityCredential,
    UsernamePasswordCredential,
)
from azure.identity._constants import AZURE_CLI_CLIENT_ID, EnvironmentVariables
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
        live_certificate["tenant_id"], live_certificate["client_id"], live_certificate["cert_path"]
    )
    get_token(credential)


def test_client_secret_credential(live_service_principal):
    credential = ClientSecretCredential(
        live_service_principal["tenant_id"],
        live_service_principal["client_id"],
        live_service_principal["client_secret"],
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
        tenant_id=live_service_principal["tenant_id"],
    )
    get_token(credential)


@pytest.mark.skipif("TEST_IMDS" not in os.environ, reason="To test IMDS authentication, set $TEST_IMDS with any value")
def test_imds_credential(managed_identity_id):
    get_token(ImdsCredential())
    if managed_identity_id:
        get_token(ImdsCredential(client_id=managed_identity_id))


@pytest.mark.skipif(
    EnvironmentVariables.MSI_ENDPOINT not in os.environ or EnvironmentVariables.MSI_SECRET in os.environ,
    reason="Legacy MSI unavailable",
)
def test_msi_legacy(managed_identity_id):
    get_token(MsiCredential())
    if managed_identity_id:
        get_token(ImdsCredential(client_id=managed_identity_id))


@pytest.mark.skipif(
    EnvironmentVariables.MSI_ENDPOINT not in os.environ or EnvironmentVariables.MSI_SECRET not in os.environ,
    reason="App Service MSI unavailable",
)
def test_msi_app_service(managed_identity_id):
    get_token(MsiCredential())
    if managed_identity_id:
        get_token(ImdsCredential(client_id=managed_identity_id))


def test_username_password_auth(live_user_details):
    credential = UsernamePasswordCredential(
        client_id=live_user_details["client_id"],
        username=live_user_details["username"],
        password=live_user_details["password"],
        tenant_id=live_user_details["tenant"],
    )
    get_token(credential)


@pytest.mark.manual
@pytest.mark.prints
def test_device_code():
    import webbrowser

    def prompt(url, user_code, _):
        print("opening a browser to '{}', enter device code {}".format(url, user_code))
        webbrowser.open_new_tab(url)

    credential = DeviceCodeCredential(client_id=AZURE_CLI_CLIENT_ID, prompt_callback=prompt, timeout=40)
    get_token(credential)


@pytest.mark.manual
def test_browser_auth():
    credential = InteractiveBrowserCredential(client_id=AZURE_CLI_CLIENT_ID, timeout=40)
    get_token(credential)
