# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Optional, cast
from azure.core.credentials import AccessToken, AccessTokenInfo, TokenRequestOptions
from ..._internal.aad_client import AadClientBase
from ... import CredentialUnavailableError
from ..._constants import DEVELOPER_SIGN_ON_CLIENT_ID
from ..._internal.shared_token_cache import NO_TOKEN, SharedTokenCacheBase
from .._internal import AsyncContextManager
from .._internal.aad_client import AadClient
from .._internal.decorators import log_get_token_async


class SharedTokenCacheCredential(SharedTokenCacheBase, AsyncContextManager):
    """Authenticates using tokens in the local cache shared between Microsoft applications.

    :param str username:
        Username (typically an email address) of the user to authenticate as. This is required because the local cache
        may contain tokens for multiple identities.

    :keyword str authority: Authority of a Microsoft Entra endpoint, for example 'login.microsoftonline.com',
        the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
        defines authorities for other clouds.
    :keyword str tenant_id: a Microsoft Entra tenant ID. Used to select an account when the cache contains
        tokens for multiple identities.
    :keyword cache_persistence_options: configuration for persistent token caching. If not provided, the credential
        will use the persistent cache shared by Microsoft development applications
    :paramtype cache_persistence_options: ~azure.identity.TokenCachePersistenceOptions
    """

    async def __aenter__(self) -> "SharedTokenCacheCredential":
        if self._client:
            await self._client.__aenter__()  # type: ignore
        return self

    async def close(self) -> None:
        """Close the credential's transport session."""

        if self._client:
            await self._client.__aexit__()  # type: ignore

    @log_get_token_async
    async def get_token(
        self,
        *scopes: str,
        claims: Optional[str] = None,
        tenant_id: Optional[str] = None,
        enable_cae: bool = False,
        **kwargs: Any,
    ) -> AccessToken:
        """Get an access token for `scopes` from the shared cache.

        If no access token is cached, attempt to acquire one using a cached refresh token.

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
        :raises ~azure.identity.CredentialUnavailableError: the cache is unavailable or contains insufficient user
            information
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
          attribute gives a reason. Any error response from Microsoft Entra ID is available as the error's
          ``response`` attribute.
        """
        options: TokenRequestOptions = {}
        if claims:
            options["claims"] = claims
        if tenant_id:
            options["tenant_id"] = tenant_id
        options["enable_cae"] = enable_cae

        token_info = await self._get_token_base(*scopes, options=options, base_method_name="get_token", **kwargs)
        return AccessToken(token_info.token, token_info.expires_on)

    @log_get_token_async
    async def get_token_info(self, *scopes: str, options: Optional[TokenRequestOptions] = None) -> AccessTokenInfo:
        """Get an access token for `scopes` from the shared cache.

        If no access token is cached, attempt to acquire one using a cached refresh token.

        This is an alternative to `get_token` to enable certain scenarios that require additional properties
        on the token. This method is called automatically by Azure SDK clients.

        :param str scopes: desired scope for the access token. This method requires at least one scope.
            For more information about scopes, see https://learn.microsoft.com/entra/identity-platform/scopes-oidc.
        :keyword options: A dictionary of options for the token request. Unknown options will be ignored. Optional.
        :paramtype options: ~azure.core.credentials.TokenRequestOptions

        :rtype: ~azure.core.credentials.AccessTokenInfo
        :return: An AccessTokenInfo instance containing information about the token.
        :raises ~azure.identity.CredentialUnavailableError: the cache is unavailable or contains insufficient user
            information
        :raises ~azure.core.exceptions.ClientAuthenticationError: authentication failed. The error's ``message``
          attribute gives a reason. Any error response from Microsoft Entra ID is available as the error's
          ``response`` attribute.
        """
        return await self._get_token_base(*scopes, options=options, base_method_name="get_token_info")

    async def _get_token_base(
        self,
        *scopes: str,
        options: Optional[TokenRequestOptions] = None,
        base_method_name: str = "get_token_info",
        **kwargs: Any,
    ) -> AccessTokenInfo:
        if not scopes:
            raise ValueError(f"'{base_method_name}' requires at least one scope")

        if not self._client_initialized:
            self._initialize_client()

        options = options or {}
        claims = options.get("claims")
        tenant_id = options.get("tenant_id")
        is_cae = options.get("enable_cae", False)

        token_cache = self._cae_cache if is_cae else self._cache

        # Try to load the cache if it is None.
        if not token_cache:
            token_cache = self._initialize_cache(is_cae=is_cae)

            # If the cache is still None, raise an error.
            if not token_cache:
                raise CredentialUnavailableError(message="Shared token cache unavailable")

        account = self._get_account(self._username, self._tenant_id, is_cae=is_cae)

        token = self._get_cached_access_token(scopes, account, is_cae=is_cae)
        if token:
            return token

        # try each refresh token, returning the first access token acquired
        for refresh_token in self._get_refresh_tokens(account, is_cae=is_cae):
            token = await cast(AadClient, self._client).obtain_token_by_refresh_token(
                scopes, refresh_token, claims=claims, tenant_id=tenant_id, enable_cae=is_cae, **kwargs
            )
            return token

        raise CredentialUnavailableError(message=NO_TOKEN.format(account.get("username")))

    def _get_auth_client(self, **kwargs: Any) -> AadClientBase:
        return AadClient(client_id=DEVELOPER_SIGN_ON_CLIENT_ID, **kwargs)
