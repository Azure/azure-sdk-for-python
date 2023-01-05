# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from marshmallow import fields, post_load

from azure.ai.ml._schema.core.fields import NestedField
from azure.ai.ml._schema.core.schema_meta import PatchedSchemaMeta
from azure.ai.ml.entities._workspace.networking import ManagedNetwork, OutboundRule


class OutboundRuleSchema(metaclass=PatchedSchemaMeta):
    direction: fields.Str(required=False)
    type: fields.Str(required=False)
    destination: fields.Str(required=False)

    @post_load
    def make(self, data, **kwargs):
        return OutboundRule(data)


class ManagedNetworkSchema(metaclass=PatchedSchemaMeta):
    managed_network_isolation: fields.Str(required=False)
    outbound_rule: fields.Dict(
        keys=fields.Str(required=True), values=NestedField(OutboundRuleSchema, allow_none=True), allow_none=True
    )

    @post_load
    def make(self, data, **kwargs):
        return ManagedNetwork(data)
