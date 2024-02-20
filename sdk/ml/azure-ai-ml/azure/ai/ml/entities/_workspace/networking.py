# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional, List

from abc import ABC
from azure.ai.ml._restclient.v2023_06_01_preview.models import (
    ManagedNetworkSettings as RestManagedNetwork,
    FqdnOutboundRule as RestFqdnOutboundRule,
    PrivateEndpointOutboundRule as RestPrivateEndpointOutboundRule,
    PrivateEndpointDestination as RestPrivateEndpointOutboundRuleDestination,
    ServiceTagOutboundRule as RestServiceTagOutboundRule,
    ServiceTagDestination as RestServiceTagOutboundRuleDestination,
    ManagedNetworkProvisionStatus as RestManagedNetworkProvisionStatus,
)
from azure.ai.ml.constants._workspace import IsolationMode, OutboundRuleCategory, OutboundRuleType


class OutboundRule(ABC):
    """Base class for Outbound Rules, cannot be instantiated directly. Please see FqdnDestination,
    PrivateEndpointDestination, and ServiceTagDestination objects to create outbound rules.

    :param name: Name of the outbound rule.
    :type name: str
    :param type: Type of the outbound rule. Supported types are "FQDN", "PrivateEndpoint", "ServiceTag"
    :type type: str
    :ivar type: Type of the outbound rule. Supported types are "FQDN", "PrivateEndpoint", "ServiceTag"
    :vartype type: str
    """

    def __init__(
        self,
        *,
        name: str = None,
        **kwargs,
    ) -> None:
        self.name = name
        self.type = kwargs.pop("type", None)
        self.category = kwargs.pop("category", OutboundRuleCategory.USER_DEFINED)
        self.status = kwargs.pop("status", None)

    @classmethod
    def _from_rest_object(cls, rest_obj: Any, name: str) -> Optional["OutboundRule"]:
        if isinstance(rest_obj, RestFqdnOutboundRule):
            rule = FqdnDestination(destination=rest_obj.destination, name=name)
            rule.category = rest_obj.category
            rule.status = rest_obj.status
            return rule
        if isinstance(rest_obj, RestPrivateEndpointOutboundRule):
            rule = PrivateEndpointDestination(
                service_resource_id=rest_obj.destination.service_resource_id,
                subresource_target=rest_obj.destination.subresource_target,
                spark_enabled=rest_obj.destination.spark_enabled,
                name=name,
            )
            rule.category = rest_obj.category
            rule.status = rest_obj.status
            return rule
        if isinstance(rest_obj, RestServiceTagOutboundRule):
            rule = ServiceTagDestination(
                service_tag=rest_obj.destination.service_tag,
                protocol=rest_obj.destination.protocol,
                port_ranges=rest_obj.destination.port_ranges,
                name=name,
            )
            rule.category = rest_obj.category
            rule.status = rest_obj.status
            return rule

        return None


class FqdnDestination(OutboundRule):
    """Class representing a FQDN outbound rule.

    :param name: Name of the outbound rule.
    :type name: str
    :param destination: Fully qualified domain name to which outbound connections are allowed.
        For example: “*.contoso.com”.
    :type destination: str
    :ivar type: Type of the outbound rule. Set to "FQDN" for this class.
    :vartype type: str

    .. literalinclude:: ../samples/ml_samples_workspace.py
            :start-after: [START fqdn_outboundrule]
            :end-before: [END fqdn_outboundrule]
            :language: python
            :dedent: 8
            :caption: Creating a FqdnDestination outbound rule object.
    """

    def __init__(self, *, name: str, destination: str, **kwargs) -> None:
        self.destination = destination
        OutboundRule.__init__(self, type=OutboundRuleType.FQDN, name=name, **kwargs)

    def _to_rest_object(self) -> RestFqdnOutboundRule:
        return RestFqdnOutboundRule(type=self.type, category=self.category, destination=self.destination)

    def _to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": OutboundRuleType.FQDN,
            "category": self.category,
            "destination": self.destination,
            "status": self.status,
        }


class PrivateEndpointDestination(OutboundRule):
    """Class representing a Private Endpoint outbound rule.

    :param name: Name of the outbound rule.
    :type name: str
    :param service_resource_id: The resource URI of the root service that supports creation of the private link.
    :type service_resource_id: str
    :param subresource_target: The target endpoint of the subresource of the service.
    :type subresource_target: str
    :param spark_enabled: Indicates if the private endpoint can be used for Spark jobs, default is “false”.
    :type spark_enabled: bool
    :ivar type: Type of the outbound rule. Set to "PrivateEndpoint" for this class.
    :vartype type: str

    .. literalinclude:: ../samples/ml_samples_workspace.py
            :start-after: [START private_endpoint_outboundrule]
            :end-before: [END private_endpoint_outboundrule]
            :language: python
            :dedent: 8
            :caption: Creating a PrivateEndpointDestination outbound rule object.
    """

    def __init__(
        self,
        *,
        name: str,
        service_resource_id: str,
        subresource_target: str,
        spark_enabled: bool = False,
        **kwargs,
    ) -> None:
        self.service_resource_id = service_resource_id
        self.subresource_target = subresource_target
        self.spark_enabled = spark_enabled
        OutboundRule.__init__(self, type=OutboundRuleType.PRIVATE_ENDPOINT, name=name, **kwargs)

    def _to_rest_object(self) -> RestPrivateEndpointOutboundRule:
        return RestPrivateEndpointOutboundRule(
            type=self.type,
            category=self.category,
            destination=RestPrivateEndpointOutboundRuleDestination(
                service_resource_id=self.service_resource_id,
                subresource_target=self.subresource_target,
                spark_enabled=self.spark_enabled,
            ),
        )

    def _to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": OutboundRuleType.PRIVATE_ENDPOINT,
            "category": self.category,
            "destination": {
                "service_resource_id": self.service_resource_id,
                "subresource_target": self.subresource_target,
                "spark_enabled": self.spark_enabled,
            },
            "status": self.status,
        }


