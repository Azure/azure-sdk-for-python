# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from typing import TYPE_CHECKING, Any, List, Union, Tuple

from azure.core.tracing.decorator_async import distributed_trace_async
from azure.core.credentials import AccessToken

from .._generated.aio._communication_identity_client\
    import CommunicationIdentityClient as CommunicationIdentityClientGen
from .._shared.utils import parse_connection_str, get_authentication_policy
from .._shared.models import CommunicationUserIdentifier
from .._version import SDK_MONIKER
from .._api_versions import DEFAULT_VERSION
from .._utils import convert_timedelta_to_mins

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential
    from .._generated.models import CommunicationTokenScope


class CommunicationIdentityClient:
    """Azure Communication Services Identity client.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param AsyncTokenCredential credential:
        The AsyncTokenCredential we use to authenticate against the service.
    :keyword api_version: Azure Communication Identity API version.
        Default value is "2022-06-01". Note that overriding this default value may result in unsupported behavior.
    :paramtype api_version: str

    .. admonition:: Example:

        .. literalinclude:: ../../samples/identity_samples_async.py
            :language: python
            :dedent: 8
    """

    def __init__(
            self,
            endpoint: str,
            credential: 'AsyncTokenCredential',
            **kwargs
        ) -> None:
        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Account URL must be a string.")

        if not credential:
            raise ValueError(
                "You need to provide account shared key to authenticate.")

        self._endpoint = endpoint
        self._api_version = kwargs.pop("api_version", DEFAULT_VERSION)
        self._identity_service_client = CommunicationIdentityClientGen(
            self._endpoint,
            api_version=self._api_version,
            authentication_policy=get_authentication_policy(endpoint, credential, decode_url=True, is_async=True),
            sdk_moniker=SDK_MONIKER,
            **kwargs)

    @classmethod
    def from_connection_string(cls, conn_str: str, **kwargs) -> 'CommunicationIdentityClient':
        """Create CommunicationIdentityClient from a Connection String.

        :param str conn_str:
            A connection string to an Azure Communication Service resource.
        :returns: Instance of CommunicationIdentityClient.
        :rtype: ~azure.communication.identity.aio.CommunicationIdentityClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/identity_samples.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Creating the CommunicationIdentityClient from a connection string.
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    @distributed_trace_async
    async def create_user(self, **kwargs) -> 'CommunicationUserIdentifier':
        """create a single Communication user

        :return: CommunicationUserIdentifier
        :rtype: ~azure.communication.identity.CommunicationUserIdentifier
        """
        return await self._identity_service_client.communication_identity.create(
            cls=lambda pr, u, e: CommunicationUserIdentifier(u['identity']['id'], raw_id=u['identity']['id']),
            **kwargs)

    @distributed_trace_async
    async def create_user_and_token(
            self,
            scopes: List[Union[str, 'CommunicationTokenScope']],
            **kwargs
        ) -> Tuple['CommunicationUserIdentifier', AccessToken]:
        """create a single Communication user with an identity token.
        :param scopes:
            List of scopes to be added to the token.
        :type scopes: list[str or ~azure.communication.identity.CommunicationTokenScope]
        :keyword token_expires_in: Custom validity period of the Communication Identity access token
         within [1, 24] hours range. If not provided, the default value of 24 hours will be used.
        :paramtype token_expires_in: ~datetime.timedelta
        :return: A tuple of a CommunicationUserIdentifier and a AccessToken.
        :rtype:
            tuple of (~azure.communication.identity.CommunicationUserIdentifier, ~azure.core.credentials.AccessToken)
        """
        token_expires_in = kwargs.pop('token_expires_in', None)
        request_body = {
            'createTokenWithScopes': scopes,
            'expiresInMinutes': convert_timedelta_to_mins(token_expires_in)
        }

        return await self._identity_service_client.communication_identity.create(
            body=request_body,
            cls=lambda pr, u, e: (CommunicationUserIdentifier(u['identity']['id'], raw_id=u['identity']['id']),
                AccessToken(u['accessToken']['token'], u['accessToken']['expiresOn'])),
            **kwargs)

    @distributed_trace_async
    async def delete_user(
            self,
            user: CommunicationUserIdentifier,
            **kwargs
        ) -> None:
        """Triggers revocation event for user and deletes all its data.

        :param user:
            Azure Communication User to delete
        :type user: ~azure.communication.identity.CommunicationUserIdentifier
        :return: None
        :rtype: None
        """
        await self._identity_service_client.communication_identity.delete(
            user.properties['id'],
            **kwargs)

    @distributed_trace_async
    async def get_token(
            self,
            user: CommunicationUserIdentifier,
            scopes: List[Union[str, 'CommunicationTokenScope']],
            **kwargs
        ) -> AccessToken:
        """Generates a new token for an identity.

        :param user: Azure Communication User
        :type user: ~azure.communication.identity.CommunicationUserIdentifier
        :param scopes:
            List of scopes to be added to the token.
        :type scopes: list[str or ~azure.communication.identity.CommunicationTokenScope]
        :keyword token_expires_in: Custom validity period of the Communication Identity access token
         within [1, 24] hours range. If not provided, the default value of 24 hours will be used.
        :paramtype token_expires_in: ~datetime.timedelta
        :return: AccessToken
        :rtype: ~azure.core.credentials.AccessToken
        """
        token_expires_in = kwargs.pop('token_expires_in', None)
        request_body = {
            'scopes': scopes,
            'expiresInMinutes': convert_timedelta_to_mins(token_expires_in)
        }

        return await self._identity_service_client.communication_identity.issue_access_token(
            user.properties['id'],
            body=request_body,
            cls=lambda pr, u, e: AccessToken(u['token'], u['expiresOn']),
            **kwargs)

    @distributed_trace_async
    async def revoke_tokens(
            self,
            user: CommunicationUserIdentifier,
            **kwargs
        ) -> None:
        """Schedule revocation of all tokens of an identity.

        :param user: Azure Communication User.
        :type user: ~azure.communication.identity.CommunicationUserIdentifier
        :return: None
        :rtype: None
        """
        return await self._identity_service_client.communication_identity.revoke_access_tokens(
            user.properties['id'] if user else None,
            **kwargs)

    @distributed_trace_async
    async def get_token_for_teams_user(
            self,
            aad_token,  # type: str
            client_id, # type: str
            user_object_id, # type: str
            **kwargs
        ) -> AccessToken:
        # type: (...) -> AccessToken
        """Exchanges an Azure AD access token of a Teams User for a new Communication Identity access token.

        :param aad_token: an Azure AD access token of a Teams User
        :type aad_token: str
        :param client_id: a Client ID of an Azure AD application to be verified against
            the appId claim in the Azure AD access token.
        :type client_id: str
        :param user_object_id: an Object ID of an Azure AD user (Teams User) to be verified against
            the OID claim in the Azure AD access token.
        :type user_object_id: str
        :return: AccessToken
        :rtype: ~azure.core.credentials.AccessToken
        """
        request_body = {
            "token": aad_token,
            "appId": client_id,
            "userId": user_object_id
        }
        return await self._identity_service_client.communication_identity.exchange_teams_user_access_token(
            body=request_body,
            cls=lambda pr, u, e: AccessToken(u['token'], u['expiresOn']),
            **kwargs)

    async def __aenter__(self) -> "CommunicationIdentityClient":
        await self._identity_service_client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the :class:
        `~azure.communication.identity.aio.CommunicationIdentityClient` session.
        """
        await self._identity_service_client.__aexit__()
