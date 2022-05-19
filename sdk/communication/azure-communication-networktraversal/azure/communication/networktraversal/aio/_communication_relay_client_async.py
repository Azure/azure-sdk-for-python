# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import TYPE_CHECKING, Optional, Union

from azure.core.tracing.decorator_async import distributed_trace_async
from .._generated.aio._communication_network_traversal_client\
    import CommunicationNetworkTraversalClient as CommunicationNetworkTraversalClientGen
from .._shared.utils import parse_connection_str, get_authentication_policy
from .._version import SDK_MONIKER

if TYPE_CHECKING:
    from azure.core.credentials_async import AsyncTokenCredential
    from .._generated.models import CommunicationRelayConfiguration
    from azure.communication.identity import CommunicationUserIdentifier
    from azure.communication.networktraversal import RouteType


class CommunicationRelayClient: # pylint: disable=client-accepts-api-version-keyword
    """Azure Communication Services Network Traversal client.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param AsyncTokenCredential credential:
        The AsyncTokenCredential we use to authenticate against the service.

    .. admonition:: Example:

        .. literalinclude:: ../samples/network_traversal_samples_async.py
            :language: python
            :dedent: 8
    """
    def __init__(
        self,
        endpoint: str,
        credential: 'AsyncTokenCredential',
        **kwargs
        ) -> None:
        # pylint: disable=bad-option-value, disable=raise-missing-from
        try:
            if not endpoint.lower().startswith('http'):
                endpoint = "https://" + endpoint
        except AttributeError:
            raise ValueError("Account URL must be a string.")

        if not credential:
            raise ValueError(
                "You need to provide account shared key to authenticate.")

        self._endpoint = endpoint
        self._network_traversal_service_client = CommunicationNetworkTraversalClientGen(
            self._endpoint,
            authentication_policy=get_authentication_policy(endpoint, credential, decode_url=True, is_async=True),
            sdk_moniker=SDK_MONIKER,
            **kwargs)

    @classmethod
    def from_connection_string(
            cls, conn_str: str,
            **kwargs
        ) -> 'CommunicationRelayClient':
        """Create CommunicationRelayClient from a Connection String.

        :param str conn_str: A connection string to an Azure Communication Service resource.
        :returns: Instance of CommunicationRelayClient.
        :rtype: ~azure.communication.networktraversal.CommunicationRelayClient

        .. admonition:: Example:

            .. literalinclude:: ../samples/network_traversal_samples_async.py
                :start-after: [START auth_from_connection_string]
                :end-before: [END auth_from_connection_string]
                :language: python
                :dedent: 8
                :caption: Creating the CommunicationRelayClient from a connection string.
        """
        endpoint, access_key = parse_connection_str(conn_str)

        return cls(endpoint, access_key, **kwargs)

    @distributed_trace_async
    async def get_relay_configuration(
            self,
            *,
            user: 'CommunicationUserIdentifier' = None,
            route_type: Optional[Union[str, "RouteType"]] = None,
            ttl: Optional[int] = 172800,
            **kwargs # type: Any
        ) -> 'CommunicationRelayConfiguration':
        """get a Communication Relay configuration.
        :param user: Azure Communication User
        :type user: ~azure.communication.identity.CommunicationUserIdentifier
        :param route_type: Azure Communication Route Type
        :type route_type: ~azure.communication.networktraversal.RouteType
        :return: CommunicationRelayConfiguration
        :rtype: ~azure.communication.networktraversal.models.CommunicationRelayConfiguration
        """
        if user is None:
            return await self._network_traversal_service_client.communication_network_traversal. \
                issue_relay_configuration(route_type=route_type, ttl=ttl, **kwargs)
        return await self._network_traversal_service_client.communication_network_traversal.issue_relay_configuration(
            id=user.properties['id'],
            route_type=route_type,
            ttl=ttl,
            **kwargs)

    async def __aenter__(self) -> "CommunicationRelayClient":
        await self._network_traversal_service_client.__aenter__()
        return self

    async def __aexit__(self, *args) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the :class:
        `~azure.communication.networktraversal.aio.CommunicationRelayClient` session.
        """
        await self._network_traversal_service_client.__aexit__()
