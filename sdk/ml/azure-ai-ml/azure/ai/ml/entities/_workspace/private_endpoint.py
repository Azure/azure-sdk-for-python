# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Optional


class EndpointConnection:
    """Private Endpoint Connection related to a workspace private endpoint.

    :param subscription_id: Subscription id of the connection.
    :type subscription_id: str
    :param resource_group: Resource group of the connection.
    :type resource_group: str
    :param vnet_name: Name of the virtual network of the connection.
    :type vnet_name: str
    :param subnet_name: Name of the subnet of the connection.
    :type subnet_name: str
    :param location: Location of the connection.
    :type location: str
    """

    def __init__(
        self,
        subscription_id: str,
        resource_group: str,
        vnet_name: str,
        subnet_name: str,
        location: Optional[str] = None,
    ):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.location = location
        self.vnet_name = vnet_name
        self.subnet_name = subnet_name


class PrivateEndpoint:
    """Private Endpoint of a workspace.

    :param approval_type: Approval type of the private endpoint.
    :type approval_type: str
    :param connections: List of private endpoint connections.
    :type connections: List[~azure.ai.ml.entities.EndpointConnection]
    """

    def __init__(
        self,
        approval_type: Optional[str] = None,
        connections: Optional[Dict[str, EndpointConnection]] = None,
    ):
        self.approval_type = approval_type
        self.connections = connections
