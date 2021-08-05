# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import os
import time
from typing import TYPE_CHECKING

import msal

from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError

from .. import CredentialUnavailableError
from .._constants import EnvironmentVariables
from .._internal import get_default_authority, normalize_authority, resolve_tenant, validate_tenant_id
from .._internal.decorators import log_get_token
from .._internal.interactive import _build_auth_record
from .._internal.msal_client import MsalClient
from .._user_assertion import get_assertion

if TYPE_CHECKING:
    from typing import Any


class OnBehalfOfCredential(object):
    """Authenticates a service principal via the on-behalf-of flow.

    This flow is typically used by middle-tier services that authorize requests to other services with a delegated
    user identity. Because this is not an interactive authentication flow, an application using it must have admin
    consent for any delegated permissions before requesting tokens for them. See `Azure Active Directory documentation
    <https://docs.microsoft.com/azure/active-directory/develop/v2-oauth2-on-behalf-of-flow>`_ for a more detailed
    description of the on-behalf-of flow.

    Each token requested by this credential requires a user assertion from :class:`~azure.identity.UserAssertion`:

        .. literalinclude:: ../tests/test_obo.py
            :start-after: [START snippet]
            :end-before: [END snippet]
            :language: python
            :dedent: 8

    :param str tenant_id: ID of the service principal's tenant. Also called its "directory" ID.
    :param str client_id: the service principal's client ID
    :param str client_secret: one of the service principal's client secrets

    :keyword bool allow_multitenant_authentication: when True, enables the credential to acquire tokens from any tenant
        the application is registered in. When False, which is the default, the credential will acquire tokens only from
        the tenant specified by **tenant_id**.
    """

    def __init__(self, tenant_id, client_id, client_secret, **kwargs):
        # type: (str, str, str, **Any) -> None
        validate_tenant_id(tenant_id)
        self._resolve_tenant = functools.partial(
            resolve_tenant, tenant_id, kwargs.pop("allow_multitenant_authentication", False)
        )

        authority = kwargs.pop("authority", None)
        self._authority = normalize_authority(authority) if authority else get_default_authority()
        regional_authority = kwargs.pop(
            "regional_authority", os.environ.get(EnvironmentVariables.AZURE_REGIONAL_AUTHORITY_NAME)
        )

        self._client = MsalClient(**kwargs)

        # msal.ConfidentialClientApplication arguments which don't vary by user or tenant
        self._confidential_client_args = {
            "azure_region": regional_authority,
            "client_capabilities": None if "AZURE_IDENTITY_DISABLE_CP1" in os.environ else ["CP1"],
            "client_credential": client_secret,
            "client_id": client_id,
            "http_client": self._client,
        }

    @log_get_token("OnBehalfOfCredential")
    def get_token(self, *scopes, **kwargs):
        # type: (*str, **Any) -> AccessToken
        """Request an access token for `scopes`.

        This method is called automatically by Azure SDK clients.

        :param str scopes: desired scope for the access token

        :rtype: :class:`azure.core.credentials.AccessToken`
        """
        if not scopes:
            raise ValueError('"get_token" requires at least one scope')

        user_assertion = get_assertion()
        if not user_assertion:
            raise CredentialUnavailableError(
                (
                    "This credential requires a user assertion to acquire tokens. See "
                    + "https://aka.ms/azsdk/python/identity/docs#azure.identity.OnBehalfOfCredential for more details."
                )
            )

        # pylint:disable=protected-access
        tenant_id = self._resolve_tenant(**kwargs)
        if tenant_id not in user_assertion._client_applications:
            user_assertion._client_applications[tenant_id] = msal.ConfidentialClientApplication(
                authority=self._authority + "/" + tenant_id, **self._confidential_client_args
            )
        client_application = user_assertion._client_applications[tenant_id]

        request_time = int(time.time())
        result = None

        if user_assertion._record:
            # we already acquired a token with this assertion, so silent authentication may work
            for account in client_application.get_accounts(username=user_assertion._record.username):
                if account.get("home_account_id") != user_assertion._record.home_account_id:
                    continue
                result = client_application.acquire_token_silent_with_error(
                    list(scopes), account=account, claims_challenge=kwargs.get("claims")
                )
                if result and "access_token" in result and "expires_in" in result:
                    break

        if not result:
            result = client_application.acquire_token_on_behalf_of(
                user_assertion._assertion, list(scopes), claims_challenge=kwargs.get("claims")
            )
            try:
                user_assertion._record = _build_auth_record(result)
            except Exception:  # pylint:disable=broad-except
                pass

        if "access_token" not in result:
            message = "Authentication failed: {}".format(result.get("error_description") or result.get("error"))
            response = self._client.get_error_response(result)
            raise ClientAuthenticationError(message=message, response=response)

        return AccessToken(result["access_token"], request_time + int(result["expires_in"]))
