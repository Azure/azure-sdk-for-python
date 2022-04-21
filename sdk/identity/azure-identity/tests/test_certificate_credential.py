# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import os

from azure.core.exceptions import ClientAuthenticationError
from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity import CertificateCredential, TokenCachePersistenceOptions
from azure.identity._enums import RegionalAuthority
from azure.identity._constants import EnvironmentVariables
from azure.identity._credentials.certificate import load_pkcs12_certificate
from azure.identity._internal.user_agent import USER_AGENT
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from msal import TokenCache
import pytest
import six
from six.moves.urllib_parse import urlparse

from helpers import (
    build_aad_response,
    get_discovery_response,
    urlsafeb64_decode,
    mock_response,
    msal_validating_transport,
    Request,
)

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

PEM_CERT_PATH = os.path.join(os.path.dirname(__file__), "certificate.pem")
PEM_CERT_WITH_PASSWORD_PATH = os.path.join(os.path.dirname(__file__), "certificate-with-password.pem")
PFX_CERT_PATH = os.path.join(os.path.dirname(__file__), "certificate.pfx")
PFX_CERT_WITH_PASSWORD_PATH = os.path.join(os.path.dirname(__file__), "certificate-with-password.pfx")
CERT_PASSWORD = "password"
ALL_CERTS = (
    (PEM_CERT_PATH, None),
    (PEM_CERT_WITH_PASSWORD_PATH, CERT_PASSWORD),  # credential should accept passwords as str or bytes
    (PEM_CERT_WITH_PASSWORD_PATH, CERT_PASSWORD.encode("utf-8")),
    (PFX_CERT_PATH, None),
    (PFX_CERT_WITH_PASSWORD_PATH, CERT_PASSWORD),
    (PFX_CERT_WITH_PASSWORD_PATH, CERT_PASSWORD.encode("utf-8")),
)

EC_CERT_PATH = os.path.join(os.path.dirname(__file__), "ec-certificate.pem")


def test_non_rsa_key():
    """The credential should raise ValueError when given a cert without an RSA private key"""
    with pytest.raises(ValueError, match=".*RS256.*"):
        CertificateCredential("tenant-id", "client-id", EC_CERT_PATH)
    with pytest.raises(ValueError, match=".*RS256.*"):
        CertificateCredential("tenant-id", "client-id", certificate_data=open(EC_CERT_PATH, "rb").read())


def test_tenant_id_validation():
    """The credential should raise ValueError when given an invalid tenant_id"""

    valid_ids = {"c878a2ab-8ef4-413b-83a0-199afb84d7fb", "contoso.onmicrosoft.com", "organizations", "common"}
    for tenant in valid_ids:
        CertificateCredential(tenant, "client-id", PEM_CERT_PATH)

    invalid_ids = {"", "my tenant", "my_tenant", "/", "\\", '"my-tenant"', "'my-tenant'"}
    for tenant in invalid_ids:
        with pytest.raises(ValueError):
            CertificateCredential(tenant, "client-id", PEM_CERT_PATH)


def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = CertificateCredential("tenant-id", "client-id", PEM_CERT_PATH)
    with pytest.raises(ValueError):
        credential.get_token()


def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    transport = msal_validating_transport(
        requests=[Request()], responses=[mock_response(json_payload=build_aad_response(access_token="**"))]
    )

    credential = CertificateCredential(
        "tenant-id", "client-id", PEM_CERT_PATH, policies=[ContentDecodePolicy(), policy], transport=transport
    )

    credential.get_token("scope")

    assert policy.on_request.called


def test_user_agent():
    transport = msal_validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = CertificateCredential("tenant-id", "client-id", PEM_CERT_PATH, transport=transport)

    credential.get_token("scope")

def test_tenant_id():
    transport = msal_validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = CertificateCredential("tenant-id", "client-id", PEM_CERT_PATH, transport=transport)

    credential.get_token("scope", tenant_id="tenant_id")


