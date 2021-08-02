# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import functools
import sys
from typing import TYPE_CHECKING

from azure.identity import CredentialUnavailableError
from .._internal import AadClient
from .._internal.decorators import log_get_token_async
from ..._internal import resolve_tenant, validate_tenant_id
from ..._user_assertion import get_assertion

if TYPE_CHECKING:
    from typing import Any
    from azure.core.credentials import AccessToken


# UserAssertion requires contextvars, added in 3.7, to operate correctly in an async context
if sys.version_info >= (3, 7):

    class OnBehalfOfCredential:
        """Authenticates a service principal via the on-behalf-of flow.

        This flow is typically used by middle-tier services that authorize requests to other services with a delegated
        user identity. Because this is not an interactive authentication flow, an application using it must have admin
        consent for any delegated permissions before requesting tokens for them. See `Azure Active Directory
        documentation <https://docs.microsoft.com/azure/active-directory/develop/v2-oauth2-on-behalf-of-flow>`_ for a
        more detailed description of the on-behalf-of flow.

        Each token requested by this credential requires a user assertion from :class:`~azure.identity.UserAssertion`:

            .. literalinclude:: ../tests/test_obo_async.py
                :start-after: [START snippet]
                :end-before: [END snippet]
                :language: python
                :dedent: 8

        :param str tenant_id: ID of the service principal's tenant. Also called its "directory" ID.
        :param str client_id: the service principal's client ID
        :param str client_secret: one of the service principal's client secrets

        :keyword bool allow_multitenant_authentication: when True, enables the credential to acquire tokens from any
            tenant the application is registered in. When False, which is the default, the credential will acquire
            tokens only from the tenant specified by **tenant_id**.
        """

        def __init__(self, tenant_id: str, client_id: str, client_secret: str, **kwargs: "Any") -> None:
            validate_tenant_id(tenant_id)
            self._resolve_tenant = functools.partial(
                resolve_tenant, tenant_id, kwargs.pop("allow_multitenant_authentication", False)
            )
            self._client_args = dict(kwargs, client_id=client_id)
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

            user_assertion = get_assertion()
            if not user_assertion:
                raise CredentialUnavailableError(
                    (
                        "This credential requires a user assertion to acquire tokens. See "
                        + "https://aka.ms/azsdk/python/identity/aio/docs#azure.identity.aio.OnBehalfOfCredential for "
                        + "more details."
                    )
                )

            # pylint:disable=protected-access
            tenant_id = self._resolve_tenant(**kwargs)
            if tenant_id not in user_assertion._async_clients:
                user_assertion._async_clients[tenant_id] = AadClient(tenant_id=tenant_id, **self._client_args)
            client = user_assertion._async_clients[tenant_id]

            token = client.get_cached_access_token(scopes)
            if not token:
                refresh_tokens = client.get_cached_refresh_tokens(scopes)
                if len(refresh_tokens) == 1:  # there should be only one
                    token = await client.obtain_token_by_refresh_token(scopes, refresh_tokens[0]["secret"], **kwargs)
                else:
                    token = await client.obtain_token_on_behalf_of(
                        scopes, self._secret, user_assertion._assertion, **kwargs
                    )

            return token
