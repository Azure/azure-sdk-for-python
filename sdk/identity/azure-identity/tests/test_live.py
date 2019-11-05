# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.identity import DefaultAzureCredential, CertificateCredential, ClientSecretCredential, KnownAuthorities
from azure.identity._internal import ConfidentialClientCredential

ARM_SCOPE = "https://management.azure.com/.default"


def test_certificate_credential(live_certificate_settings):
    credential = CertificateCredential(
        live_certificate_settings["tenant_id"],
        live_certificate_settings["client_id"],
        live_certificate_settings["cert_path"],
    )
    token = credential.get_token(ARM_SCOPE)
    assert token
    assert token.token
    assert token.expires_on


def test_client_secret_credential(live_identity_settings):
    credential = ClientSecretCredential(
        live_identity_settings["tenant_id"],
        live_identity_settings["client_id"],
        live_identity_settings["client_secret"],
    )
    token = credential.get_token(ARM_SCOPE)
    assert token
    assert token.token
    assert token.expires_on


def test_default_credential(live_identity_settings):
    credential = DefaultAzureCredential()
    token = credential.get_token(ARM_SCOPE)
    assert token
    assert token.token
    assert token.expires_on


def test_confidential_client_credential(live_identity_settings):
    credential = ConfidentialClientCredential(
        client_id=live_identity_settings["client_id"],
        client_credential=live_identity_settings["client_secret"],
        authority=KnownAuthorities.AZURE_PUBLIC_CLOUD,
        tenant_id=live_identity_settings["tenant_id"],
    )
    token = credential.get_token(ARM_SCOPE)
    assert token
    assert token.token
    assert token.expires_on
