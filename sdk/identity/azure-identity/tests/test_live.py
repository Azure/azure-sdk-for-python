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
from azure.identity._constants import DEVELOPER_SIGN_ON_CLIENT_ID

ARM_SCOPE = "https://management.azure.com/.default"


def get_token(credential):
    token = credential.get_token(ARM_SCOPE)
    assert token
    assert token.token
    assert token.expires_on


def test_certificate_credential(live_certificate):
    tenant_id = live_certificate["tenant_id"]
    client_id = live_certificate["client_id"]

    credential = CertificateCredential(tenant_id, client_id, live_certificate["cert_path"])
    get_token(credential)

    credential = CertificateCredential(
        tenant_id, client_id, live_certificate["cert_with_password_path"], password=live_certificate["password"]
    )
    get_token(credential)

    credential = CertificateCredential(tenant_id, client_id, certificate_data=live_certificate["cert_bytes"])
    get_token(credential)

    credential = CertificateCredential(
        tenant_id,
        client_id,
        certificate_data=live_certificate["cert_with_password_bytes"],
        password=live_certificate["password"],
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

    credential = DeviceCodeCredential(client_id=DEVELOPER_SIGN_ON_CLIENT_ID, prompt_callback=prompt, timeout=40)
    get_token(credential)
