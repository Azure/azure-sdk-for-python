# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import os

from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity import CertificateCredential
from azure.identity._internal.user_agent import USER_AGENT
from six.moves.urllib_parse import urlparse

from helpers import build_aad_response, urlsafeb64_decode, mock_response, Request, validating_transport

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

CERT_PATH = os.path.join(os.path.dirname(__file__), "certificate.pem")


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


def test_request_url():
    authority = "authority.com"
    tenant_id = "expected_tenant"
    access_token = "***"

    def validate_url(url):
        scheme, netloc, path, _, _, _ = urlparse(url)
        assert scheme == "https"
        assert netloc == authority
        assert path.startswith("/" + tenant_id)

    def mock_send(request, **kwargs):
        validate_url(request.url)
        return mock_response(json_payload={"token_type": "Bearer", "expires_in": 42, "access_token": access_token})

    cred = CertificateCredential(tenant_id, "client_id", CERT_PATH, transport=Mock(send=mock_send), authority=authority)
    token = cred.get_token("scope")
    assert token.token == access_token


def test_request_body():
    access_token = "***"
    authority = "authority.com"
    tenant_id = "tenant"

    def validate_url(url):
        scheme, netloc, path, _, _, _ = urlparse(url)
        assert scheme == "https"
        assert netloc == authority
        assert path.startswith("/" + tenant_id)

    def mock_send(request, **kwargs):
        jwt = request.body["client_assertion"]
        header, payload, signature = (urlsafeb64_decode(s) for s in jwt.split("."))
        claims = json.loads(payload.decode("utf-8"))
        validate_url(claims["aud"])
        return mock_response(json_payload={"token_type": "Bearer", "expires_in": 42, "access_token": access_token})

    cred = CertificateCredential(tenant_id, "client_id", CERT_PATH, transport=Mock(send=mock_send), authority=authority)
    token = cred.get_token("scope")
    assert token.token == access_token