@pytest.mark.parametrize("authority", ("localhost", "https://localhost"))
def test_authority(authority):
    """the credential should accept an authority, with or without scheme, as an argument or environment variable"""

    tenant_id = "expected-tenant"
    parsed_authority = urlparse(authority)
    expected_netloc = parsed_authority.netloc or authority
    expected_authority = "https://{}/{}".format(expected_netloc, tenant_id)

    mock_ctor = Mock(
        return_value=Mock(acquire_token_silent_with_error=lambda *_, **__: {"access_token": "**", "expires_in": 42})
    )

    credential = CertificateCredential(tenant_id, "client-id", PEM_CERT_PATH, authority=authority)
    with patch("msal.ConfidentialClientApplication", mock_ctor):
        # must call get_token because the credential constructs the MSAL application lazily
        credential.get_token("scope")

    assert mock_ctor.call_count == 1
    _, kwargs = mock_ctor.call_args
    assert kwargs["authority"] == expected_authority
    mock_ctor.reset_mock()

    # authority can be configured via environment variable
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
        credential = CertificateCredential(tenant_id, "client-id", PEM_CERT_PATH, authority=authority)
    with patch("msal.ConfidentialClientApplication", mock_ctor):
        credential.get_token("scope")

    assert mock_ctor.call_count == 1
    _, kwargs = mock_ctor.call_args
    assert kwargs["authority"] == expected_authority


def test_regional_authority():
    """the credential should configure MSAL with a regional authority specified via kwarg or environment variable"""

    mock_confidential_client = Mock(
        return_value=Mock(acquire_token_silent_with_error=lambda *_, **__: {"access_token": "**", "expires_in": 3600}),
    )

    for region in RegionalAuthority:
        mock_confidential_client.reset_mock()

        # region can be configured via environment variable
        with patch.dict("os.environ", {EnvironmentVariables.AZURE_REGIONAL_AUTHORITY_NAME: region}, clear=True):
            credential = CertificateCredential("tenant", "client-id", PEM_CERT_PATH)
        with patch("msal.ConfidentialClientApplication", mock_confidential_client):
            credential.get_token("scope")

        assert mock_confidential_client.call_count == 1
        _, kwargs = mock_confidential_client.call_args
        assert kwargs["azure_region"] == region


def test_requires_certificate():
    """the credential should raise ValueError when not given a certificate"""

    with pytest.raises(ValueError):
        CertificateCredential("tenant", "client-id")
    with pytest.raises(ValueError):
        CertificateCredential("tenant", "client-id", certificate_path=None)
    with pytest.raises(ValueError):
        CertificateCredential("tenant", "client-id", certificate_path="")
    with pytest.raises(ValueError):
        CertificateCredential("tenant", "client-id", certificate_data=None)
    with pytest.raises(ValueError):
        CertificateCredential("tenant", "client-id", certificate_path="", certificate_data=None)


@pytest.mark.parametrize("cert_path,cert_password", ALL_CERTS)
@pytest.mark.parametrize("send_certificate_chain", (True, False))
def test_request_body(cert_path, cert_password, send_certificate_chain):
    access_token = "***"
    authority = "authority.com"
    client_id = "client-id"
    expected_scope = "scope"
    tenant_id = "tenant"

    def mock_send(request, **kwargs):
        if not request.body:
            return get_discovery_response()

        assert request.body["grant_type"] == "client_credentials"
        assert request.body["scope"] == expected_scope

        with open(cert_path, "rb") as cert_file:
            validate_jwt(request, client_id, cert_file.read(), cert_password, expect_x5c=send_certificate_chain)

        return mock_response(json_payload=build_aad_response(access_token=access_token))

    cred = CertificateCredential(
        tenant_id,
        client_id,
        cert_path,
        password=cert_password,
        transport=Mock(send=mock_send),
        authority=authority,
        send_certificate_chain=send_certificate_chain,
    )
    token = cred.get_token(expected_scope)
    assert token.token == access_token

    # credential should also accept the certificate as bytes
    with open(cert_path, "rb") as f:
        cert_bytes = f.read()

    cred = CertificateCredential(
        tenant_id,
        client_id,
        certificate_data=cert_bytes,
        password=cert_password,
        transport=Mock(send=mock_send),
        authority=authority,
        send_certificate_chain=send_certificate_chain,
    )
    token = cred.get_token(expected_scope)
    assert token.token == access_token


