# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional


class IsolationMode:
    disabled = "disabled"
    allow_internet_outbound = "allowInternetOutbound"
    allow_only_approved_outbound = "allowOnlyApprovedOutbound"


class OutboundRule:
    def __init__(
        self,
        type: str = None,
        destination: str = None
    ) -> None:
        self.type = type
        self.destination = destination

    @classmethod
    def _from_rest_object(cls, rest_obj: Any) -> "OutboundRule":
        return ManagedNetwork()


class FqdnDestination(OutboundRule):
    def __init__(self, destination: str) -> None:
        OutboundRule.__init__(self, "FQDN", destination)


class ServiceTagDestination(OutboundRule):
    def __init__(self, destination: str) -> None:
        OutboundRule.__init__(self, "ServiceTag", destination)


class PrivateEndpointDestination(OutboundRule):
    def __init__(self, privateLinkService: str, subResourceTarget: str) -> None:
        destination = privateLinkService + "," + subResourceTarget
        OutboundRule.__init__(self, "privateEndpoint", destination)


class ManagedNetwork:
    def __init__(
        self,
        isolation_mode: str = IsolationMode.disabled, 
        outbound_rules: Optional[Dict[str, OutboundRule]] = None
    ) -> None:
        self.isolation_mode = isolation_mode
        self.outbound_rules = outbound_rules

    @classmethod
    def _from_rest_object(cls, rest_obj: Any) -> "ManagedNetwork":
        return ManagedNetwork()
