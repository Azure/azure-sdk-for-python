# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import Any, Callable, Optional

from azure.core.credentials import AccessToken
from .._internal import AadClient, AsyncContextManager
from .._internal.get_token_mixin import GetTokenMixin


class ClientAssertionCredential(AsyncContextManager, GetTokenMixin):
    """Authenticates a service principal with a JWT assertion.

    This credential is for advanced scenarios. :class:`~azure.identity.ClientCertificateCredential` has a more
    convenient API for the most common assertion scenario, authenticating a service principal with a certificate.

    :param str tenant_id: ID of the principal's tenant. Also called its "directory" ID.
    :param str client_id: The principal's client ID
    :param func: A callable that returns a string assertion. The credential will call this every time it
        acquires a new token.
    :paramtype func: Callable[[], str]

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example
        "login.microsoftonline.com", the authority for Azure Public Cloud (which is the default).
        :class:`~azure.identity.AzureAuthorityHosts` defines authorities for other clouds.
    :keyword List[str] additionally_allowed_tenants: Specifies tenants in addition to the specified "tenant_id"
        for which the credential may acquire tokens. Add the wildcard value "*" to allow the credential to
        acquire tokens for any tenant the application can access.
    """

    def __init__(self, tenant_id: str, client_id: str, func: Callable[[], str], **kwargs) -> None:
        self._func = func
        self._client = AadClient(tenant_id, client_id, **kwargs)
        super().__init__(**kwargs)

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def close(self) -> None:
        """Close the credential's transport session."""
        await self._client.close()

    async def _acquire_token_silently(self, *scopes: str, **kwargs) -> Optional[AccessToken]:
        return self._client.get_cached_access_token(scopes, **kwargs)

    async def _request_token(self, *scopes: str, **kwargs) -> AccessToken:
        assertion = self._func()
        token = await self._client.obtain_token_by_jwt_assertion(scopes, assertion, **kwargs)
        return token