def validate_jwt(request, client_id, cert_bytes, cert_password, expect_x5c=False):
    """Validate the request meets AAD's expectations for a client credential grant using a certificate, as documented
    at https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-certificate-credentials
    """

    try:
        cert = x509.load_pem_x509_certificate(cert_bytes, default_backend())
    except ValueError:
        if cert_password:
            cert_password = six.ensure_binary(cert_password)
        cert_bytes = load_pkcs12_certificate(cert_bytes, cert_password).pem_bytes
        cert = x509.load_pem_x509_certificate(cert_bytes, default_backend())

    # jwt is of the form 'header.payload.signature'; 'signature' is 'header.payload' signed with cert's private key
    jwt = six.ensure_str(request.body["client_assertion"])
    header, payload, signature = (urlsafeb64_decode(s) for s in jwt.split("."))
    signed_part = jwt[: jwt.rfind(".")]

    claims = json.loads(payload.decode("utf-8"))
    assert claims["aud"] == request.url
    assert claims["iss"] == claims["sub"] == client_id

    deserialized_header = json.loads(header.decode("utf-8"))
    assert deserialized_header["alg"] == "RS256"
    assert deserialized_header["typ"] == "JWT"
    if expect_x5c:
        # x5c should have all the certs in the file, in order, in PEM format minus headers and footers
        pem_lines = cert_bytes.decode("utf-8").splitlines()
        header = "-----BEGIN CERTIFICATE-----"
        assert len(deserialized_header["x5c"]) == pem_lines.count(header)

        # concatenate the PEM file's certs, removing headers and footers
        chain_start = pem_lines.index(header)
        pem_chain_content = "".join(line for line in pem_lines[chain_start:] if not line.startswith("-" * 5))
        assert "".join(deserialized_header["x5c"]) == pem_chain_content, "JWT's x5c claim contains unexpected content"
    else:
        assert "x5c" not in deserialized_header
    assert urlsafeb64_decode(deserialized_header["x5t"]) == cert.fingerprint(hashes.SHA1())  # nosec

    cert.public_key().verify(signature, signed_part.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())


@pytest.mark.parametrize("cert_path,cert_password", ALL_CERTS)
def test_token_cache(cert_path, cert_password):
    """the credential should optionally use a persistent cache, and default to an in memory cache"""

    with patch("azure.identity._internal.msal_credentials._load_persistent_cache") as load_persistent_cache:
        credential = CertificateCredential("tenant", "client-id", cert_path, password=cert_password)
        assert not load_persistent_cache.called
        assert isinstance(credential._cache, TokenCache)

        CertificateCredential(
            "tenant",
            "client-id",
            cert_path,
            password=cert_password,
            cache_persistence_options=TokenCachePersistenceOptions(),
        )
        assert load_persistent_cache.call_count == 1


