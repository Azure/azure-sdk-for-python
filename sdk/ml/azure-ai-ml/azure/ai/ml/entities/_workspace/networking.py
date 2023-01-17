# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Optional

from azure.ai.ml._restclient.v2022_12_01_preview.models import (
    ManagedNetworkSettings as RestManagedNetwork,
    FqdnOutboundRule as RestFqdnOutboundRule,
    PrivateEndpointOutboundRule as RestPrivateEndpointOutboundRule,
    PrivateEndpointOutboundRuleDestination as RestPrivateEndpointOutboundRuleDestination,
    ServiceTagOutboundRule as RestServiceTagOutboundRule,
    ServiceTagOutboundRuleDestination as RestServiceTagOutboundRuleDestination,
)


class IsolationMode:
    DISABLED = "Disabled"
    ALLOW_INTERNET_OUTBOUND = "AllowInternetOutbound"
    ALLOW_ONLY_APPROVED_OUTBOUND = "AllowOnlyApprovedOutbound"


class Protocol:
    TCP = "TCP"
    UDP = "UDP"
    ICMP = "ICMP"
    ALL = "*"


class OutboundRuleCategory:
    REQUIRED = "Required"
    RECOMMENDED = "Recommended"
    USER_DEFINED = "UserDefined"


class OutboundRuleType:
    FQDN = "FQDN"
    PRIVATE_ENDPOINT = "PrivateEndpoint"
    SERVICE_TAG = "ServiceTag"


class OutboundRule:
    def __init__(
        self, type: str = None, category: str = OutboundRuleCategory.USER_DEFINED  # pylint: disable=redefined-builtin
    ) -> None:
        self.type = type
        self.category = category

    @classmethod
    def _from_rest_object(cls, rest_obj: Any) -> "OutboundRule":
        if isinstance(rest_obj, RestFqdnOutboundRule):
            rule = FqdnDestination(destination=rest_obj.destination)
            rule.category = rest_obj.category
            return rule
        if isinstance(rest_obj, RestPrivateEndpointOutboundRule):
            rule = PrivateEndpointDestination(
                service_resource_id=rest_obj.destination.service_resource_id,
                subresource_target=rest_obj.destination.subresource_target,
                spark_jobs_enabled=rest_obj.destination.spark_jobs_enabled,
            )
            rule.category = rest_obj.category
            return rule
        if isinstance(rest_obj, RestServiceTagOutboundRule):
            rule = ServiceTagDestination(
                service_tag=rest_obj.destination.service_tag,
                protocol=rest_obj.destination.protocol,
                port_ranges=rest_obj.destination.port_ranges,
            )
            rule.category = rest_obj.category
            return rule


class FqdnDestination(OutboundRule):
    def __init__(self, destination: str) -> None:
        self.destination = destination
        OutboundRule.__init__(self, type=OutboundRuleType.FQDN)

    def _to_rest_object(self) -> RestFqdnOutboundRule:
        return RestFqdnOutboundRule(type=self.type, category=self.category, destination=self.destination)


class PrivateEndpointDestination(OutboundRule):
    def __init__(self, service_resource_id: str, subresource_target: str, spark_jobs_enabled: bool = False) -> None:
        self.service_resource_id = service_resource_id
        self.subresource_target = subresource_target
        self.spark_jobs_enabled = spark_jobs_enabled
        OutboundRule.__init__(self, OutboundRuleType.PRIVATE_ENDPOINT)

    def _to_rest_object(self) -> RestPrivateEndpointOutboundRule:
        return RestPrivateEndpointOutboundRule(
            type=self.type,
            category=self.category,
            destination=RestPrivateEndpointOutboundRuleDestination(
                service_resource_id=self.service_resource_id,
                subresource_target=self.subresource_target,
                spark_jobs_enabled=self.spark_jobs_enabled,
            ),
        )


class ServiceTagDestination(OutboundRule):
    def __init__(self, service_tag: str, protocol: str, port_ranges: str) -> None:
        self.service_tag = service_tag
        self.protocol = protocol
        self.port_ranges = port_ranges
        OutboundRule.__init__(self, OutboundRuleType.SERVICE_TAG)

    def _to_rest_object(self) -> RestServiceTagOutboundRule:
        return RestServiceTagOutboundRule(
            type=self.type,
            category=self.category,
            destination=RestServiceTagOutboundRuleDestination(
                service_tag=self.service_tag, protocol=self.protocol, port_ranges=self.port_ranges
            ),
        )


class ManagedNetwork:
    def __init__(
        self, isolation_mode: str = IsolationMode.DISABLED, outbound_rules: Optional[Dict[str, OutboundRule]] = None
    ) -> None:
        self.isolation_mode = isolation_mode
        self.outbound_rules = outbound_rules

    def _to_rest_object(self) -> RestManagedNetwork:
        rest_outbound_rules = (
            {
                rule_name: self.outbound_rules[rule_name]._to_rest_object() for rule_name in self.outbound_rules
            }  # pylint: disable=protected-access
            if self.outbound_rules
            else None
        )
        return RestManagedNetwork(isolation_mode=self.isolation_mode, outbound_rules=rest_outbound_rules)

    @classmethod
    def _from_rest_object(cls, obj: RestManagedNetwork) -> "ManagedNetwork":
        from_rest_outbound_rules = (
            {
                rule_name: OutboundRule._from_rest_object(
                    obj.outbound_rules[rule_name]
                )  # pylint: disable=protected-access
                for rule_name in obj.outbound_rules
            }
            if obj.outbound_rules
            else {}
        )
        return ManagedNetwork(isolation_mode=obj.isolation_mode, outbound_rules=from_rest_outbound_rules)
