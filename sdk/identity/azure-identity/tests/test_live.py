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
    UsernamePasswordCredential,
)
from azure.identity._constants import DEVELOPER_SIGN_ON_CLIENT_ID

from helpers import get_token_payload_contents

ARM_SCOPE = "https://management.azure.com/.default"


def get_token(credential, **kwargs):
    token = credential.get_token(ARM_SCOPE, **kwargs)
    assert token
    assert token.token
    assert token.expires_on
    return token


@pytest.mark.parametrize("certificate_fixture", ("live_pem_certificate", "live_pfx_certificate"))
def test_certificate_credential(certificate_fixture, request):
    cert = request.getfixturevalue(certificate_fixture)

    tenant_id = cert["tenant_id"]
    client_id = cert["client_id"]

    credential = CertificateCredential(tenant_id, client_id, cert["cert_path"])
    get_token(credential)

    credential = CertificateCredential(tenant_id, client_id, cert["cert_with_password_path"], password=cert["password"])
    get_token(credential)

    credential = CertificateCredential(tenant_id, client_id, certificate_data=cert["cert_bytes"])
    get_token(credential)

    credential = CertificateCredential(
        tenant_id, client_id, certificate_data=cert["cert_with_password_bytes"], password=cert["password"]
    )
    token = get_token(credential, enable_cae=True)
    parsed_payload = get_token_payload_contents(token.token)
    assert "xms_cc" in parsed_payload and "CP1" in parsed_payload["xms_cc"]


def test_client_secret_credential(live_service_principal):
    credential = ClientSecretCredential(
        live_service_principal["tenant_id"],
        live_service_principal["client_id"],
        live_service_principal["client_secret"],
    )
    token = get_token(credential, enable_cae=True)
    parsed_payload = get_token_payload_contents(token.token)
    assert "xms_cc" in parsed_payload and "CP1" in parsed_payload["xms_cc"]


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
