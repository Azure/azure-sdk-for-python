# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
from typing import TYPE_CHECKING

from azure.core.exceptions import ClientAuthenticationError

from .._internal import AadClient, AsyncContextManager
from .._internal.get_token_mixin import GetTokenMixin
from ..._credentials.certificate import get_client_credential
from ..._internal import AadClientCertificate, validate_tenant_id

if TYPE_CHECKING:
    from typing import Any, Optional, Union
    from azure.core.credentials import AccessToken

_LOGGER = logging.getLogger(__name__)


class OnBehalfOfCredential(AsyncContextManager, GetTokenMixin):
    """Authenticates a service principal via the on-behalf-of flow.

    This flow is typically used by middle-tier services that authorize requests to other services with a delegated
    user identity. Because this is not an interactive authentication flow, an application using it must have admin
    consent for any delegated permissions before requesting tokens for them. See `Azure Active Directory documentation
    <https://docs.microsoft.com/azure/active-directory/develop/v2-oauth2-on-behalf-of-flow>`_ for a more detailed
    description of the on-behalf-of flow.

    :param str tenant_id: ID of the service principal's tenant. Also called its "directory" ID.
    :param str client_id: the service principal's client ID
    :param client_credential: a credential to authenticate the service principal, either one of its client secrets (a
        string) or the bytes of a certificate in PEM or PKCS12 format including the private key
    :paramtype client_credential: str or bytes
    :param str user_assertion: the access token the credential will use as the user assertion when requesting
        on-behalf-of tokens

    :keyword bool allow_multitenant_authentication: when True, enables the credential to acquire tokens from any tenant
        the application is registered in. When False, which is the default, the credential will acquire tokens only
        from the tenant specified by **tenant_id**.
    :keyword str authority: Authority of an Azure Active Directory endpoint, for example "login.microsoftonline.com",
        the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
        defines authorities for other clouds.
    :keyword password: a certificate password. Used only when **client_credential** is certificate bytes. If this value
        is a unicode string, it will be encoded as UTF-8. If the certificate requires a different encoding, pass
        appropriately encoded bytes instead.
    :paramtype password: str or bytes
    """

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_credential: "Union[bytes, str]",
        user_assertion: str,
        **kwargs: "Any"
    ) -> None:
        super().__init__()
        validate_tenant_id(tenant_id)

        if isinstance(client_credential, bytes):
            try:
                cert = get_client_credential(None, kwargs.pop("password", None), client_credential)
            except ValueError as ex:
                message = (
                    '"client_credential" should be either a client secret (a string)'
                    + " or the bytes of a certificate in PEM or PKCS12 format"
                )
                raise ValueError(message) from ex
            self._client_credential = AadClientCertificate(
                cert["private_key"], password=cert.get("passphrase")
            )  # type: Union[str, AadClientCertificate]
        else:
            self._client_credential = client_credential

        # note AadClient handles "allow_multitenant_authentication", "authority", and any pipeline kwargs
        self._client = AadClient(tenant_id, client_id, **kwargs)
        self._assertion = user_assertion

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def close(self):
        await self._client.close()

    async def _acquire_token_silently(self, *scopes: str, **kwargs: "Any") -> "Optional[AccessToken]":
        return self._client.get_cached_access_token(scopes, **kwargs)

    async def _request_token(self, *scopes: str, **kwargs: "Any") -> "AccessToken":
        # Note we assume the cache has tokens for one user only. That's okay because each instance of this class is
        # locked to a single user (assertion). This assumption will become unsafe if this class allows applications
        # to change an instance's assertion.
        refresh_tokens = self._client.get_cached_refresh_tokens(scopes)
        if len(refresh_tokens) == 1:  # there should be only one
            try:
                refresh_token = refresh_tokens[0]["secret"]
                return await self._client.obtain_token_by_refresh_token(scopes, refresh_token, **kwargs)
            except ClientAuthenticationError as ex:
                _LOGGER.debug("silent authentication failed: %s", ex, exc_info=True)
            except (IndexError, KeyError, TypeError) as ex:
                # this is purely defensive, hasn't been observed in practice
                _LOGGER.debug("silent authentication failed due to malformed refresh token: %s", ex, exc_info=True)

        # we don't have a refresh token, or silent auth failed: acquire a new token from the assertion
        return await self._client.obtain_token_on_behalf_of(scopes, self._client_credential, self._assertion, **kwargs)
