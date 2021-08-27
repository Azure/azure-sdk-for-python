# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
from typing import TYPE_CHECKING

from azure.core.exceptions import ClientAuthenticationError

from .._internal import AadClient
from .._internal.decorators import log_get_token_async
from ..._internal import validate_tenant_id

if TYPE_CHECKING:
    from typing import Any
    from azure.core.credentials import AccessToken

_LOGGER = logging.getLogger(__name__)


class OnBehalfOfCredential:
    """Authenticates a service principal via the on-behalf-of flow.

    This flow is typically used by middle-tier services that authorize requests to other services with a delegated
    user identity. Because this is not an interactive authentication flow, an application using it must have admin
    consent for any delegated permissions before requesting tokens for them. See `Azure Active Directory documentation
    <https://docs.microsoft.com/azure/active-directory/develop/v2-oauth2-on-behalf-of-flow>`_ for a more detailed
    description of the on-behalf-of flow.

    :param str tenant_id: ID of the service principal's tenant. Also called its "directory" ID.
    :param str client_id: the service principal's client ID
    :param str client_secret: one of the service principal's client secrets
    :param str user_assertion: the access token the credential will use as the user assertion when requesting
        on-behalf-of tokens

    :keyword bool allow_multitenant_authentication: when True, enables the credential to acquire tokens from any tenant
        the application is registered in. When False, which is the default, the credential will acquire tokens only
        from the tenant specified by **tenant_id**.
    :keyword str authority: Authority of an Azure Active Directory endpoint, for example "login.microsoftonline.com",
        the authority for Azure Public Cloud (which is the default). :class:`~azure.identity.AzureAuthorityHosts`
        defines authorities for other clouds.
    """

    def __init__(
        self, tenant_id: str, client_id: str, client_secret: str, user_assertion: str, **kwargs: "Any"
    ) -> None:
        validate_tenant_id(tenant_id)

        # note AadClient handles "allow_multitenant_authentication", "authority", and any pipeline kwargs
        self._client = AadClient(tenant_id, client_id, **kwargs)
        self._assertion = user_assertion
        self._secret = client_secret

    @log_get_token_async
    async def get_token(self, *scopes: "Any", **kwargs: "Any") -> "AccessToken":
        """Asynchronously request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scope for the access token

        :rtype: :class:`azure.core.credentials.AccessToken`
        """
        if not scopes:
            raise ValueError('"get_token" requires at least one scope')

        token = self._client.get_cached_access_token(scopes, **kwargs)
        if not token:
            # Note we assume the cache has tokens for one user only. That's okay because each instance of this class is
            # locked to a single user (assertion). This assumption will become unsafe if this class allows applications
            # to change an instance's assertion.
            refresh_tokens = self._client.get_cached_refresh_tokens(scopes)
            if len(refresh_tokens) == 1:  # there should be only one
                try:
                    refresh_token = refresh_tokens[0]["secret"]
                    token = await self._client.obtain_token_by_refresh_token(scopes, refresh_token, **kwargs)
                except ClientAuthenticationError as ex:
                    _LOGGER.debug("silent authentication failed: %s", ex, exc_info=True)
                except (IndexError, KeyError, TypeError) as ex:
                    # this is purely defensive, hasn't been observed in practice
                    _LOGGER.debug("silent authentication failed due to malformed refresh token: %s", ex, exc_info=True)

            if not token:
                # we don't have a refresh token, or silent auth failed: acquire a new token from the assertion
                token = await self._client.obtain_token_on_behalf_of(scopes, self._secret, self._assertion, **kwargs)

        return token
