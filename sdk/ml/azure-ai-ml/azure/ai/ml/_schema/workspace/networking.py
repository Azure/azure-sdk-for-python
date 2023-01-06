# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields
from marshmallow.decorators import post_load, pre_dump, pre_load, post_dump

from azure.ai.ml._schema.core.fields import NestedField, StringTransformedEnum
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml._utils.utils import camel_to_snake, snake_to_camel
from azure.ai.ml.entities._workspace.networking import ManagedNetwork, OutboundRule, FqdnDestination, ServiceTagDestination, PrivateEndpointDestination, OutboundRuleType


class DestinationSchema(metaclass=PatchedSchemaMeta):
    service_resource_id = fields.Str()
    subresource_target = fields.Str()
    spark_jobs_enabled = fields.Bool()
    service_tag = fields.Str()
    protocol = fields.Str()
    port_ranges = fields.Str()



class OutboundRuleSchema(metaclass=PatchedSchemaMeta):
    type = fields.Str(required=False)
    # category = fields.Str(required=False)
    # destination = NestedField(DestinationSchema)
    """destination = fields.Dict(
        keys=fields.Str(required=True), values=fields.Raw(required=True), allow_none=True
    )"""
    destination = fields.Raw(required=True)

    """@pre_dump
    def predump(self, data, **kwargs):
        if data and isinstance(data, FqdnDestination):
            data.destination = data.destination
        if data and isinstance(data, PrivateEndpointDestination):
            data.destination = {}
            data.destination["service_resource_id"] = data.service_resource_id
            data.destination["subresource_target"] = data.subresource_target
            data.destination["spark_jobs_enabled"] = data.spark_jobs_enabled
        if data and isinstance(data, ServiceTagDestination):
            data.destination = {}
            data.destination["service_tag"] = data.service_tag
            data.destination["protocol"] = data.protocol
            data.destination["port_ranges"] = data.port_ranges
        return data
    """

    @pre_dump
    def predump(self, data, **kwargs):
        if data and isinstance(data, FqdnDestination):
            data.destination = self.fqdndest2dict(
                data.destination
            )
        if data and isinstance(data, PrivateEndpointDestination):
            data.destination = self.pedest2dict(
                data.service_resource_id,
                data.subresource_target,
                data.spark_jobs_enabled
            )
        if data and isinstance(data, ServiceTagDestination):
            data.destination = self.servicetagdest2dict(
                data.service_tag,
                data.protocol,
                data.port_ranges
            )
        return data

    """
    @post_dump
    def postdump(self, data, **kwargs):
        print("\n\nIN POST DUMP FUNCTION\n\n")
        print("data: ", data)
        desttype = data["type"]
        print("desttype: ", desttype)
        restore_data = {"type": data["type"]}
        if desttype==OutboundRuleType.fqdn:
            restore_data["destination"] = data["destination"]
        if desttype==OutboundRuleType.private_endpoint:
            restore_data["service_resource_id"] = data["destination"]["service_resource_id"]
            restore_data["subresource_target"] = data["destination"]["subresource_target"]
            restore_data["spark_jobs_enabled"] = data["destination"]["spark_jobs_enabled"]
        if desttype==OutboundRuleType.service_tag:
            restore_data["service_tag"] = data["destination"]["service_tag"]
            restore_data["protocol"] = data["destination"]["protocol"]
            restore_data["port_ranges"] = data["destination"]["port_ranges"]
        return restore_data

    @post_dump
    def postdump(self, data, **kwargs):
        print("\n\nIN POST DUMP FUNCTION\n\n")
        print("data: ", data)
        if desttype==OutboundRuleType.fqdn:
            print("REACHED HERE")
            return FqdnDestination(data["destination"])
        if desttype==OutboundRuleType.private_endpoint:
            return PrivateEndpointDestination(data["service_resource_id"], data["subresource_target"], data["spark_jobs_enabled"])
        if desttype==OutboundRuleType.service_tag:
            return ServiceTagDestination(data["service_tag"], data["protocol"], data["port_ranges"])
        return OutboundRule(data)
    
    @post_dump
    def postdump(self, data, **kwargs):
        if not isinstance(data.get("destination", False), str):
            data = data.pop("destination")
        return data
    """

    @post_load
    def createdestobject(self, data, **kwargs):
        dest = data.get("destination", False)
        if dest:
            if isinstance(dest, str):
                return FqdnDestination(dest)
            else:
                if dest.get("subresource_target", False):
                    return PrivateEndpointDestination(dest["service_resource_id"], dest["subresource_target"], dest["spark_jobs_enabled"])
                if dest.get("service_tag", False):
                    return ServiceTagDestination(dest["service_tag"], dest["protocol"], dest["port_ranges"])
        return OutboundRule(data)

    def fqdndest2dict(self, fqdndest):
        res = fqdndest
        return res

    def pedest2dict(self, service_resource_id, subresource_target, spark_jobs_enabled):
        pedest = {}
        pedest["service_resource_id"] = service_resource_id
        pedest["subresource_target"] = subresource_target
        pedest["spark_jobs_enabled"] = spark_jobs_enabled
        return pedest

    def servicetagdest2dict(self, service_tag, protocol, port_ranges):
        servicetagdest = {}
        servicetagdest["service_tag"] = service_tag
        servicetagdest["protocol"] = protocol
        servicetagdest["port_ranges"] = port_ranges
        return servicetagdest

    """
    @post_load
    def lowerstrip_email(self, item, many, **kwargs):
        item['email'] = item['email'].lower().strip()
        return item

    @pre_load(pass_many=True)
    def remove_envelope(self, data, many, **kwargs):
        namespace = 'results' if many else 'result'
        return data[namespace]

    @post_dump(pass_many=True)
    def add_envelope(self, data, many, **kwargs):
        namespace = 'results' if many else 'result'
        return {namespace: data}
    """



class ManagedNetworkSchema(metaclass=PatchedSchemaMeta):
    isolation_mode = fields.Str(required=True)
    outbound_rules = fields.Dict(
        keys=fields.Str(required=True), values=NestedField(OutboundRuleSchema, allow_none=False), allow_none=True
    )

    @post_load
    def make(self, data, **kwargs):
        return ManagedNetwork(data["isolation_mode"], data["outbound_rules"])
