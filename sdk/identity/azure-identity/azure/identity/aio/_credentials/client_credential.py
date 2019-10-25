# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING

from .._authn_client import AsyncAuthnClient
from ..._base import ClientSecretCredentialBase, CertificateCredentialBase

if TYPE_CHECKING:
    from typing import Any, Mapping
    from azure.core.credentials import AccessToken


class ClientSecretCredential(ClientSecretCredentialBase):
    """Authenticates as a service principal using a client ID and client secret.

    :param str tenant_id: ID of the service principal's tenant. Also called its 'directory' ID.
    :param str client_id: the service principal's client ID
    :param str client_secret: one of the service principal's client secrets

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
          the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.KnownAuthorities`
          defines authorities for other clouds.
    """

    def __init__(self, tenant_id: str, client_id: str, client_secret: str, **kwargs: "Any") -> None:
        super(ClientSecretCredential, self).__init__(tenant_id, client_id, client_secret, **kwargs)
        self._client = AsyncAuthnClient(tenant=tenant_id, **kwargs)

    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":  # pylint:disable=unused-argument
        """Asynchronously request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.core.exceptions.ClientAuthenticationError:
        """
        token = self._client.get_cached_token(scopes)
        if not token:
            data = dict(self._form_data, scope=" ".join(scopes))
            token = await self._client.request_token(scopes, form_data=data)
        return token  # type: ignore


class CertificateCredential(CertificateCredentialBase):
    """Authenticates as a service principal using a certificate.

    :param str tenant_id: ID of the service principal's tenant. Also called its 'directory' ID.
    :param str client_id: the service principal's client ID
    :param str certificate_path: path to a PEM-encoded certificate file including the private key
      This file must not be password-protected.

    :keyword str authority: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com',
          the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.KnownAuthorities`
          defines authorities for other clouds.
    """

    def __init__(self, tenant_id: str, client_id: str, certificate_path: str, **kwargs: "Mapping[str, Any]") -> None:
        super(CertificateCredential, self).__init__(tenant_id, client_id, certificate_path, **kwargs)
        self._client = AsyncAuthnClient(tenant=tenant_id, **kwargs)

    async def get_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":  # pylint:disable=unused-argument
        """Asynchronously request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises ~azure.core.exceptions.ClientAuthenticationError:
        """
        token = self._client.get_cached_token(scopes)
        if not token:
            data = self._get_request_data(*scopes)
            token = await self._client.request_token(scopes, form_data=data)
        return token  # type: ignore
