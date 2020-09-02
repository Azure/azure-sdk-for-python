# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.identity import (
    DefaultAzureCredential,
    CertificateCredential,
    ClientSecretCredential,
    DeviceCodeCredential,
    InteractiveBrowserCredential,
    UsernamePasswordCredential,
)
from azure.identity._constants import AZURE_CLI_CLIENT_ID


def get_token(credential, scope):
    token = credential.get_token(scope)
    assert token
    assert token.token
    assert token.expires_on


def test_certificate_credential(live_cloud_environment, live_certificate):
    credential = CertificateCredential(
        live_certificate["tenant_id"],
        live_certificate["client_id"],
        live_certificate["cert_path"],
        authority=live_cloud_environment["authority"],
    )
    get_token(credential, live_cloud_environment["scope"])


def test_certificate_credential_with_password(live_cloud_environment, live_certificate_with_password):
    credential = CertificateCredential(
        live_certificate_with_password["tenant_id"],
        live_certificate_with_password["client_id"],
        live_certificate_with_password["cert_path"],
        password=live_certificate_with_password["password"],
        authority=live_cloud_environment["authority"],
    )
    get_token(credential, live_cloud_environment["scope"])


def test_client_secret_credential(live_cloud_environment, live_service_principal):
    credential = ClientSecretCredential(
        live_service_principal["tenant_id"],
        live_service_principal["client_id"],
        live_service_principal["client_secret"],
        authority=live_cloud_environment["authority"],
    )
    get_token(credential, live_cloud_environment["scope"])


def test_default_credential(live_cloud_environment):
    credential = DefaultAzureCredential(authority=live_cloud_environment["authority"])
    get_token(credential, live_cloud_environment["scope"])


def test_username_password_auth(live_cloud_environment, live_user_details):
    credential = UsernamePasswordCredential(
        client_id=live_user_details["client_id"],
        username=live_user_details["username"],
        password=live_user_details["password"],
        tenant_id=live_user_details["tenant"],
        authority=live_cloud_environment["authority"],
    )
    get_token(credential, live_cloud_environment["scope"])


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
