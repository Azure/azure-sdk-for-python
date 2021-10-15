# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

import msal

from .._internal import AadClient, AsyncContextManager
from .._internal.get_token_mixin import GetTokenMixin
from ..._credentials.certificate import get_client_credential
from ..._internal import AadClientCertificate, validate_tenant_id
from ..._persistent_cache import _load_persistent_cache

if TYPE_CHECKING:
    from typing import Any, Optional
    from azure.core.credentials import AccessToken


class CertificateCredential(AsyncContextManager, GetTokenMixin):
    """Authenticates as a service principal using a certificate.

    The certificate must have an RSA private key, because this credential signs assertions using RS256. See
    `Azure Active Directory documentation
    <https://docs.microsoft.com/azure/active-directory/develop/active-directory-certificate-credentials#register-your-certificate-with-microsoft-identity-platform>`_
    for more information on configuring certificate authentication.

    :param str tenant_id: ID of the service principal's tenant. Also called its 'directory' ID.
    :param str client_id: the service principal's client ID
    :param str certificate_path: path to a PEM-encoded certificate file including the private key. If not provided,
          `certificate_data` is required.

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
          the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
          defines authorities for other clouds.
    :keyword bytes certificate_data: the bytes of a certificate in PEM format, including the private key
    :keyword password: The certificate's password. If a unicode string, it will be encoded as UTF-8. If the certificate
          requires a different encoding, pass appropriately encoded bytes instead.
    :paramtype password: str or bytes
    :keyword cache_persistence_options: configuration for persistent token caching. If unspecified, the credential
          will cache tokens in memory.
    :paramtype cache_persistence_options: ~azure.identity.TokenCachePersistenceOptions
    """

    def __init__(self, tenant_id, client_id, certificate_path=None, **kwargs):
        # type: (str, str, Optional[str], **Any) -> None
        validate_tenant_id(tenant_id)

        client_credential = get_client_credential(certificate_path, **kwargs)

        self._certificate = AadClientCertificate(
            client_credential["private_key"], password=client_credential.get("passphrase")
        )

        cache_options = kwargs.pop("cache_persistence_options", None)
        if cache_options:
            cache = _load_persistent_cache(cache_options)
        else:
            cache = msal.TokenCache()

        self._client = AadClient(tenant_id, client_id, cache=cache, **kwargs)
        self._client_id = client_id
        super().__init__()

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def close(self):
        """Close the credential's transport session."""

        await self._client.__aexit__()

    async def _acquire_token_silently(self, *scopes: str, **kwargs: "Any") -> "Optional[AccessToken]":
        return self._client.get_cached_access_token(scopes, **kwargs)

    async def _request_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        return await self._client.obtain_token_by_client_certificate(scopes, self._certificate, **kwargs)
