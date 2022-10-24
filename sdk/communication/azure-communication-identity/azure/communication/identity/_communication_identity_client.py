# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import TYPE_CHECKING, Any, Tuple

from azure.core.tracing.decorator import distributed_trace
from azure.core.credentials import AccessToken

from ._generated._communication_identity_client\
    import CommunicationIdentityClient as CommunicationIdentityClientGen
from ._shared.utils import parse_connection_str, get_authentication_policy
from ._shared.models import CommunicationUserIdentifier
from ._version import SDK_MONIKER
from ._api_versions import DEFAULT_VERSION
from ._utils import convert_timedelta_to_mins

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from ._generated.models import CommunicationTokenScope


class CommunicationIdentityClient(object): # pylint: disable=client-accepts-api-version-keyword
    """Azure Communication Services Identity client.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param TokenCredential credential:
        The TokenCredential we use to authenticate against the service.

    .. admonition:: Example:

        .. literalinclude:: ../samples/identity_samples.py
            :language: python
            :dedent: 8
    """

    def __init__(
            self,
            endpoint, # type: str
            credential, # type: TokenCredential
            **kwargs # type: Any
        ):
        # type: (...) -> None
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
            authentication_policy=get_authentication_policy(endpoint, credential),
            sdk_moniker=SDK_MONIKER,
            **kwargs)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            **kwargs  # type: Any
        ):  # type: (...) -> CommunicationIdentityClient
        """Create CommunicationIdentityClient from a Connection String.

        :param str conn_str: A connection string to an Azure Communication Service resource.
        :returns: Instance of CommunicationIdentityClient.
        :rtype: ~azure.communication.identity.CommunicationIdentityClient

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

    @distributed_trace
    def create_user(self, **kwargs):
        # type: (Any) -> CommunicationUserIdentifier
        """create a single Communication user

        :return: CommunicationUserIdentifier
        :rtype: ~azure.communication.identity.CommunicationUserIdentifier
        """
        return self._identity_service_client.communication_identity.create(
            cls=lambda pr, u, e: CommunicationUserIdentifier(u['identity']['id'], raw_id=u['identity']['id']),
            **kwargs)

    @distributed_trace
    def create_user_and_token(
            self,
            scopes, # List[Union[str, CommunicationTokenScope]]
            **kwargs # type: Any
        ):
        # type: (...) -> Tuple[CommunicationUserIdentifier, AccessToken]
        """Create a single Communication user with an identity token.

        :param scopes: List of scopes to be added to the token.
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
        return self._identity_service_client.communication_identity.create(
            cls=lambda pr, u, e: (CommunicationUserIdentifier(u['identity']['id'], raw_id=u['identity']['id']),
                AccessToken(u['accessToken']['token'], u['accessToken']['expiresOn'])),
            body=request_body,
            **kwargs)

    @distributed_trace
    def delete_user(
            self,
            user, # type: CommunicationUserIdentifier
            **kwargs # type: Any
        ):
        # type: (...) -> None
        """Triggers revocation event for user and deletes all its data.

        :param user: Azure Communication User to delete
        :type user: ~azure.communication.identity.CommunicationUserIdentifier
        :return: None
        :rtype: None
        """
        self._identity_service_client.communication_identity.delete(
            user.properties['id'],
            **kwargs)

    @distributed_trace
    def get_token(
            self,
            user, # type: CommunicationUserIdentifier
            scopes, # List[Union[str, CommunicationTokenScope]]
            **kwargs # type: Any
        ):
        # type: (...) -> AccessToken
        """Generates a new token for an identity.

        :param user: Azure Communication User
        :type user: ~azure.communication.identity.CommunicationUserIdentifier
        :param scopes: List of scopes to be added to the token.
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

        return self._identity_service_client.communication_identity.issue_access_token(
            user.properties['id'],
            body=request_body,
            cls=lambda pr, u, e: AccessToken(u['token'], u['expiresOn']),
            **kwargs)

    @distributed_trace
    def revoke_tokens(
            self,
            user, # type: CommunicationUserIdentifier
            **kwargs # type: Any
        ):
        # type: (...) -> None
        """Schedule revocation of all tokens of an identity.

        :param user: Azure Communication User.
        :type user: ~azure.communication.identity.CommunicationUserIdentifier.
        :return: None
        :rtype: None
        """
        return self._identity_service_client.communication_identity.revoke_access_tokens(
            user.properties['id'] if user else None,
            **kwargs)

    @distributed_trace
    def get_token_for_teams_user(
            self,
            aad_token, # type: str
            client_id, # type: str
            user_object_id, # type: str
            **kwargs
        ):
        # type: (...) -> AccessToken
        """Exchanges an Azure AD access token of a Teams User for a new Communication Identity access token.

        :param aad_token: an Azure AD access token of a Teams User.
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

        return self._identity_service_client.communication_identity.exchange_teams_user_access_token(
            body=request_body,
            cls=lambda pr, u, e: AccessToken(u['token'], u['expiresOn']),
            **kwargs)
        