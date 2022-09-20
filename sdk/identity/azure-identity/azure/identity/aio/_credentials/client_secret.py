# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING, TypeVar

import msal

from .._internal import AadClient, AsyncContextManager
from .._internal.get_token_mixin import GetTokenMixin
from ..._internal import validate_tenant_id
from ..._persistent_cache import _load_persistent_cache

if TYPE_CHECKING:
    from typing import Any, Optional, List
    from azure.core.credentials import AccessToken

T = TypeVar("T", bound="ClientSecretCredential")


class ClientSecretCredential(AsyncContextManager, GetTokenMixin):
    """Authenticates as a service principal using a client secret.

    :param str tenant_id: ID of the service principal's tenant. Also called its 'directory' ID.
    :param str client_id: The service principal's client ID
    :param str client_secret: One of the service principal's client secrets

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
          the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
          defines authorities for other clouds.
    :keyword cache_persistence_options: Configuration for persistent token caching. If unspecified, the credential
          will cache tokens in memory.
    :paramtype cache_persistence_options: ~azure.identity.TokenCachePersistenceOptions
    :keyword List[str] additionally_allowed_tenants: Specifies tenants in addition to the specified "tenant_id"
        for which the credential may acquire tokens. Add the wildcard value "*" to allow the credential to
        acquire tokens for any tenant the application can access.
    """

    def __init__(self, tenant_id: str, client_id: str, client_secret: str, **kwargs: "Any") -> None:
        if not client_id:
            raise ValueError("client_id should be the id of an Azure Active Directory application")
        if not client_secret:
            raise ValueError("secret should be an Azure Active Directory application's client secret")
        if not tenant_id:
            raise ValueError(
                "tenant_id should be an Azure Active Directory tenant's id (also called its 'directory id')"
            )
        validate_tenant_id(tenant_id)

        cache_options = kwargs.pop("cache_persistence_options", None)
        if cache_options:
            cache = _load_persistent_cache(cache_options)
        else:
            cache = msal.TokenCache()

        self._client = AadClient(tenant_id, client_id, cache=cache, **kwargs)
        self._client_id = client_id
        self._secret = client_secret
        super().__init__()

    async def __aenter__(self:T) -> T:
        await self._client.__aenter__()
        return self

    async def close(self):
        """Close the credential's transport session."""

        await self._client.__aexit__()

    async def _acquire_token_silently(self, *scopes: str, **kwargs: "Any") -> "Optional[AccessToken]":
        return self._client.get_cached_access_token(scopes, **kwargs)

    async def _request_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        return await self._client.obtain_token_by_client_secret(scopes, self._secret, **kwargs)
