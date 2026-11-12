# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from typing import Any, Optional, Union
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from azure.core.exceptions import ClientAuthenticationError
from azure.core.credentials import AccessToken, AccessTokenInfo, TokenRequestOptions
from azure.core.rest import AsyncHttpResponse, HttpRequest, HttpResponse

from .client_assertion import ClientAssertionCredential
from .._constants import AzureAuthorityHosts, EnvironmentVariables
from .._exceptions import CredentialUnavailableError
from .._internal import get_default_authority, normalize_authority, validate_tenant_id
from .._internal.pipeline import build_pipeline

ACTIONS_ID_TOKEN_REQUEST_URL = "ACTIONS_ID_TOKEN_REQUEST_URL"
ACTIONS_ID_TOKEN_REQUEST_TOKEN = "ACTIONS_ID_TOKEN_REQUEST_TOKEN"

TROUBLESHOOTING_GUIDE = (
    "https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/identity/azure-identity/"
    "TROUBLESHOOTING.md#troubleshoot-githubactionscredential-authentication-issues"
)

_AUDIENCE_BY_AUTHORITY_HOST = {
    AzureAuthorityHosts.AZURE_PUBLIC_CLOUD: "api://AzureADTokenExchange",
    AzureAuthorityHosts.AZURE_CHINA: "api://AzureADTokenExchangeChina",
    AzureAuthorityHosts.AZURE_GOVERNMENT: "api://AzureADTokenExchangeUSGov",
}


def build_oidc_request(audience: str) -> HttpRequest:
    url = os.environ[ACTIONS_ID_TOKEN_REQUEST_URL]
    parts = urlsplit(url)
    query = [(name, value) for name, value in parse_qsl(parts.query, keep_blank_values=True) if name != "audience"]
    query.append(("audience", audience))
    url = urlunsplit(parts._replace(query=urlencode(query)))
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ[ACTIONS_ID_TOKEN_REQUEST_TOKEN]}",
    }
    return HttpRequest("GET", url, headers=headers)


def validate_env_vars() -> None:
    if ACTIONS_ID_TOKEN_REQUEST_URL not in os.environ:
        raise CredentialUnavailableError(
            message=f"Missing value for {ACTIONS_ID_TOKEN_REQUEST_URL} environment variable. "
            f"GitHubActionsCredential is intended for use in GitHub Actions where the "
            f"{ACTIONS_ID_TOKEN_REQUEST_URL} environment variable is set. Enable 'id-token: write' "
            f"in the workflow permissions. Please refer to the "
            f"troubleshooting guide at {TROUBLESHOOTING_GUIDE}"
        )
    if ACTIONS_ID_TOKEN_REQUEST_TOKEN not in os.environ:
        raise CredentialUnavailableError(f"Environment variable {ACTIONS_ID_TOKEN_REQUEST_TOKEN} is not set")


def derive_audience(authority: str) -> str:
    hostname = urlsplit(authority).hostname
    if hostname not in _AUDIENCE_BY_AUTHORITY_HOST:
        raise ValueError(f"Unsupported authority: {authority}")
    return _AUDIENCE_BY_AUTHORITY_HOST[hostname]


def _handle_oidc_response(response: Union[HttpResponse, AsyncHttpResponse]) -> str:
    if response.status_code != 200:
        raise ClientAuthenticationError("Unexpected response from OIDC token endpoint.", response=response)
    assertion = response.json().get("value")
    if not isinstance(assertion, str):
        raise ClientAuthenticationError("OIDC token not found in response.", response=response)
    return assertion


