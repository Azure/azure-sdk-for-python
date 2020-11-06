# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import json
import os

from azure.core.pipeline.policies import ContentDecodePolicy, SansIOHTTPPolicy
from azure.identity import CertificateCredential
from azure.identity._constants import EnvironmentVariables
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
    validating_transport,
)

try:
    from unittest.mock import Mock, patch
except ImportError:  # python < 3.3
    from mock import Mock, patch  # type: ignore

CERT_PATH = os.path.join(os.path.dirname(__file__), "certificate.pem")
CERT_WITH_PASSWORD_PATH = os.path.join(os.path.dirname(__file__), "certificate-with-password.pem")
CERT_PASSWORD = "password"
BOTH_CERTS = (
    (CERT_PATH, None),
    (CERT_WITH_PASSWORD_PATH, CERT_PASSWORD),  # credential should accept passwords as str or bytes
    (CERT_WITH_PASSWORD_PATH, CERT_PASSWORD.encode("utf-8")),
)


def test_tenant_id_validation():
    """The credential should raise ValueError when given an invalid tenant_id"""

    valid_ids = {"c878a2ab-8ef4-413b-83a0-199afb84d7fb", "contoso.onmicrosoft.com", "organizations", "common"}
    for tenant in valid_ids:
        CertificateCredential(tenant, "client-id", CERT_PATH)

    invalid_ids = {"", "my tenant", "my_tenant", "/", "\\", '"my-tenant"', "'my-tenant'"}
    for tenant in invalid_ids:
        with pytest.raises(ValueError):
            CertificateCredential(tenant, "client-id", CERT_PATH)


def test_no_scopes():
    """The credential should raise ValueError when get_token is called with no scopes"""

    credential = CertificateCredential("tenant-id", "client-id", CERT_PATH)
    with pytest.raises(ValueError):
        credential.get_token()