class ServiceTagDestination(OutboundRule):
    """Class representing a Service Tag outbound rule.

    :param name: Name of the outbound rule.
    :type name: str
    :param service_tag: Service Tag of an Azure service, maps to predefined IP addresses for its service endpoints.
    :type service_tag: str
    :param protocol: Allowed transport protocol, can be "TCP", "UDP", "ICMP" or "*" for all supported protocols.
    :type protocol: str
    :param port_ranges: A comma-separated list of single ports and/or range of ports, such as "80,1024-65535".
        Traffics should be allowed to these port ranges.
    :type port_ranges: str
    :ivar type: Type of the outbound rule. Set to "ServiceTag" for this class.
    :vartype type: str

    .. literalinclude:: ../samples/ml_samples_workspace.py
            :start-after: [START service_tag_outboundrule]
            :end-before: [END service_tag_outboundrule]
            :language: python
            :dedent: 8
            :caption: Creating a ServiceTagDestination outbound rule object.
    """

    def __init__(
        self,
        *,
        name: str,
        service_tag: str,
        protocol: str,
        port_ranges: str,
        **kwargs,
    ) -> None:
        self.service_tag = service_tag
        self.protocol = protocol
        self.port_ranges = port_ranges
        OutboundRule.__init__(self, type=OutboundRuleType.SERVICE_TAG, name=name, **kwargs)

    def _to_rest_object(self) -> RestServiceTagOutboundRule:
        return RestServiceTagOutboundRule(
            type=self.type,
            category=self.category,
            destination=RestServiceTagOutboundRuleDestination(
                service_tag=self.service_tag, protocol=self.protocol, port_ranges=self.port_ranges
            ),
        )

    def _to_dict(self) -> Dict:
        return {
            "name": self.name,
            "type": OutboundRuleType.SERVICE_TAG,
            "category": self.category,
            "destination": {
                "service_tag": self.service_tag,
                "protocol": self.protocol,
                "port_ranges": self.port_ranges,
            },
            "status": self.status,
        }


class ManagedNetwork:
    """Managed Network settings for a workspace.

    :param isolation_mode: Isolation of the managed network, defaults to Disabled.
    :type isolation_mode: str
    :param outbound_rules: List of outbound rules for the managed network.
    :type outbound_rules: List[~azure.ai.ml.entities.OutboundRule]
    :param network_id: Network id for the managed network, not meant to be set by user.
    :type network_id: str

    .. literalinclude:: ../samples/ml_samples_workspace.py
            :start-after: [START workspace_managed_network]
            :end-before: [END workspace_managed_network]
            :language: python
            :dedent: 8
            :caption: Creating a ManagedNetwork object with one of each rule type.
    """

    def __init__(
        self,
        *,
        isolation_mode: str = IsolationMode.DISABLED,
        outbound_rules: Optional[List[OutboundRule]] = None,
        network_id: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.isolation_mode = isolation_mode
        self.network_id = network_id
        self.outbound_rules = outbound_rules
        self.status = kwargs.pop("status", None)

    def _to_rest_object(self) -> RestManagedNetwork:
        rest_outbound_rules = (
            {
                outbound_rule.name: outbound_rule._to_rest_object()  # pylint: disable=protected-access
                for outbound_rule in self.outbound_rules
            }
            if self.outbound_rules
            else None
        )
        return RestManagedNetwork(isolation_mode=self.isolation_mode, outbound_rules=rest_outbound_rules)

    @classmethod
    def _from_rest_object(cls, obj: RestManagedNetwork) -> "ManagedNetwork":
        from_rest_outbound_rules = (
            [
                OutboundRule._from_rest_object(obj.outbound_rules[name], name=name)  # pylint: disable=protected-access
                for name in obj.outbound_rules
            ]
            if obj.outbound_rules
            else {}
        )
        return ManagedNetwork(
            isolation_mode=obj.isolation_mode,
            outbound_rules=from_rest_outbound_rules,
            network_id=obj.network_id,
            status=obj.status,
        )


class ManagedNetworkProvisionStatus:
    """ManagedNetworkProvisionStatus.

    :param status: Status for managed network provision.
    :type status: str
    :param spark_ready: Bool value indicating if managed network is spark ready
    :type spark_ready: bool
    """

    def __init__(
        self,
        *,
        status: Optional[str] = None,
        spark_ready: Optional[bool] = None,
    ):
        self.status = status
        self.spark_ready = spark_ready

    @classmethod
    def _from_rest_object(cls, rest_obj: RestManagedNetworkProvisionStatus) -> "ManagedNetworkProvisionStatus":
        return cls(
            status=rest_obj.status,
            spark_ready=rest_obj.spark_ready,
        )