class GitHubActionsCredential:
    """Authenticates to Microsoft Entra ID using GitHub Actions workload identity federation.

    The workflow must grant ``id-token: write`` permission, and the identity must have a federated identity
    credential configured to trust the workflow.

    :keyword str tenant_id: ID of the application's Microsoft Entra tenant. Defaults to the
        ``AZURE_TENANT_ID`` environment variable.
    :keyword str client_id: ID of the Microsoft Entra application. Defaults to the
        ``AZURE_CLIENT_ID`` environment variable.
    :keyword str authority: Authority of a Microsoft Entra endpoint. Defaults to ``AZURE_AUTHORITY_HOST``,
        or Azure Public Cloud when unset. Azure Public, China, and US Government clouds are supported.
        The GitHub OIDC token audience is derived from this authority.
    :keyword cache_persistence_options: Configuration for persistent token caching. If unspecified,
        tokens are cached in memory.
    :paramtype cache_persistence_options: ~azure.identity.TokenCachePersistenceOptions
    :keyword List[str] additionally_allowed_tenants: Additional tenants for which the credential may acquire
        tokens. Use "*" to allow any tenant the application can access.
    :raises ValueError: Required identity configuration is missing, the tenant ID is invalid, or the authority
        is unsupported.

    .. admonition:: Example:

        .. literalinclude:: ../samples/credential_creation_code_snippets.py
            :start-after: [START create_github_actions_credential]
            :end-before: [END create_github_actions_credential]
            :language: python
            :dedent: 4
            :caption: Create a GitHubActionsCredential.
    """

    def __init__(
        self,
        *,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        tenant_id = tenant_id or os.environ.get(EnvironmentVariables.AZURE_TENANT_ID)
        client_id = client_id or os.environ.get(EnvironmentVariables.AZURE_CLIENT_ID)

        if not tenant_id:
            raise ValueError("Missing required argument: tenant_id")
        if not client_id:
            raise ValueError("Missing required argument: client_id")
        validate_tenant_id(tenant_id)

        authority = kwargs.pop("authority", None)
        resolved_authority = normalize_authority(authority) if authority else get_default_authority()
        self._audience = derive_audience(resolved_authority)

        self._client_assertion_credential = ClientAssertionCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            func=self._get_oidc_token,
            authority=resolved_authority,
            **kwargs,
        )
        self._pipeline = build_pipeline(**kwargs)

    def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        enable_cae: bool = False,
        **kwargs: Any,
    ) -> AccessToken:
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scopes for the access token. This method requires at least one scope.
            For more information about scopes, see
            https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword str claims: additional claims required in the token, such as those returned in a resource provider's
            claims challenge following an authorization failure.
        :keyword str tenant_id: optional tenant to include in the token request.
        :keyword bool enable_cae: indicates whether to enable Continuous Access Evaluation (CAE) for the requested
            token. Defaults to False.

        :return: An access token with the desired scopes.
        :rtype: ~azure.core.credentials.AccessToken
        :raises CredentialUnavailableError: the credential is unable to attempt authentication because it lacks
            required data, state, or platform support
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
            attribute gives a reason.
        """
        validate_env_vars()
        return self._client_assertion_credential.get_token(
            *scopes,
            claims=claims,
            tenant_id=tenant_id,
            enable_cae=enable_cae,
            **kwargs,
        )

    def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
        """Request an access token for `scopes` with additional token information.

        This method is called automatically by Azure SDK clients.

        :param str scopes: Desired scopes for the access token. Requires at least one scope.
        :keyword options: Token request options. Unknown options will be ignored.
        :paramtype options: ~azure.core.credentials.TokenRequestOptions
        :return: An access token with additional information.
        :rtype: ~azure.core.credentials.AccessTokenInfo
        :raises ~azure.identity.CredentialUnavailableError: GitHub Actions configuration is missing.
        :raises ~azure.core.exceptions.ClientAuthenticationError: Authentication failed.
        """
        validate_env_vars()
        return self._client_assertion_credential.get_token_info(*scopes, options=options)

    def _get_oidc_token(self) -> str:
        request = build_oidc_request(self._audience)
        response = self._pipeline.run(request)
        return _handle_oidc_response(response.http_response)

    def __enter__(self) -> "GitHubActionsCredential":
        self._client_assertion_credential.__enter__()
        self._pipeline.__enter__()
        return self

    def __exit__(self, *args: Any) -> None:
        self._client_assertion_credential.__exit__(*args)
        self._pipeline.__exit__(*args)

    def close(self) -> None:
        """Close the credential's transport session."""
        self.__exit__()