def test_policies_configurable():
    policy = Mock(spec_set=SansIOHTTPPolicy, on_request=Mock())

    transport = msal_validating_transport(
        requests=[Request()], responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = CertificateCredential(
        "tenant-id", "client-id", CERT_PATH, policies=[ContentDecodePolicy(), policy], transport=transport
    )

    credential.get_token("scope")

    assert policy.on_request.called


def test_user_agent():
    transport = msal_validating_transport(
        requests=[Request(required_headers={"User-Agent": USER_AGENT})],
        responses=[mock_response(json_payload=build_aad_response(access_token="**"))],
    )

    credential = CertificateCredential("tenant-id", "client-id", CERT_PATH, transport=transport)

    credential.get_token("scope")


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

    credential = CertificateCredential(tenant_id, "client-id", CERT_PATH, authority=authority)
    with patch("msal.ConfidentialClientApplication", mock_ctor):
        # must call get_token because the credential constructs the MSAL application lazily
        credential.get_token("scope")

    assert mock_ctor.call_count == 1
    _, kwargs = mock_ctor.call_args
    assert kwargs["authority"] == expected_authority
    mock_ctor.reset_mock()

    # authority can be configured via environment variable
    with patch.dict("os.environ", {EnvironmentVariables.AZURE_AUTHORITY_HOST: authority}, clear=True):
        credential = CertificateCredential(tenant_id, "client-id", CERT_PATH, authority=authority)
    with patch("msal.ConfidentialClientApplication", mock_ctor):
        credential.get_token("scope")

    assert mock_ctor.call_count == 1
    _, kwargs = mock_ctor.call_args
    assert kwargs["authority"] == expected_authority


@pytest.mark.parametrize("cert_path,cert_password", BOTH_CERTS)
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
            validate_jwt(request, client_id, cert_file.read(), expect_x5c=send_certificate_chain)

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


def validate_jwt(request, client_id, pem_bytes, expect_x5c=False):
    """Validate the request meets AAD's expectations for a client credential grant using a certificate, as documented
    at https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-certificate-credentials
    """

    cert = x509.load_pem_x509_certificate(pem_bytes, default_backend())

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
        # x5c should have all the certs in the PEM file, in order, minus headers and footers
        pem_lines = pem_bytes.decode("utf-8").splitlines()
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


@pytest.mark.parametrize("cert_path,cert_password", BOTH_CERTS)
def test_enable_persistent_cache(cert_path, cert_password):
    """the credential should use the persistent cache only when given _enable_persistent_cache=True"""

    persistent_cache = "azure.identity._internal.persistent_cache"
    required_arguments = ("tenant-id", "client-id", cert_path)

    # credential should default to an in memory cache
    raise_when_called = Mock(side_effect=Exception("credential shouldn't attempt to load a persistent cache"))
    with patch(persistent_cache + "._load_persistent_cache", raise_when_called):
        CertificateCredential(*required_arguments, password=cert_password)

        # allowing an unencrypted cache doesn't count as opting in to the persistent cache
        CertificateCredential(*required_arguments, password=cert_password, _allow_unencrypted_cache=True)

    # keyword argument opts in to persistent cache
    with patch(persistent_cache + ".msal_extensions") as mock_extensions:
        CertificateCredential(*required_arguments, password=cert_password, _enable_persistent_cache=True)
    assert mock_extensions.PersistedTokenCache.call_count == 1

    # opting in on an unsupported platform raises an exception
    with patch(persistent_cache + ".sys.platform", "commodore64"):
        with pytest.raises(NotImplementedError):
            CertificateCredential(*required_arguments, password=cert_password, _enable_persistent_cache=True)
        with pytest.raises(NotImplementedError):
            CertificateCredential(
                *required_arguments, password=cert_password, _enable_persistent_cache=True, _allow_unencrypted_cache=True
            )


@patch("azure.identity._internal.persistent_cache.sys.platform", "linux2")
@patch("azure.identity._internal.persistent_cache.msal_extensions")
@pytest.mark.parametrize("cert_path,cert_password", BOTH_CERTS)
def test_persistent_cache_linux(mock_extensions, cert_path, cert_password):
    """The credential should use an unencrypted cache when encryption is unavailable and the user explicitly opts in.

    This test was written when Linux was the only platform on which encryption may not be available.
    """

    required_arguments = ("tenant-id", "client-id", cert_path)

    # the credential should prefer an encrypted cache even when the user allows an unencrypted one
    CertificateCredential(
        *required_arguments, password=cert_password, _enable_persistent_cache=True, _allow_unencrypted_cache=True
    )
    assert mock_extensions.PersistedTokenCache.called_with(mock_extensions.LibsecretPersistence)
    mock_extensions.PersistedTokenCache.reset_mock()

    # (when LibsecretPersistence's dependencies aren't available, constructing it raises ImportError)
    mock_extensions.LibsecretPersistence = Mock(side_effect=ImportError)

    # encryption unavailable, no opt in to unencrypted cache -> credential should raise
    with pytest.raises(ValueError):
        CertificateCredential(*required_arguments, password=cert_password, _enable_persistent_cache=True)

    CertificateCredential(
        *required_arguments, password=cert_password, _enable_persistent_cache=True, _allow_unencrypted_cache=True
    )
    assert mock_extensions.PersistedTokenCache.called_with(mock_extensions.FilePersistence)


@pytest.mark.parametrize("cert_path,cert_password", BOTH_CERTS)
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
    with patch("azure.identity._internal.persistent_cache._load_persistent_cache") as mock_cache_loader:
        mock_cache_loader.return_value = Mock(wraps=cache)
        credential_a = CertificateCredential(
            "tenant", "client-a", cert_path, password=cert_password, _enable_persistent_cache=True, transport=transport_a
        )
        assert mock_cache_loader.call_count == 1, "credential should load the persistent cache"
        credential_b = CertificateCredential(
            "tenant", "client-b", cert_path, password=cert_password, _enable_persistent_cache=True, transport=transport_b
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
