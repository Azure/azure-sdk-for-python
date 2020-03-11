# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import os

from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity import CertificateCredential
from azure.identity._internal.user_agent import USER_AGENT
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import pytest
from six.moves.urllib_parse import urlparse

from helpers import build_aad_response, urlsafeb64_decode, mock_response, Request, validating_transport

try:
    from unittest.mock import Mock
except ImportError:  # python < 3.3
    from mock import Mock  # type: ignore

CERT_PATH = os.path.join(os.path.dirname(__file__), "certificate.pem")
CERT_WITH_PASSWORD_PATH = os.path.join(os.path.dirname(__file__), "certificate-with-password.pem")
CERT_PASSWORD = "password"
BOTH_CERTS = ((CERT_PATH, None), (CERT_WITH_PASSWORD_PATH, CERT_PASSWORD))


def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    def send(*_, **__):
        return mock_response(json_payload=build_aad_response(access_token="**"))

    credential = CertificateCredential(
        "tenant-id", "client-id", CERT_PATH, policies=[ContentDecodePolicy(), policy], transport=Mock(send=send)
    )

    credential.get_token("scope")

    assert policy.on_request.called


def test_user_agent():
    transport = validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = CertificateCredential("tenant-id", "client-id", CERT_PATH, transport=transport)

    credential.get_token("scope")


@pytest.mark.parametrize("cert_path,cert_password", BOTH_CERTS)
def test_request_url(cert_path, cert_password):
    authority = "authority.com"
    tenant_id = "expected_tenant"
    access_token = "***"

    def validate_url(url):
        parsed = urlparse(url)
        assert parsed.scheme == "https"
        assert parsed.netloc == authority
        assert parsed.path.startswith("/" + tenant_id)

    def mock_send(request, **kwargs):
        validate_url(request.url)
        return mock_response(json_payload={"token_type": "Bearer", "expires_in": 42, "access_token": access_token})

    cred = CertificateCredential(
        tenant_id, "client-id", cert_path, password=cert_password, transport=Mock(send=mock_send), authority=authority
    )
    token = cred.get_token("scope")
    assert token.token == access_token


@pytest.mark.parametrize("cert_path,cert_password", BOTH_CERTS)
def test_request_body(cert_path, cert_password):
    access_token = "***"
    authority = "authority.com"
    client_id = "client-id"
    expected_scope = "scope"
    tenant_id = "tenant"

    def mock_send(request, **kwargs):
        assert request.body["grant_type"] == "client_credentials"
        assert request.body["scope"] == expected_scope

        with open(cert_path, "rb") as cert_file:
            validate_jwt(request, client_id, cert_file.read())

        return mock_response(json_payload={"token_type": "Bearer", "expires_in": 42, "access_token": access_token})

    cred = CertificateCredential(
        tenant_id, client_id, cert_path, password=cert_password, transport=Mock(send=mock_send), authority=authority
    )
    token = cred.get_token(expected_scope)
    assert token.token == access_token


def validate_jwt(request, client_id, pem_bytes):
    """Validate the request meets AAD's expectations for a client credential grant using a certificate, as documented
    at https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-certificate-credentials
    """

    cert = x509.load_pem_x509_certificate(pem_bytes, default_backend())

    # jwt is of the form 'header.payload.signature'; 'signature' is 'header.payload' signed with cert's private key
    jwt = request.body["client_assertion"]
    header, payload, signature = (urlsafeb64_decode(s) for s in jwt.split("."))
    signed_part = jwt[: jwt.rfind(".")]
    claims = json.loads(payload.decode("utf-8"))

    deserialized_header = json.loads(header.decode("utf-8"))
    assert deserialized_header["alg"] == "RS256"
    assert deserialized_header["typ"] == "JWT"
    assert urlsafeb64_decode(deserialized_header["x5t"]) == cert.fingerprint(hashes.SHA1())

    assert claims["aud"] == request.url
    assert claims["iss"] == claims["sub"] == client_id

    cert.public_key().verify(signature, signed_part.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
