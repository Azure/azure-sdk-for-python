# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Dict, Optional


class EndpointConnection:
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
    def __init__(
        self,
        approval_type: Optional[str] = None,
        connections: Optional[Dict[str, EndpointConnection]] = None,
    ):
        self.approval_type = approval_type
        self.connections = connections
