# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=unused-argument,no-self-use,no-else-return

from marshmallow import fields
from marshmallow.decorators import post_load, pre_dump
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml.entities._workspace.networking import (
    ManagedNetwork,
    OutboundRule,
    FqdnDestination,
    ServiceTagDestination,
    PrivateEndpointDestination,
)


class DestinationSchema(metaclass=PatchedSchemaMeta):
    service_resource_id = fields.Str()
    subresource_target = fields.Str()
    spark_jobs_enabled = fields.Bool()
    service_tag = fields.Str()
    protocol = fields.Str()
    port_ranges = fields.Str()


class OutboundRuleSchema(metaclass=PatchedSchemaMeta):
    type = fields.Str(required=False)
    destination = fields.Raw(required=True)
    category = fields.Str(required=False)

    @pre_dump
    def predump(self, data, **kwargs):
        if data and isinstance(data, FqdnDestination):
            data.destination = self.fqdn_dest2dict(data.destination)
        if data and isinstance(data, PrivateEndpointDestination):
            data.destination = self.pe_dest2dict(
                data.service_resource_id, data.subresource_target, data.spark_jobs_enabled
            )
        if data and isinstance(data, ServiceTagDestination):
            data.destination = self.service_tag_dest2dict(data.service_tag, data.protocol, data.port_ranges)
        return data

    @post_load
    def createdestobject(self, data, **kwargs):
        dest = data.get("destination", False)
        if dest:
            if isinstance(dest, str):
                return FqdnDestination(dest)
            else:
                if dest.get("subresource_target", False):
                    return PrivateEndpointDestination(
                        dest["service_resource_id"], dest["subresource_target"], dest["spark_jobs_enabled"]
                    )
                if dest.get("service_tag", False):
                    return ServiceTagDestination(dest["service_tag"], dest["protocol"], dest["port_ranges"])
        return OutboundRule(data)

    def fqdn_dest2dict(self, fqdndest):
        res = fqdndest
        return res

    def pe_dest2dict(self, service_resource_id, subresource_target, spark_jobs_enabled):
        pedest = {}
        pedest["service_resource_id"] = service_resource_id
        pedest["subresource_target"] = subresource_target
        pedest["spark_jobs_enabled"] = spark_jobs_enabled
        return pedest

    def service_tag_dest2dict(self, service_tag, protocol, port_ranges):
        service_tag_dest = {}
        service_tag_dest["service_tag"] = service_tag
        service_tag_dest["protocol"] = protocol
        service_tag_dest["port_ranges"] = port_ranges
        return service_tag_dest


class ManagedNetworkSchema(metaclass=PatchedSchemaMeta):
    isolation_mode = fields.Str(required=True)
    outbound_rules = fields.Dict(
        keys=fields.Str(required=True), values=NestedField(OutboundRuleSchema, allow_none=False), allow_none=True
    )
    network_id = fields.Str(required=False)

    @post_load
    def make(self, data, **kwargs):
        if data.get("outbound_rules", False):
            return ManagedNetwork(data["isolation_mode"], data["outbound_rules"], data["network_id"])
        else:
            return ManagedNetwork(data["isolation_mode"])
