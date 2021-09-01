# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import time
from typing import cast, TYPE_CHECKING

import six

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from .certificate import get_client_credential
from .._internal.decorators import wrap_exceptions
from .._internal.get_token_mixin import GetTokenMixin
from .._internal.interactive import _build_auth_record
from .._internal.msal_credentials import MsalCredential

if TYPE_CHECKING:
    from typing import Any, Dict, Optional, Union
    import msal
    from .. import AuthenticationRecord


class OnBehalfOfCredential(MsalCredential, GetTokenMixin):
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
    :type client_credential: str or bytes
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

    def __init__(self, tenant_id, client_id, client_credential, user_assertion, **kwargs):
        # type: (str, str, Union[bytes, str], str, **Any) -> None
        credential = cast("Union[Dict, str]", client_credential)
        if isinstance(client_credential, six.binary_type):
            try:
                credential = get_client_credential(
                    certificate_path=None, password=kwargs.pop("password", None), certificate_data=client_credential
                )
            except ValueError as ex:
                # client_credential isn't a valid cert. On 2.7 str == bytes and we ignore this exception because we
                # can't tell whether the caller intended to provide a cert. On Python 3 we can say the caller provided
                # either an invalid cert, or a client secret as bytes; both are errors.
                if six.PY3:
                    message = (
                        '"client_credential" should be either a client secret (a string)'
                        + " or the bytes of a certificate in PEM or PKCS12 format"
                    )
                    six.raise_from(ValueError(message), ex)

        super(OnBehalfOfCredential, self).__init__(client_id, credential, tenant_id=tenant_id, **kwargs)
        self._assertion = user_assertion
        self._auth_record = None  # type: Optional[AuthenticationRecord]

    @wrap_exceptions
    def _acquire_token_silently(self, *scopes, **kwargs):
        # type: (*str, **Any) -> Optional[AccessToken]
        if self._auth_record:
            claims = kwargs.get("claims")
            app = self._get_app(**kwargs)
            for account in app.get_accounts(username=self._auth_record.username):
                if account.get("home_account_id") != self._auth_record.home_account_id:
                    continue

                now = int(time.time())
                result = app.acquire_token_silent_with_error(list(scopes), account=account, claims_challenge=claims)
                if result and "access_token" in result and "expires_in" in result:
                    return AccessToken(result["access_token"], now + int(result["expires_in"]))

        return None

    @wrap_exceptions
    def _request_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        app = self._get_app(**kwargs)  # type: msal.ConfidentialClientApplication
        request_time = int(time.time())
        result = app.acquire_token_on_behalf_of(self._assertion, list(scopes), claims_challenge=kwargs.get("claims"))
        if "access_token" not in result or "expires_in" not in result:
            message = "Authentication failed: {}".format(result.get("error_description") or result.get("error"))
            response = self._client.get_error_response(result)
            raise ClientAuthenticationError(message=message, response=response)

        try:
            self._auth_record = _build_auth_record(result)
        except ClientAuthenticationError:
            pass  # non-fatal; we'll use the assertion again next time instead of a refresh token

        return AccessToken(result["access_token"], request_time + int(result["expires_in"]))
