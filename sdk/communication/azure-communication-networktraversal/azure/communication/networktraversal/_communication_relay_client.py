# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from typing import TYPE_CHECKING

from azure.core.tracing.decorator import distributed_trace

from ._generated._communication_network_traversal_client\
    import CommunicationNetworkTraversalClient\
        as CommunicationNetworkTraversalClientGen
from ._shared.utils import parse_connection_str, get_authentication_policy
from ._version import SDK_MONIKER
from ._generated.models import CommunicationRelayConfiguration

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from azure.communication.identity import CommunicationUserIdentifier
    from azure.communication.networktraversal import RouteType

class CommunicationRelayClient(object): # pylint: disable=client-accepts-api-version-keyword
    """Azure Communication Services Relay client.

    :param str endpoint:
        The endpoint url for Azure Communication Service resource.
    :param TokenCredential credential:
        The TokenCredential we use to authenticate against the service.

    .. admonition:: Example:

        .. literalinclude:: ../samples/network_traversal_samples.py
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
            authentication_policy=get_authentication_policy(endpoint, credential),
            sdk_moniker=SDK_MONIKER,
            **kwargs)

    @classmethod
    def from_connection_string(
            cls, conn_str,  # type: str
            **kwargs  # type: Any
        ):  # type: (...) -> CommunicationRelayClient
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

    @distributed_trace
    def get_relay_configuration(
            self,
            *,
            user=None, # type: CommunicationUserIdentifier
            route_type=None, # type: Optional[Union[str, "RouteType"]]
            ttl=172800,  # type: Optional[int]
            **kwargs # type: Any
    ):
    # type: (...) -> CommunicationRelayConfiguration
        """get a Communication Relay configuration
        :param user: Azure Communication User
        :type user: ~azure.communication.identity.CommunicationUserIdentifier
        :param route_type: Azure Communication Route Type
        :type route_type: ~azure.communication.networktraversal.RouteType
        :return: CommunicationRelayConfiguration
        :rtype: ~azure.communication.networktraversal.models.CommunicationRelayConfiguration
        """
        if user is None:
            return self._network_traversal_service_client.communication_network_traversal.issue_relay_configuration(
                route_type=route_type, ttl=ttl, **kwargs)
        return self._network_traversal_service_client.communication_network_traversal.issue_relay_configuration(
            id=user.properties['id'],
            route_type=route_type,
            ttl=ttl,
            **kwargs)
