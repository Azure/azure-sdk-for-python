# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from unittest.mock import MagicMock, Mock, patch
from urllib.parse import parse_qsl, urlsplit

import pytest
from azure.core.credentials import AccessToken, AccessTokenInfo
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import (
    AzureAuthorityHosts,
    ChainedTokenCredential,
    CredentialUnavailableError,
    GitHubActionsCredential,
)
from azure.identity.aio import GitHubActionsCredential as AsyncGitHubActionsCredential
from azure.identity._credentials.github_actions import (
    ACTIONS_ID_TOKEN_REQUEST_TOKEN,
    ACTIONS_ID_TOKEN_REQUEST_URL,
    build_oidc_request,
    derive_audience,
)
from azure.identity._internal.aad_client_base import JWT_BEARER_ASSERTION

from helpers import GET_TOKEN_METHODS, build_aad_response, mock_response

ENVIRONMENT = {
    "AZURE_TENANT_ID": "environment-tenant",
    "AZURE_CLIENT_ID": "environment-client",
    ACTIONS_ID_TOKEN_REQUEST_URL: "https://example.test/oidc?job=123",
    ACTIONS_ID_TOKEN_REQUEST_TOKEN: "request-token",
}


@pytest.fixture(autouse=True)
def github_environment():
    with patch.dict(os.environ, ENVIRONMENT, clear=True):
        yield


@pytest.mark.parametrize("credential_class", [GitHubActionsCredential, AsyncGitHubActionsCredential])
@pytest.mark.parametrize("explicit", [False, True])
def test_initialize(credential_class, explicit):
    kwargs = {"tenant_id": "explicit-tenant", "client_id": "explicit-client"} if explicit else {}
    credential = credential_class(**kwargs)
    client = credential._client_assertion_credential._client
    assert client._tenant_id == ("explicit-tenant" if explicit else "environment-tenant")
    assert client._client_id == ("explicit-client" if explicit else "environment-client")
    assert client._authority == "https://login.microsoftonline.com"
    assert credential._audience == "api://AzureADTokenExchange"
    assert credential._client_assertion_credential._func.__self__ is credential


@pytest.mark.parametrize("credential_class", [GitHubActionsCredential, AsyncGitHubActionsCredential])
@pytest.mark.parametrize("missing", ["tenant_id", "client_id"])
def test_missing_identity(credential_class, missing):
    os.environ.pop("AZURE_" + missing.upper())
    with pytest.raises(ValueError, match=missing):
        credential_class()


@pytest.mark.parametrize("credential_class", [GitHubActionsCredential, AsyncGitHubActionsCredential])
def test_invalid_tenant(credential_class):
    with pytest.raises(ValueError):
        credential_class(tenant_id="invalid tenant")


@pytest.mark.parametrize("credential_class", [GitHubActionsCredential, AsyncGitHubActionsCredential])
@pytest.mark.parametrize(
    "authority,audience",
    [
        (AzureAuthorityHosts.AZURE_PUBLIC_CLOUD, "api://AzureADTokenExchange"),
        (AzureAuthorityHosts.AZURE_CHINA, "api://AzureADTokenExchangeChina"),
        (AzureAuthorityHosts.AZURE_GOVERNMENT, "api://AzureADTokenExchangeUSGov"),
    ],
)
@pytest.mark.parametrize("explicit", [False, True])
def test_authority(credential_class, authority, audience, explicit):
    os.environ["AZURE_AUTHORITY_HOST"] = AzureAuthorityHosts.AZURE_CHINA if explicit else authority
    kwargs = {"authority": authority} if explicit else {}
    credential = credential_class(**kwargs)
    assert credential._audience == audience
    assert credential._client_assertion_credential._client._authority == "https://" + authority


def test_derive_audience_normalized_url():
    assert derive_audience("https://LOGIN.MICROSOFTONLINE.COM/") == "api://AzureADTokenExchange"


@pytest.mark.parametrize("credential_class", [GitHubActionsCredential, AsyncGitHubActionsCredential])
def test_unsupported_authority(credential_class):
    with pytest.raises(ValueError, match="Unsupported authority"):
        credential_class(authority="https://example.test")


