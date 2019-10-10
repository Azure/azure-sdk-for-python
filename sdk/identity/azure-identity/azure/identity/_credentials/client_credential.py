# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from .._authn_client import AuthnClient
from .._base import ClientSecretCredentialBase, CertificateCredentialBase

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    # pylint:disable=unused-import,ungrouped-imports
    from typing import Any, Mapping
    from azure.core.credentials import AccessToken


class ClientSecretCredential(ClientSecretCredentialBase):
    """
    Authenticates as a service principal using a client ID and client secret.

    :param str client_id: the service principal's client ID
    :param str secret: one of the service principal's client secrets
    :param str tenant_id: ID of the service principal's tenant. Also called its 'directory' ID.

    Keyword arguments
        - **authority**: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com', the
          authority for Azure Public Cloud (which is the default). :class:`~azure.identity.KnownAuthorities` defines
          authorities for other clouds.
    """

    def __init__(self, client_id, secret, tenant_id, **kwargs):
        # type: (str, str, str, Mapping[str, Any]) -> None
        super(ClientSecretCredential, self).__init__(client_id, secret, tenant_id, **kwargs)
        self._client = AuthnClient(tenant=tenant_id, **kwargs)

    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (*str, **Any) -> AccessToken
        """
        Request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """
        token = self._client.get_cached_token(scopes)
        if not token:
            data = dict(self._form_data, scope=" ".join(scopes))
            token = self._client.request_token(scopes, form_data=data)
        return token


class CertificateCredential(CertificateCredentialBase):
    """
    Authenticates as a service principal using a certificate.

    :param str client_id: the service principal's client ID
    :param str tenant_id: ID of the service principal's tenant. Also called its 'directory' ID.
    :param str certificate_path: path to a PEM-encoded certificate file including the private key

    Keyword arguments
        - **authority**: Authority of an Azure Active Directory endpoint, for example 'login.microsoftonline.com', the
          authority for Azure Public Cloud (which is the default). :class:`~azure.identity.KnownAuthorities` defines
          authorities for other clouds.
    """

    def __init__(self, client_id, tenant_id, certificate_path, **kwargs):
        # type: (str, str, str, Mapping[str, Any]) -> None
        self._client = AuthnClient(tenant=tenant_id, **kwargs)
        super(CertificateCredential, self).__init__(client_id, tenant_id, certificate_path, **kwargs)

    def get_token(self, *scopes, **kwargs):  # pylint:disable=unused-argument
        # type: (*str, **Any) -> AccessToken
        """
        Request an access token for `scopes`.

        :param str scopes: desired scopes for the token
        :rtype: :class:`azure.core.credentials.AccessToken`
        :raises: :class:`azure.core.exceptions.ClientAuthenticationError`
        """
        token = self._client.get_cached_token(scopes)
        if not token:
            data = self._get_request_data(*scopes)
            token = self._client.request_token(scopes, form_data=data)
        return token
