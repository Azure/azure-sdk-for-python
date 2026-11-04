# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from typing import Any, Optional

from azure.core.credentials import AccessToken, AccessTokenInfo, TokenRequestOptions

from .client_assertion import ClientAssertionCredential
from .._internal import AsyncContextManager
from ..._constants import EnvironmentVariables
from ..._credentials.github_actions import (
    _handle_oidc_response,
    build_oidc_request,
    derive_audience,
    validate_env_vars,
)
from ..._internal import get_default_authority, normalize_authority, validate_tenant_id
from ..._internal.pipeline import build_pipeline


class GitHubActionsCredential(AsyncContextManager):
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
            :start-after: [START create_github_actions_credential_async]
            :end-before: [END create_github_actions_credential_async]
            :language: python
            :dedent: 4
            :caption: Create an asynchronous GitHubActionsCredential.
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

    async def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        enable_cae: bool = False,
        **kwargs: Any,
    ) -> AccessToken:
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: Desired scopes for the access token. Requires at least one scope.
        :keyword str claims: Additional claims required in the token.
        :keyword str tenant_id: Optional tenant to include in the token request.
        :keyword bool enable_cae: Whether to enable Continuous Access Evaluation. Defaults to False.
        :return: An access token with the desired scopes.
        :rtype: ~azure.core.credentials.AccessToken
        :raises ~azure.identity.CredentialUnavailableError: GitHub Actions configuration is missing.
        :raises ~azure.core.exceptions.ClientAuthenticationError: Authentication failed.
        """
        validate_env_vars()
        return await self._client_assertion_credential.get_token(
            *scopes, claims=claims, tenant_id=tenant_id, enable_cae=enable_cae, **kwargs
        )

    async def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
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
        return await self._client_assertion_credential.get_token_info(*scopes, options=options)

    def _get_oidc_token(self) -> str:
        request = build_oidc_request(self._audience)
        response = self._pipeline.run(request)
        return _handle_oidc_response(response.http_response)

    async def __aenter__(self) -> "GitHubActionsCredential":
        await self._client_assertion_credential.__aenter__()
        self._pipeline.__enter__()
        return self

    async def close(self) -> None:
        """Close the credential's transport sessions."""
        await self._client_assertion_credential.close()
        self._pipeline.__exit__()
