# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use,no-else-return

from marshmallow import fields, EXCLUDE
from marshmallow.decorators import post_load, pre_dump
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml._schema.core.fields import StringTransformedEnum
from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml.entities._workspace.networking import (
    ManagedNetwork,
    FqdnDestination,
    ServiceTagDestination,
    PrivateEndpointDestination,
)
from azure.ai.ml.constants._workspace import IsolationMode, OutboundRuleCategory, OutboundRuleType
from azure.ai.ml._utils.utils import camel_to_snake, _snake_to_camel

from azure.ai.ml._utils._experimental import experimental


@experimental
class DestinationSchema(metaclass=PatchedSchemaMeta):
    service_resource_id = fields.Str()
    subresource_target = fields.Str()
    spark_enabled = fields.Bool()
    service_tag = fields.Str()
    protocol = fields.Str()
    port_ranges = fields.Str()


@experimental
class ManagedNetworkStatusSchema(metaclass=PatchedSchemaMeta):
    spark_ready = fields.Bool()
    status = fields.Str()


@experimental
class OutboundRuleSchema(metaclass=PatchedSchemaMeta):
    name = fields.Str(required=True)
    type = StringTransformedEnum(
        allowed_values=[OutboundRuleType.FQDN, OutboundRuleType.PRIVATE_ENDPOINT, OutboundRuleType.SERVICE_TAG],
        casing_transform=camel_to_snake,
        metadata={"description": "outbound rule type."},
    )
    destination = fields.Raw(required=True)
    category = StringTransformedEnum(
        allowed_values=[
            OutboundRuleCategory.REQUIRED,
            OutboundRuleCategory.RECOMMENDED,
            OutboundRuleCategory.USER_DEFINED,
        ],
        casing_transform=camel_to_snake,
        metadata={"description": "outbound rule category."},
    )
    status = fields.Str(dump_only=True)

    @pre_dump
    def predump(self, data, **kwargs):
        if data and isinstance(data, FqdnDestination):
            data.destination = self.fqdn_dest2dict(data.destination)
        if data and isinstance(data, PrivateEndpointDestination):
            data.destination = self.pe_dest2dict(data.service_resource_id, data.subresource_target, data.spark_enabled)
        if data and isinstance(data, ServiceTagDestination):
            data.destination = self.service_tag_dest2dict(data.service_tag, data.protocol, data.port_ranges)
        return data

    @post_load
    def createdestobject(self, data, **kwargs):
        dest = data.get("destination", False)
        category = data.get("category", OutboundRuleCategory.USER_DEFINED)
        name = data.get("name", None)
        status = data.get("status", None)
        if dest:
            if isinstance(dest, str):
                return FqdnDestination(name=name, destination=dest, category=_snake_to_camel(category), status=status)
            else:
                if dest.get("subresource_target", False):
                    return PrivateEndpointDestination(
                        name=name,
                        service_resource_id=dest["service_resource_id"],
                        subresource_target=dest["subresource_target"],
                        spark_enabled=dest["spark_enabled"],
                        category=_snake_to_camel(category),
                        status=status,
                    )
            return ServiceTagDestination(
                name=name,
                service_tag=dest["service_tag"],
                protocol=dest["protocol"],
                port_ranges=dest["port_ranges"],
                category=_snake_to_camel(category),
                status=status,
            )

    def fqdn_dest2dict(self, fqdndest):
        res = fqdndest
        return res

    def pe_dest2dict(self, service_resource_id, subresource_target, spark_enabled):
        pedest = {}
        pedest["service_resource_id"] = service_resource_id
        pedest["subresource_target"] = subresource_target
        pedest["spark_enabled"] = spark_enabled
        return pedest

    def service_tag_dest2dict(self, service_tag, protocol, port_ranges):
        service_tag_dest = {}
        service_tag_dest["service_tag"] = service_tag
        service_tag_dest["protocol"] = protocol
        service_tag_dest["port_ranges"] = port_ranges
        return service_tag_dest


@experimental
class ManagedNetworkSchema(metaclass=PatchedSchemaMeta):
    isolation_mode = StringTransformedEnum(
        allowed_values=[
            IsolationMode.DISABLED,
            IsolationMode.ALLOW_INTERNET_OUTBOUND,
            IsolationMode.ALLOW_ONLY_APPROVED_OUTBOUND,
        ],
        casing_transform=camel_to_snake,
        metadata={"description": "isolation mode for the workspace managed network."},
    )
    outbound_rules = fields.List(NestedField(OutboundRuleSchema, allow_none=False, unknown=EXCLUDE), allow_none=True)
    network_id = fields.Str(required=False)
    status = NestedField(ManagedNetworkStatusSchema, dump_only=True)

    @post_load
    def make(self, data, **kwargs):
        outbound_rules = data.get("outbound_rules", False)
        if outbound_rules:
            return ManagedNetwork(_snake_to_camel(data["isolation_mode"]), outbound_rules)
        else:
            return ManagedNetwork(_snake_to_camel(data["isolation_mode"]))