@pytest.mark.parametrize("query", ["", "?job=123", "?job=123&flag=&job=456&audience=old&audience=duplicate"])
def test_build_oidc_request(query):
    os.environ[ACTIONS_ID_TOKEN_REQUEST_URL] = "https://example.test/oidc" + query
    audience = "api://AzureADTokenExchange"
    request = build_oidc_request(audience)
    assert request.method == "GET"
    assert request.headers["Authorization"] == "Bearer request-token"
    parsed = urlsplit(request.url)
    assert parsed.scheme == "https"
    assert parsed.netloc == "example.test"
    assert parsed.path == "/oidc"
    expected = [
        (key, value) for key, value in parse_qsl(query.lstrip("?"), keep_blank_values=True) if key != "audience"
    ]
    assert parse_qsl(parsed.query, keep_blank_values=True) == expected + [("audience", audience)]


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
@pytest.mark.parametrize("missing", [ACTIONS_ID_TOKEN_REQUEST_URL, ACTIONS_ID_TOKEN_REQUEST_TOKEN])
def test_missing_github_environment(get_token_method, missing):
    credential = GitHubActionsCredential()
    os.environ.pop(missing)
    credential._client_assertion_credential = Mock()
    with pytest.raises(CredentialUnavailableError, match=missing):
        getattr(credential, get_token_method)("scope")
    assert not getattr(credential._client_assertion_credential, get_token_method).called


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_delegation(get_token_method):
    credential = GitHubActionsCredential()
    credential._client_assertion_credential = Mock()
    expected = (
        AccessToken("access-token", 123) if get_token_method == "get_token" else AccessTokenInfo("access-token", 123)
    )
    method = getattr(credential._client_assertion_credential, get_token_method)
    method.return_value = expected
    options = {"claims": "claims", "tenant_id": "other-tenant", "enable_cae": True}
    kwargs = options if get_token_method == "get_token" else {"options": options}
    assert getattr(credential, get_token_method)("scope", **kwargs) is expected
    method.assert_called_once_with("scope", **kwargs)


@pytest.mark.parametrize("status,payload", [(400, {}), (200, {}), (200, {"value": 123})])
def test_oidc_error(status, payload):
    credential = GitHubActionsCredential()
    response = Mock(status_code=status, headers={}, json=Mock(return_value=payload))
    credential._pipeline = Mock()
    credential._pipeline.run.return_value.http_response = response
    with pytest.raises(ClientAuthenticationError) as error:
        credential._get_oidc_token()
    assert error.value.response is response


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_token_exchange_and_cache(get_token_method):
    def send(request, **kwargs):
        assert request.url == "https://login.microsoftonline.com/environment-tenant/oauth2/v2.0/token"
        assert request.data["client_id"] == "environment-client"
        assert request.data["client_assertion"] == "github-assertion"
        assert request.data["client_assertion_type"] == JWT_BEARER_ASSERTION
        assert request.data["scope"] == "scope"
        return mock_response(json_payload=build_aad_response(access_token="azure-token"))

    transport = Mock(send=Mock(side_effect=send))
    credential = GitHubActionsCredential(transport=transport)
    credential._pipeline = Mock()
    credential._pipeline.run.return_value.http_response = Mock(
        status_code=200, json=Mock(return_value={"value": "github-assertion"})
    )
    for _ in range(2):
        assert getattr(credential, get_token_method)("scope").token == "azure-token"
    transport.send.assert_called_once()
    credential._pipeline.run.assert_called_once()
    request = credential._pipeline.run.call_args.args[0]
    assert dict(parse_qsl(urlsplit(request.url).query))["audience"] == credential._audience


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_github_request_through_pipeline(get_token_method):
    def send(request, **kwargs):
        if request.method == "GET":
            assert request.headers["Authorization"] == "Bearer request-token"
            assert dict(parse_qsl(urlsplit(request.url).query)) == {
                "job": "123",
                "audience": "api://AzureADTokenExchange",
            }
            response = mock_response(json_payload={"value": "github-assertion"})
            response.json = Mock(return_value={"value": "github-assertion"})
            return response
        assert request.data["client_assertion"] == "github-assertion"
        return mock_response(json_payload=build_aad_response(access_token="azure-token"))

    transport = MagicMock(send=Mock(side_effect=send))
    with GitHubActionsCredential(transport=transport) as credential:
        assert getattr(credential, get_token_method)("scope").token == "azure-token"
    assert transport.send.call_count == 2


@pytest.mark.parametrize("get_token_method", GET_TOKEN_METHODS)
def test_chain_skips_unavailable(get_token_method):
    os.environ.pop(ACTIONS_ID_TOKEN_REQUEST_URL)
    fallback = Mock()
    chain = ChainedTokenCredential(GitHubActionsCredential(), fallback)
    getattr(chain, get_token_method)("scope")
    assert getattr(fallback, get_token_method).called


def test_context_manager():
    credential = GitHubActionsCredential()
    credential._client_assertion_credential = Mock(__enter__=Mock(), __exit__=Mock())
    credential._pipeline = Mock(__enter__=Mock(), __exit__=Mock())
    with credential as entered:
        assert entered is credential
        credential._client_assertion_credential.__enter__.assert_called_once()
        credential._pipeline.__enter__.assert_called_once()
    credential._client_assertion_credential.__exit__.assert_called_once()
    credential._pipeline.__exit__.assert_called_once()


def test_close():
    credential = GitHubActionsCredential()
    credential._client_assertion_credential = Mock(__exit__=Mock())
    credential._pipeline = Mock(__exit__=Mock())
    credential.close()
    credential._client_assertion_credential.__exit__.assert_called_once()
    credential._pipeline.__exit__.assert_called_once()
