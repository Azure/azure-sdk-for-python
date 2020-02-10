# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from unittest.mock import Mock
from urllib.parse import urlparse

from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity._internal.user_agent import USER_AGENT
from azure.identity.aio import CertificateCredential

import pytest

from helpers import build_aad_response, urlsafeb64_decode, mock_response, Request
from helpers_async import async_validating_transport, AsyncMockTransport
from test_certificate_credential import BOTH_CERTS, CERT_PATH, validate_jwt


@pytest.mark.asyncio
async def test_close():
    transport = AsyncMockTransport()
    credential = CertificateCredential("tenant-id", "client-id", CERT_PATH, transport=transport)

    await credential.close()

    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_context_manager():
    transport = AsyncMockTransport()
    credential = CertificateCredential("tenant-id", "client-id", CERT_PATH, transport=transport)

    async with credential:
        assert transport.__aenter__.call_count == 1

    assert transport.__aenter__.call_count == 1
    assert transport.__aexit__.call_count == 1


@pytest.mark.asyncio
async def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    async def send(*_, **__):
        return mock_response(json_payload=build_aad_response(access_token="**"))

    credential = CertificateCredential(
        "tenant-id", "client-id", CERT_PATH, policies=[ContentDecodePolicy(), policy], transport=Mock(send=send)
    )

    await credential.get_token("scope")

    assert policy.on_request.called


@pytest.mark.asyncio
async def test_user_agent():
    transport = async_validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = CertificateCredential("tenant-id", "client-id", CERT_PATH, transport=transport)

    await credential.get_token("scope")


@pytest.mark.asyncio
@pytest.mark.parametrize("cert_path,cert_password", BOTH_CERTS)
async def test_request_url(cert_path, cert_password):
    authority = "authority.com"
    tenant_id = "expected_tenant"
    access_token = "***"

    def validate_url(url):
        parsed = urlparse(url)
        assert parsed.scheme == "https"
        assert parsed.netloc == authority
        assert parsed.path.startswith("/" + tenant_id)

    async def mock_send(request, **kwargs):
        validate_url(request.url)
        return mock_response(json_payload={"token_type": "Bearer", "expires_in": 42, "access_token": access_token})

    cred = CertificateCredential(
        tenant_id, "client-id", cert_path, password=cert_password, transport=Mock(send=mock_send), authority=authority
    )
    token = await cred.get_token("scope")
    assert token.token == access_token


@pytest.mark.asyncio
@pytest.mark.parametrize("cert_path,cert_password", BOTH_CERTS)
async def test_request_body(cert_path, cert_password):
    access_token = "***"
    authority = "authority.com"
    client_id = "client-id"
    expected_scope = "scope"
    tenant_id = "tenant"

    async def mock_send(request, **kwargs):
        assert request.body["grant_type"] == "client_credentials"
        assert request.body["scope"] == expected_scope

        with open(cert_path, "rb") as cert_file:
            validate_jwt(request, client_id, cert_file.read())

        return mock_response(json_payload={"token_type": "Bearer", "expires_in": 42, "access_token": access_token})

    cred = CertificateCredential(
        tenant_id, client_id, cert_path, password=cert_password, transport=Mock(send=mock_send), authority=authority
    )
    token = await cred.get_token("scope")

    assert token.token == access_token
