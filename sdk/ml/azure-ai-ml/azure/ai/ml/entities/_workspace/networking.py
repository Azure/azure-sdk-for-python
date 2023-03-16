# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional, List

from azure.ai.ml._restclient.v2022_12_01_preview.models import (
    ManagedNetworkSettings as RestManagedNetwork,
    FqdnOutboundRule as RestFqdnOutboundRule,
    PrivateEndpointOutboundRule as RestPrivateEndpointOutboundRule,
    PrivateEndpointOutboundRuleDestination as RestPrivateEndpointOutboundRuleDestination,
    ServiceTagOutboundRule as RestServiceTagOutboundRule,
    ServiceTagOutboundRuleDestination as RestServiceTagOutboundRuleDestination,
)
from azure.ai.ml.constants._workspace import IsolationMode, OutboundRuleCategory, OutboundRuleType

from azure.ai.ml._utils._experimental import experimental


@experimental
class OutboundRule:
    """Base class for Outbound Rules, should not be instantiated directly.

    :param rule_name: Name of the outbound rule.
    :type rule_name: str
    :param type: Type of the outbound rule. Supported types are "FQDN", "PrivateEndpoint", "ServiceTag"
    :type type: str
    """

    def __init__(
        self,
        *,
        rule_name: str = None,
        **kwargs,
    ) -> None:
        self.rule_name = rule_name
        self.type = kwargs.pop("type", None)
        self.category = kwargs.pop("category", OutboundRuleCategory.USER_DEFINED)

    @classmethod
    def _from_rest_object(cls, rest_obj: Any, rule_name: str) -> "OutboundRule":
        if isinstance(rest_obj, RestFqdnOutboundRule):
            rule = FqdnDestination(destination=rest_obj.destination, rule_name=rule_name)
            rule.category = rest_obj.category
            return rule
        if isinstance(rest_obj, RestPrivateEndpointOutboundRule):
            rule = PrivateEndpointDestination(
                service_resource_id=rest_obj.destination.service_resource_id,
                subresource_target=rest_obj.destination.subresource_target,
                spark_enabled=rest_obj.destination.spark_enabled,
                rule_name=rule_name,
            )
            rule.category = rest_obj.category
            return rule
        if isinstance(rest_obj, RestServiceTagOutboundRule):
            rule = ServiceTagDestination(
                service_tag=rest_obj.destination.service_tag,
                protocol=rest_obj.destination.protocol,
                port_ranges=rest_obj.destination.port_ranges,
                rule_name=rule_name,
            )
            rule.category = rest_obj.category
            return rule


@experimental
class FqdnDestination(OutboundRule):
    def __init__(
        self,
        *,
        rule_name: str,
        destination: str,
        **kwargs
    ) -> None:
        self.destination = destination
        category = kwargs.pop("category", OutboundRuleCategory.USER_DEFINED)
        OutboundRule.__init__(self, type=OutboundRuleType.FQDN, category=category, rule_name=rule_name)

    def _to_rest_object(self) -> RestFqdnOutboundRule:
        return RestFqdnOutboundRule(type=self.type, category=self.category, destination=self.destination)

    def _to_dict(self) -> Dict:
        return {
            self.rule_name: {"type": OutboundRuleType.FQDN, "category": self.category, "destination": self.destination}
        }


@experimental
class PrivateEndpointDestination(OutboundRule):
    def __init__(
        self,
        *,
        rule_name: str,
        service_resource_id: str,
        subresource_target: str,
        spark_enabled: bool = False,
        **kwargs,
    ) -> None:
        self.service_resource_id = service_resource_id
        self.subresource_target = subresource_target
        self.spark_enabled = spark_enabled
        category = kwargs.pop("category", OutboundRuleCategory.USER_DEFINED)
        OutboundRule.__init__(self, type=OutboundRuleType.PRIVATE_ENDPOINT, category=category, rule_name=rule_name)

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
            self.rule_name: {
                "type": OutboundRuleType.PRIVATE_ENDPOINT,
                "category": self.category,
                "destination": {
                    "service_resource_id": self.service_resource_id,
                    "subresource_target": self.subresource_target,
                    "spark_enabled": self.spark_enabled,
                },
            }
        }


@experimental
class ServiceTagDestination(OutboundRule):
    def __init__(
        self,
        *,
        rule_name: str,
        service_tag: str,
        protocol: str,
        port_ranges: str,
        **kwargs,
    ) -> None:
        self.service_tag = service_tag
        self.protocol = protocol
        self.port_ranges = port_ranges
        category = kwargs.pop("category", OutboundRuleCategory.USER_DEFINED)
        OutboundRule.__init__(self, type=OutboundRuleType.SERVICE_TAG, category=category, rule_name=rule_name)

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
            self.rule_name: {
                "type": OutboundRuleType.SERVICE_TAG,
                "category": self.category,
                "destination": {
                    "service_tag": self.service_tag,
                    "protocol": self.protocol,
                    "port_ranges": self.port_ranges,
                },
            }
        }


@experimental
class ManagedNetwork:
    def __init__(
        self,
        isolation_mode: str = IsolationMode.DISABLED,
        outbound_rules: Optional[List[OutboundRule]] = None,
        network_id: Optional[str] = None,
    ) -> None:
        self.isolation_mode = isolation_mode
        self.network_id = network_id
        self.outbound_rules = outbound_rules

    def _to_rest_object(self) -> RestManagedNetwork:
        rest_outbound_rules = (
            {
                outbound_rule.rule_name: outbound_rule._to_rest_object()  # pylint: disable=protected-access
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
                OutboundRule._from_rest_object(  # pylint: disable=protected-access
                    obj.outbound_rules[rule_name], rule_name=rule_name
                )
                for rule_name in obj.outbound_rules
            ]
            if obj.outbound_rules
            else {}
        )
        return ManagedNetwork(
            isolation_mode=obj.isolation_mode, outbound_rules=from_rest_outbound_rules, network_id=obj.network_id
        )
