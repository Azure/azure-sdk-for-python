# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import TYPE_CHECKING

import msal

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from .._internal.get_token_mixin import GetTokenMixin
from .._internal.msal_credentials import MsalCredential

if TYPE_CHECKING:
    from typing import Any, Optional


class OnBehalfOfCredential(MsalCredential, GetTokenMixin):
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

    def __init__(self, tenant_id, client_id, client_secret, user_assertion, **kwargs):
        # type: (str, str, str, str, **Any) -> None
        super(OnBehalfOfCredential, self).__init__(client_id, client_secret, tenant_id=tenant_id, **kwargs)
        self._assertion = user_assertion

    def _acquire_token_silently(self, *scopes, **kwargs):
        # type: (*str, **Any) -> Optional[AccessToken]
        app = self._get_app(**kwargs)  # type: msal.ConfidentialClientApplication
        request_time = int(time.time())
        result = app.acquire_token_on_behalf_of(self._assertion, list(scopes), claims_challenge=kwargs.get("claims"))
        if result and "access_token" in result and "expires_in" in result:
            return AccessToken(result["access_token"], request_time + int(result["expires_in"]))
        return None

    def _request_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        app = self._get_app(**kwargs)  # type: msal.ConfidentialClientApplication
        request_time = int(time.time())
        result = app.acquire_token_on_behalf_of(self._assertion, list(scopes), claims_challenge=kwargs.get("claims"))
        if "access_token" not in result:
            message = "Authentication failed: {}".format(result.get("error_description") or result.get("error"))
            response = self._client.get_error_response(result)
            raise ClientAuthenticationError(message=message, response=response)

        return AccessToken(result["access_token"], request_time + int(result["expires_in"]))