@pytest.mark.parametrize("cert_path,cert_password", ALL_CERTS)
def test_persistent_cache_multiple_clients(cert_path, cert_password):
    """the credential shouldn't use tokens issued to other service principals"""

    access_token_a = "token a"
    access_token_b = "not " + access_token_a
    transport_a = msal_validating_transport(
        requests=[Request()], responses=[mock_response(json_payload=build_aad_response(access_token=access_token_a))]
    )
    transport_b = msal_validating_transport(
        requests=[Request()], responses=[mock_response(json_payload=build_aad_response(access_token=access_token_b))]
    )

    cache = TokenCache()
    with patch("azure.identity._internal.msal_credentials._load_persistent_cache") as mock_cache_loader:
        mock_cache_loader.return_value = Mock(wraps=cache)
        credential_a = CertificateCredential(
            "tenant",
            "client-a",
            cert_path,
            password=cert_password,
            transport=transport_a,
            cache_persistence_options=TokenCachePersistenceOptions(),
        )
        assert mock_cache_loader.call_count == 1, "credential should load the persistent cache"

        credential_b = CertificateCredential(
            "tenant",
            "client-b",
            cert_path,
            password=cert_password,
            transport=transport_b,
            cache_persistence_options=TokenCachePersistenceOptions(),
        )
        assert mock_cache_loader.call_count == 2, "credential should load the persistent cache"

    # A caches a token
    scope = "scope"
    token_a = credential_a.get_token(scope)
    assert token_a.token == access_token_a
    assert transport_a.send.call_count == 3  # two MSAL discovery requests, one token request

    # B should get a different token for the same scope
    token_b = credential_b.get_token(scope)
    assert token_b.token == access_token_b
    assert transport_b.send.call_count == 3

    assert len(cache.find(TokenCache.CredentialType.ACCESS_TOKEN)) == 2


def test_certificate_arguments():
    """The credential should raise ValueError for mutually exclusive arguments"""

    with pytest.raises(ValueError) as ex:
        CertificateCredential("tenant-id", "client-id", certificate_path="...", certificate_data="...")
    message = str(ex.value)
    assert "certificate_data" in message and "certificate_path" in message


@pytest.mark.parametrize("cert_path,cert_password", ALL_CERTS)
def test_multitenant_authentication(cert_path, cert_password):
    first_tenant = "first-tenant"
    first_token = "***"
    second_tenant = "second-tenant"
    second_token = first_token * 2

    def send(request, **_):
        parsed = urlparse(request.url)
        tenant = parsed.path.split("/")[1]
        assert tenant in (first_tenant, second_tenant, "common"), 'unexpected tenant "{}"'.format(tenant)
        if "/oauth2/v2.0/token" not in parsed.path:
            return get_discovery_response("https://{}/{}".format(parsed.netloc, tenant))

        token = first_token if tenant == first_tenant else second_token
        return mock_response(json_payload=build_aad_response(access_token=token))

    credential = CertificateCredential(
        first_tenant,
        "client-id",
        cert_path,
        password=cert_password,
        transport=Mock(send=send),
    )
    token = credential.get_token("scope")
    assert token.token == first_token

    token = credential.get_token("scope", tenant_id=first_tenant)
    assert token.token == first_token

    token = credential.get_token("scope", tenant_id=second_tenant)
    assert token.token == second_token

    # should still default to the first tenant
    token = credential.get_token("scope")
    assert token.token == first_token


@pytest.mark.parametrize("cert_path,cert_password", ALL_CERTS)
def test_multitenant_authentication_backcompat(cert_path, cert_password):
    expected_tenant = "expected-tenant"
    expected_token = "***"

    def send(request, **_):
        parsed = urlparse(request.url)
        if "/oauth2/v2.0/token" not in parsed.path:
            return get_discovery_response("https://{}/{}".format(parsed.netloc, expected_tenant))

        tenant = parsed.path.split("/")[1]
        token = expected_token if tenant == expected_tenant else expected_token * 2
        return mock_response(json_payload=build_aad_response(access_token=token))

    credential = CertificateCredential(
        expected_tenant, "client-id", cert_path, password=cert_password, transport=Mock(send=send)
    )

    token = credential.get_token("scope")
    assert token.token == expected_token

    # explicitly specifying the configured tenant is okay
    token = credential.get_token("scope", tenant_id=expected_tenant)
    assert token.token == expected_token

    token = credential.get_token("scope", tenant_id="un" + expected_tenant)
    assert token.token == expected_token
